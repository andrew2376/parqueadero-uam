import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, catchError, defer, map, of, share } from 'rxjs';
import { AUTH_LOGIN_URL, AUTH_PERFIL_URL } from '../api.config';
import { CredencialesLogin, RespuestaLogin, UsuarioSesion } from '../models/sesion.model';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly storageKey = 'parqueadero_uam_sesion';
  private readonly usuarioActualSubject = new BehaviorSubject<UsuarioSesion | null>(null);
  readonly usuarioActual$ = this.usuarioActualSubject.asObservable();
  private versionSesion = 0;

  private readonly restauracion$ = defer(() => {
    const token = this.leerTokenAlmacenado();
    if (!token) return of(false);

    const version = this.versionSesion;
    return this.http.get<Omit<UsuarioSesion, 'token'>>(AUTH_PERFIL_URL, {
      headers: { Authorization: `Bearer ${token}` },
      timeout: 10_000
    }).pipe(
      map(perfil => {
        if (version === this.versionSesion) {
          this.guardarSesion({ ...perfil, token });
        }
        return this.estaAutenticado();
      }),
      catchError((error: HttpErrorResponse) => {
        if (version === this.versionSesion && error.status === 401) {
          this.logout();
        }
        return of(this.estaAutenticado());
      })
    );
  }).pipe(share());

  constructor(private readonly http: HttpClient) {}

  get usuarioActual(): UsuarioSesion | null {
    return this.usuarioActualSubject.value;
  }

  estaAutenticado(): boolean {
    return this.usuarioActual !== null;
  }

  validarSesion(): Observable<boolean> {
    return defer(() => this.estaAutenticado() ? of(true) : this.restauracion$);
  }

  tieneRol(rolRequerido: string): boolean {
    const rol = this.usuarioActual?.rol;
    return rol === 'ADMINISTRADOR' || rol === rolRequerido;
  }

  login(credenciales: CredencialesLogin): Observable<UsuarioSesion> {
    return this.http.post<RespuestaLogin>(AUTH_LOGIN_URL, credenciales, { timeout: 10_000 }).pipe(
      map(({ usuario, token }) => {
        const sesion = { ...usuario, token };
        this.guardarSesion(sesion);
        return sesion;
      })
    );
  }

  logout(): void {
    this.versionSesion++;
    localStorage.removeItem(this.storageKey);
    this.usuarioActualSubject.next(null);
  }

  private guardarSesion(usuario: UsuarioSesion): void {
    this.versionSesion++;
    localStorage.setItem(this.storageKey, JSON.stringify(usuario));
    this.usuarioActualSubject.next(usuario);
  }

  private leerTokenAlmacenado(): string | null {
    try {
      const sesion = JSON.parse(localStorage.getItem(this.storageKey) ?? 'null');
      return typeof sesion?.token === 'string' && sesion.token.trim() ? sesion.token : null;
    } catch {
      return null;
    }
  }
}
