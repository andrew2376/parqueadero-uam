import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.estaAutenticado()) {
    // Si la ruta requiere un rol específico
    const rolRequerido = route.data?.['rol'];
    if (rolRequerido && !authService.tieneRol(rolRequerido)) {
      router.navigate(['/panel']);
      return false;
    }
    return true;
  }

  // Redirigir a login preservando la ruta que intentaba acceder
  router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
  return false;
};
