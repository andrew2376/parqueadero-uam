import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { map } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return authService.validarSesion().pipe(
    map(autenticado => {
      if (!autenticado) {
        return router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
      }

      const rolRequerido = route.data['rol'];
      return !rolRequerido || authService.tieneRol(rolRequerido)
        ? true
        : router.createUrlTree(['/panel']);
    })
  );
};
