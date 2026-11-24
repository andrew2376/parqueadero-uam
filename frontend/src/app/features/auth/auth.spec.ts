import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';
import { firstValueFrom } from 'rxjs';
import { vi } from 'vitest';
import { routes } from '../../app.routes';
import { API_BASE_URL, AUTH_LOGIN_URL, AUTH_PERFIL_URL } from '../../core/api.config';
import { authInterceptor } from '../../core/interceptors/auth.interceptor';
import { UsuarioSesion } from '../../core/models/sesion.model';
import { AuthService } from '../../core/services/auth.service';

@Component({ template: '' })
class PaginaProtegida {}

const storageKey = 'parqueadero_uam_sesion';
const token = 'jwt-de-prueba';
const operador: UsuarioSesion = {
  id: '00000000-0000-0000-0000-000000000001',
  username: 'operador1',
  nombreCompleto: 'Operador de Turno UAM',
  rol: 'OPERADOR'
};
const administrador: UsuarioSesion = {
  id: '00000000-0000-0000-0000-000000000002',
  username: 'admin',
  nombreCompleto: 'Administrador UAM',
  rol: 'ADMINISTRADOR'
};

describe('Autenticación y navegación', () => {
  let http: HttpTestingController;
  let auth: AuthService;
  let router: Router;
  let harness: RouterTestingHarness;

  beforeEach(async () => {
    localStorage.removeItem(storageKey);
    TestBed.configureTestingModule({
      providers: [
        provideRouter(routes.map(ruta => ruta.canActivate
          ? { ...ruta, component: PaginaProtegida, loadComponent: undefined }
          : ruta)),
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting()
      ]
    });
    http = TestBed.inject(HttpTestingController);
    auth = TestBed.inject(AuthService);
    router = TestBed.inject(Router);
    harness = await RouterTestingHarness.create();
  });

  afterEach(() => {
    http.verify();
    localStorage.removeItem(storageKey);
  });

  async function enviarFormulario(url = '/login') {
    await harness.navigateByUrl(url);
    const host = harness.routeNativeElement!;
    for (const [id, valor] of [['username', 'admin'], ['password', 'admin123']]) {
      const campo = host.querySelector<HTMLInputElement>(`#${id}`)!;
      campo.value = valor;
      campo.dispatchEvent(new Event('input'));
    }
    host.querySelector('form')!.dispatchEvent(new Event('submit', { cancelable: true }));
    return http.expectOne(AUTH_LOGIN_URL);
  }

  async function iniciarSesion(usuario: UsuarioSesion) {
    const resultado = firstValueFrom(auth.login({ username: usuario.username, password: 'prueba' }));
    const solicitud = http.expectOne(AUTH_LOGIN_URL);
    expect(solicitud.request.headers.has('Authorization')).toBe(false);
    solicitud.flush({ usuario, token, tipoToken: 'Bearer' });
    await resultado;
  }

  it('pide iniciar sesión al visitante y conserva el destino solicitado', async () => {
    await harness.navigateByUrl('/carriles');
    expect(router.parseUrl(router.url).queryParams['returnUrl']).toBe('/carriles');
    expect(harness.routeNativeElement?.querySelector('form')).not.toBeNull();
    http.expectNone(AUTH_PERFIL_URL);
  });

  it('distingue credenciales incorrectas de una conexión fallida y no crea una sesión ficticia', async () => {
    const solicitud = await enviarFormulario();
    solicitud.flush(null, { status: 401, statusText: 'Unauthorized' });
    harness.detectChanges();
    expect(harness.routeNativeElement?.textContent).toContain('Usuario o contraseña incorrectos.');

    const reintento = await enviarFormulario();
    reintento.error(new ProgressEvent('error'));
    harness.detectChanges();
    expect(harness.routeNativeElement?.textContent).toContain('No se pudo conectar con el servidor.');
    expect(auth.estaAutenticado()).toBe(false);
    expect(localStorage.getItem(storageKey)).toBeNull();
    expect(router.url).toBe('/login');
  });

  it('también rechaza el login si la ruta de la API devuelve 404', async () => {
    const solicitud = await enviarFormulario();
    solicitud.flush(null, { status: 404, statusText: 'Not Found' });
    expect(auth.estaAutenticado()).toBe(false);
    expect(localStorage.getItem(storageKey)).toBeNull();
    expect(router.url).toBe('/login');
  });

  it('vuelve a la ruta solicitada después de iniciar sesión correctamente', async () => {
    await harness.navigateByUrl('/ingreso');
    const solicitud = await enviarFormulario(router.url);
    solicitud.flush({ usuario: administrador, token, tipoToken: 'Bearer' });
    await harness.fixture.whenStable();
    expect(router.url).toBe('/ingreso');
    expect(auth.usuarioActual?.rol).toBe('ADMINISTRADOR');
  });

  it('comparte la validación pendiente y no restaura una sesión cerrada mientras esperaba', async () => {
    localStorage.setItem(storageKey, JSON.stringify({ token }));
    const primera = firstValueFrom(auth.validarSesion());
    const segunda = firstValueFrom(auth.validarSesion());
    const perfil = http.expectOne(AUTH_PERFIL_URL);

    auth.logout();
    perfil.flush(operador);
    expect(await Promise.all([primera, segunda])).toEqual([false, false]);
    expect(localStorage.getItem(storageKey)).toBeNull();
  });

  it('espera el perfil y usa el rol del servidor en lugar del rol almacenado', async () => {
    localStorage.setItem(storageKey, JSON.stringify({ ...administrador, token }));
    const navegacion = harness.navigateByUrl('/carriles');
    const perfil = await vi.waitFor(() => http.expectOne(AUTH_PERFIL_URL));
    expect(perfil.request.headers.get('Authorization')).toBe(`Bearer ${token}`);
    expect(auth.estaAutenticado()).toBe(false);
    expect(router.url).not.toBe('/carriles');

    perfil.flush(operador);
    await navegacion;
    expect(router.url).toBe('/panel');
    expect(auth.usuarioActual?.rol).toBe('OPERADOR');
    await harness.navigateByUrl('/ingreso');
    expect(router.url).toBe('/ingreso');
  });

  it('permite a un administrador entrar en carriles tras validar el perfil', async () => {
    localStorage.setItem(storageKey, JSON.stringify({ token }));
    const navegacion = harness.navigateByUrl('/carriles');
    const perfil = await vi.waitFor(() => http.expectOne(AUTH_PERFIL_URL));
    perfil.flush(administrador);
    await navegacion;
    expect(router.url).toBe('/carriles');

    await harness.navigateByUrl('/login');
    await harness.fixture.whenStable();
    expect(router.url).toBe('/panel');
  });

  it('elimina un token restaurado que el servidor rechaza y vuelve al login', async () => {
    localStorage.setItem(storageKey, JSON.stringify({ token }));
    const navegacion = harness.navigateByUrl('/panel');
    const perfil = await vi.waitFor(() => http.expectOne(AUTH_PERFIL_URL));
    perfil.flush(null, { status: 401, statusText: 'Unauthorized' });
    await navegacion;
    expect(router.parseUrl(router.url).queryParams['returnUrl']).toBe('/panel');
    expect(auth.estaAutenticado()).toBe(false);
    expect(localStorage.getItem(storageKey)).toBeNull();
  });

  it('deniega la navegación si el servidor no puede validar el perfil', async () => {
    localStorage.setItem(storageKey, JSON.stringify({ token }));
    const navegacion = harness.navigateByUrl('/panel');
    const perfil = await vi.waitFor(() => http.expectOne(AUTH_PERFIL_URL));
    perfil.error(new ProgressEvent('error'));
    await navegacion;
    expect(router.parseUrl(router.url).queryParams['returnUrl']).toBe('/panel');
    expect(auth.estaAutenticado()).toBe(false);
  });

  it('envía el Bearer solo al origen y prefijo de la API y cierra la sesión ante un 401 propio', async () => {
    await iniciarSesion(administrador);
    await harness.navigateByUrl('/carriles');
    const cliente = TestBed.inject(HttpClient);

    const urlsExternas = [
      'http://localhost:9000/api/v1/carriles',
      'https://externo.example/api/v1/carriles',
      'http://localhost:8001/api/v10/carriles'
    ];
    for (const url of urlsExternas) {
      cliente.get(url).subscribe({ error: () => {} });
      const solicitud = http.expectOne(url);
      expect(solicitud.request.headers.has('Authorization')).toBe(false);
      solicitud.flush(null, { status: 401, statusText: 'Unauthorized' });
    }
    expect(auth.estaAutenticado()).toBe(true);

    const url = `${API_BASE_URL}/carriles`;
    cliente.get(url).subscribe({ error: () => {} });
    const prohibida = http.expectOne(url);
    expect(prohibida.request.headers.get('Authorization')).toBe(`Bearer ${token}`);
    prohibida.flush(null, { status: 403, statusText: 'Forbidden' });
    expect(auth.estaAutenticado()).toBe(true);

    cliente.get(url).subscribe({ error: () => {} });
    http.expectOne(url).flush(null, { status: 401, statusText: 'Unauthorized' });
    await harness.fixture.whenStable();
    expect(router.parseUrl(router.url).queryParams['returnUrl']).toBe('/carriles');
    expect(harness.routeNativeElement?.querySelector('form')).not.toBeNull();
    expect(auth.estaAutenticado()).toBe(false);
    expect(localStorage.getItem(storageKey)).toBeNull();
  });
});
