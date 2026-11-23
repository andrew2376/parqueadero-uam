import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of, throwError } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { CredencialesLogin, RespuestaLogin, UsuarioSesion } from '../models/sesion.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly apiUrl = 'http://localhost:8001/api/v1/auth';
  private readonly storageKey = 'parqueadero_uam_sesion';

  private usuarioActualSubject = new BehaviorSubject<UsuarioSesion | null>(this.cargarSesionAlmacenada());
  public usuarioActual$ = this.usuarioActualSubject.asObservable();

  constructor(private http: HttpClient) {}

  public get usuarioActual(): UsuarioSesion | null {
    return this.usuarioActualSubject.value;
  }

  public estaAutenticado(): boolean {
    return !!this.usuarioActualSubject.value;
  }

  public obtenerToken(): string | null {
    return this.usuarioActualSubject.value?.token ?? null;
  }

  public tieneRol(rolRequerido: string): boolean {
    const usuario = this.usuarioActualSubject.value;
    if (!usuario) return false;
    return usuario.rol === rolRequerido;
  }

  public login(credenciales: CredencialesLogin): Observable<UsuarioSesion> {
    return this.http.post<RespuestaLogin>(`${this.apiUrl}/login`, credenciales).pipe(
      map(res => {
        const usuario: UsuarioSesion = {
          ...res.usuario,
          token: res.token
        };
        this.guardarSesion(usuario);
        return usuario;
      }),
      catchError(error => {
        // Fallback demo para desarrollo ágil / pruebas locales (S115 Frontend)
        if (error.status === 0 || error.status === 404) {
          const usuarioMock = this.autenticarDemo(credenciales);
          if (usuarioMock) {
            this.guardarSesion(usuarioMock);
            return of(usuarioMock);
          }
        }
        return throwError(() => error);
      })
    );
  }

  public logout(): void {
    localStorage.removeItem(this.storageKey);
    this.usuarioActualSubject.next(null);
  }

  private guardarSesion(usuario: UsuarioSesion): void {
    localStorage.setItem(this.storageKey, JSON.stringify(usuario));
    this.usuarioActualSubject.next(usuario);
  }

  private cargarSesionAlmacenada(): UsuarioSesion | null {
    try {
      const data = localStorage.getItem(this.storageKey);
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  }

  private autenticarDemo(credenciales: CredencialesLogin): UsuarioSesion | null {
    const usr = credenciales.username.trim().toLowerCase();
    const pwd = credenciales.password;

    if (usr === 'admin' && pwd === 'admin123') {
      return {
        id: 'usr-admin-demo',
        username: 'admin',
        nombreCompleto: 'Administrador UAM',
        rol: 'ADMINISTRADOR',
        token: 'demo-jwt-token-admin'
      };
    }

    if ((usr === 'operador' || usr === 'operador1') && pwd === 'operador123') {
      return {
        id: 'usr-operador-demo',
        username: 'operador',
        nombreCompleto: 'Operador de Turno',
        rol: 'OPERADOR',
        token: 'demo-jwt-token-operador'
      };
    }

    return null;
  }
}
