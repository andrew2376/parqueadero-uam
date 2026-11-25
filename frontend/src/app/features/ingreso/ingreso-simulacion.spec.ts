import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { API_BASE_URL } from '../../core/api.config';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { LecturaSimulada } from '../../core/services/ingreso.service';
import { ControlIngresoComponent } from './ingreso';

describe('Camaras LPR del carril mixto', () => {
  let fixture: ComponentFixture<ControlIngresoComponent>;
  let http: HttpTestingController;
  const carril = '12345678-1234-1234-1234-123456789abc';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ControlIngresoComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: ActivatedRoute, useValue: { snapshot: { queryParamMap: convertToParamMap({ carril }) } } },
        { provide: AuthService, useValue: { usuarioActual: { id: 'operador', rol: 'OPERADOR' } } }
      ]
    });
    fixture = TestBed.createComponent(ControlIngresoComponent);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(`${API_BASE_URL}/carriles/${carril}`).flush({
      id: carril, sede_id: 'sede', activo: true, tipo: 'MIXTO', nombre: 'Mixto'
    });
    const sedes = http.expectOne(req => req.url === `${API_BASE_URL}/lecturas-lpr/carriles-activos`);
    expect(sedes.request.params.get('sede_id')).toBe('sede');
    sedes.flush([{ id: carril, sede_id: 'sede', nombre: 'Mixto', nombre_sede: 'Sede demo', tipo: 'MIXTO' }]);
    fixture.detectChanges();
  });

  afterEach(() => http.verify());

  function capturar(escenario: string) {
    const selector: HTMLSelectElement = fixture.nativeElement.querySelector('#escenario-lpr');
    selector.value = escenario;
    selector.dispatchEvent(new Event('change'));
    fixture.nativeElement.querySelector('.btn-simulate').click();
    const solicitud = http.expectOne(req => req.url === `${API_BASE_URL}/lecturas-lpr/simulacion`);
    expect(solicitud.request.method).toBe('POST');
    expect(solicitud.request.params.get('escenario')).toBe(escenario);
    expect(solicitud.request.params.get('carril_id')).toBe(carril);
    return solicitud;
  }

  const casos: Array<[string, Omit<LecturaSimulada, 'id' | 'direccion'>, string]> = [
    ['alta', { placa: 'ABC123', tipo_vehiculo: 'CARRO', estado: 'EXITOSA',
      confianza: 95, requiere_confirmacion_manual: false }, 'Automóvil'],
    ['baja', { placa: 'DEF45A', tipo_vehiculo: 'MOTO', estado: 'BAJA_CONFIANZA',
      confianza: 55, requiere_confirmacion_manual: true }, 'Motocicleta'],
    ['sin-lectura', { placa: null, tipo_vehiculo: null, estado: 'FALLIDA',
      confianza: 0, requiere_confirmacion_manual: true }, '']
  ];

  it.each(casos)('muestra la captura %s sin solicitar un ingreso', (escenario, lectura, tipo) => {
    capturar(escenario).flush({ id: 'evento', direccion: 'ENTRADA', ...lectura });
    fixture.detectChanges();
    const componente = fixture.componentInstance;
    expect(componente.ingresoForm.get('placa')?.value).toBe(lectura.placa ?? '');
    expect(componente.ingresoForm.get('tipoVehiculoTexto')?.value).toBe(tipo);
    expect(componente.lectura?.confianza).toBe(lectura.confianza);
    expect(componente.lectura?.requiere_confirmacion_manual).toBe(lectura.requiere_confirmacion_manual);
    expect(componente.resultadoIngreso).toBeNull();
    if (lectura.placa === null) {
      expect(fixture.nativeElement.querySelector('.status-banner').textContent).toContain('Sin lectura');
    }
    http.expectNone(req => req.url.endsWith('/accesos/ingreso'));
  });

  it('descarta la lectura anterior y presenta el fallo sin autorizar un ingreso', () => {
    capturar('alta').flush({ id: 'evento', direccion: 'ENTRADA', ...casos[0][1] });
    capturar('alta').flush(null, { status: 503, statusText: 'Service Unavailable' });
    fixture.componentInstance.onRegistrarIngreso();
    fixture.detectChanges();
    expect(fixture.componentInstance.lectura).toBeNull()
    expect(fixture.componentInstance.resultadoIngreso).toBeNull();
    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain('servidor');
    http.expectNone(req => req.url.endsWith('/accesos/ingreso'));
  });

  it('mantiene cerrada la barrera si falla un ingreso solicitado tras la captura', () => {
    capturar('alta').flush({ id: 'evento', direccion: 'ENTRADA', ...casos[0][1] });
    fixture.componentInstance.onRegistrarIngreso();
    http.expectOne(`${API_BASE_URL}/accesos/ingreso`).flush(null, {
      status: 503, statusText: 'Service Unavailable'
    });
    fixture.detectChanges();
    expect(fixture.componentInstance.resultadoIngreso).toBeNull();
    expect(fixture.nativeElement.querySelector('.barrier-result-box').textContent).toContain('BARRERA CERRADA');
  });
  it('envia a salida la placa corregida en el formulario y confirmada por FastAPI', () => {
    fixture.componentInstance.seleccionarCamara('SALIDA');
    const captura = capturar('baja');
    expect(captura.request.params.get('direccion')).toBe('SALIDA');
    captura.flush({ id: 'evento', direccion: 'SALIDA', ...casos[1][1] });
    fixture.detectChanges();
    const placa: HTMLInputElement = fixture.nativeElement.querySelector('#placa');
    placa.value = 'def-454';
    placa.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    const registrar: HTMLButtonElement = fixture.nativeElement.querySelector('.btn-register');
    expect(registrar.textContent).toContain('Registrar salida');
    expect(registrar.disabled).toBe(false);
    http.expectNone(`${API_BASE_URL}/estancias/salida`);
    registrar.click();
    http.expectOne(`${API_BASE_URL}/carriles/${carril}`).flush({
      id: carril, sede_id: 'sede', activo: true, tipo: 'MIXTO', nombre: 'Mixto'
    });
    const manual = http.expectOne(`${API_BASE_URL}/lecturas-lpr/manual`);
    expect(manual.request.body).toEqual({ carril_id: carril, placa: 'def-454' });
    http.expectNone(`${API_BASE_URL}/estancias/salida`);
    manual.flush({ placa: 'DEF454', estado: 'EXITOSA' });
    const salida = http.expectOne(`${API_BASE_URL}/estancias/salida`);
    expect(salida.request.body).toEqual({ sede_id: 'sede', placa: 'DEF454' });
    salida.flush({ autorizado: false, decision_barrera: 'DENEGAR', motivo: 'Pago pendiente' });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.result-card').textContent).toContain('Pago pendiente');
    expect(fixture.nativeElement.querySelector('.result-card').textContent).toContain('BARRERA CERRADA');
  });
  it('habilita la digitacion con el carril validado y detiene el ingreso si falla la confirmacion', () => {
    expect(fixture.componentInstance.carril?.id).toBe(carril);
    expect(fixture.nativeElement.querySelector('#estado-carril').textContent).toContain('activo y verificado');
    const placa: HTMLInputElement = fixture.nativeElement.querySelector('#placa');
    expect(placa.readOnly).toBe(false);
    placa.value = 'abc-123';
    placa.dispatchEvent(new Event('input'));
    fixture.componentInstance.onRegistrarIngreso();
    const manual = http.expectOne(`${API_BASE_URL}/lecturas-lpr/manual`);
    expect(manual.request.body).toEqual({ carril_id: carril, placa: 'abc-123' });
    manual.flush({ detail: 'Placa invalida' }, { status: 422, statusText: 'Unprocessable Content' });
    http.expectNone(`${API_BASE_URL}/accesos/ingreso`);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain('Placa invalida');
    expect(fixture.nativeElement.querySelector('.barrier-result-box').textContent).toContain('BARRERA CERRADA');
  });

  it('informa cuando el carril no existe y bloquea los controles de captura', () => {
    fixture.componentInstance.cargarCarril(carril);
    http.expectOne(`${API_BASE_URL}/carriles/${carril}`).flush(
      null, { status: 404, statusText: 'Not Found' }
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('#estado-carril').textContent).toContain('no existe');
    expect(fixture.nativeElement.querySelector('.btn-simulate').disabled).toBe(true);
    expect(fixture.nativeElement.querySelector('#placa').readOnly).toBe(true);
  });
  it('envia la placa opcional y la omite en el escenario sin lectura', () => {
    fixture.componentInstance.placaSimulada.setValue(' xyz-789 ');
    const alta = capturar('alta');
    expect(alta.request.params.get('placa')).toBe('xyz-789');
    alta.flush({ id: 'evento', direccion: 'ENTRADA', ...casos[0][1], placa: 'XYZ789' });
    expect(fixture.componentInstance.ingresoForm.controls.placa.value).toBe('XYZ789');
    const sinLectura = capturar('sin-lectura');
    expect(sinLectura.request.params.has('placa')).toBe(false);
    sinLectura.flush({ id: 'evento', direccion: 'ENTRADA', ...casos[2][1] });
  });
  it('mantiene el escenario y la confianza de la captura al cambiar los ajustes', () => {
    fixture.componentInstance.placaSimulada.setValue('ABC123');
    const captura = capturar('alta');
    const selector: HTMLSelectElement = fixture.nativeElement.querySelector('#escenario-lpr');
    selector.value = 'baja';
    selector.dispatchEvent(new Event('change'));
    captura.flush({ id: 'evento', direccion: 'ENTRADA', ...casos[0][1] });
    fixture.detectChanges();
    const revision = fixture.nativeElement.querySelector('#revision-titulo').parentElement;
    expect(revision.textContent).toContain('Confianza alta');
    expect(revision.textContent).toContain('95 %');
    expect(revision.textContent).toContain('sigue siendo la anterior');
    expect(revision.textContent).not.toContain('Confianza baja');

    selector.value = 'alta';
    selector.dispatchEvent(new Event('change'));
    const placa: HTMLInputElement = fixture.nativeElement.querySelector('#placa-simulada');
    placa.value = 'XYZ789';
    placa.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    expect(revision.textContent).toContain('sigue siendo la anterior');
    expect(revision.textContent).toContain('ABC123');
    http.expectNone(`${API_BASE_URL}/accesos/ingreso`);
  });

  it('limpia la lectura al cambiar de direccion y conserva sede y carril', () => {
    capturar('alta').flush({ id: 'evento', direccion: 'ENTRADA', ...casos[0][1] });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('#estado-carril').textContent).toContain('Sede demo');
    const botones = fixture.nativeElement.querySelectorAll('.camera-switch button');
    botones[1].click();
    fixture.detectChanges();
    expect(botones[1].getAttribute('aria-pressed')).toBe('true');
    expect(fixture.componentInstance.carril?.id).toBe(carril);
    expect(fixture.nativeElement.querySelector('#placa').value).toBe('');
    expect(fixture.nativeElement.querySelector('.status-banner').textContent).not.toContain('ABC123');
    expect(fixture.nativeElement.querySelector('.btn-register').disabled).toBe(true);
    expect(fixture.nativeElement.querySelector('.camera-active').textContent).toContain('Salida');
    expect(fixture.nativeElement.querySelector('#estado-carril').textContent).toContain('Sede demo');
    http.expectNone(`${API_BASE_URL}/estancias/salida`);
  });

  it.each([
    { sede_id: 'sede', activo: false, tipo: 'MIXTO' },
    { sede_id: 'otra', activo: true, tipo: 'SALIDA' },
    { sede_id: 'sede', activo: true, tipo: 'ENTRADA' }
  ])('bloquea la salida si cambio la configuracion del carril', datos => {
    fixture.componentInstance.seleccionarCamara('SALIDA');
    fixture.componentInstance.ingresoForm.controls.placa.setValue('DEF454');
    fixture.componentInstance.onRegistrarIngreso();
    http.expectOne(`${API_BASE_URL}/carriles/${carril}`).flush({ id: carril, ...datos });
    http.expectNone(`${API_BASE_URL}/lecturas-lpr/manual`);
    http.expectNone(`${API_BASE_URL}/estancias/salida`);
    expect(fixture.componentInstance.resultadoIngreso).toBeNull();
  });

});

describe('Seleccion de carril sin UUID en el formulario', () => {
  const primero = { id: 'c1', sede_id: 's1', nombre: 'Principal', nombre_sede: 'Sede Norte', tipo: 'ENTRADA' };
  const segundo = { id: 'c2', sede_id: 's2', nombre: 'Principal', nombre_sede: 'Sede Sur', tipo: 'SALIDA' };

  function montar(sede?: string) {
    TestBed.configureTestingModule({
      imports: [ControlIngresoComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: ActivatedRoute, useValue: { snapshot: { queryParamMap: convertToParamMap(sede ? { sede } : {}) } } },
        { provide: AuthService, useValue: { usuarioActual: { id: 'operador', rol: 'OPERADOR' } } }
      ]
    });
    const fixture = TestBed.createComponent(ControlIngresoComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    const catalogo = http.expectOne(req => req.url === `${API_BASE_URL}/lecturas-lpr/carriles-activos`);
    return { fixture, http, catalogo };
  }

  it('carga automaticamente el unico carril para la sede indicada', () => {
    const { fixture, http, catalogo } = montar('s1');
    expect(catalogo.request.params.get('sede_id')).toBe('s1');
    catalogo.flush([primero]);
    fixture.detectChanges();
    expect(fixture.componentInstance.carril?.id).toBe(primero.id);
    expect(fixture.nativeElement.querySelector('#carril-lpr')).toBeNull();
    expect(fixture.nativeElement.querySelector('.btn-simulate').disabled).toBe(false);
    const botones = fixture.nativeElement.querySelectorAll('.camera-switch button');
    expect(botones.length).toBe(1);
    expect(botones[0].textContent.trim()).toBe('Entrada');
    expect(fixture.nativeElement.querySelector('.btn-register').textContent).toContain('Registrar ingreso');
    http.verify();
  });

  it('espera una seleccion por nombre cuando hay varios carriles', () => {
    const { fixture, http, catalogo } = montar();
    expect(catalogo.request.params.has('sede_id')).toBe(false);
    catalogo.flush([primero, segundo]);
    fixture.detectChanges();
    const selector: HTMLSelectElement = fixture.nativeElement.querySelector('#carril-lpr');
    expect(selector.options[1].text).toContain('Sede Norte');
    expect(selector.options[2].text).toContain('Sede Sur');
    expect(fixture.componentInstance.carril).toBeNull();
    selector.value = segundo.id;
    selector.dispatchEvent(new Event('change'));
    http.expectOne(`${API_BASE_URL}/carriles/${segundo.id}`).flush({
      ...segundo, activo: true
    });
    fixture.detectChanges();
    expect(fixture.componentInstance.carril?.sede_id).toBe(segundo.sede_id);
    expect(fixture.componentInstance.direccion).toBe('SALIDA');
    const botones = fixture.nativeElement.querySelectorAll('.camera-switch button');
    expect(botones.length).toBe(1);
    expect(botones[0].textContent.trim()).toBe('Salida');
    expect(fixture.nativeElement.querySelector('.btn-register').textContent).toContain('Registrar salida');
    http.verify();
  });
});
