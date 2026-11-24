import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { DOCUMENT, inject } from '@angular/core';
import { Router } from '@angular/router';
import { tap } from 'rxjs';
import { API_BASE_URL, AUTH_LOGIN_URL } from '../api.config';
import { AuthService } from '../services/auth.service';

const api = new URL(API_BASE_URL);
const loginPath = new URL(AUTH_LOGIN_URL).pathname;

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const url = new URL(req.url, inject(DOCUMENT).baseURI);
  if (url.origin !== api.origin || !url.pathname.startsWith(`${api.pathname}/`) ||
      url.pathname === loginPath) {
    return next(req);
  }

  const authService = inject(AuthService);
  const sesion = authService.usuarioActual;
  if (!sesion?.token) {
    return next(req);
  }

  const router = inject(Router);
  return next(req.clone({
    setHeaders: { Authorization: `Bearer ${sesion.token}` }
  })).pipe(
    tap({
      error: (error: unknown) => {
        if (error instanceof HttpErrorResponse && error.status === 401 &&
            authService.usuarioActual === sesion) {
          authService.logout();
          void router.navigate(['/login'], { queryParams: { returnUrl: router.url } });
        }
      }
    })
  );
};
