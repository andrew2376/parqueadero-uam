import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.obtenerToken();

  // Si hay token y la petición va dirigida a la API, adjuntamos Bearer token
  if (token && req.url.includes('/api/')) {
    const peticionClonada = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
    return next(peticionClonada);
  }

  return next(req);
};
