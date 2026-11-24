
import { Routes } from '@angular/router';
import { PanelComponent } from './features/panel/panel';
import { LoginComponent } from './features/auth/login/login';
import { ControlIngresoComponent } from './features/ingreso/ingreso';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: '', redirectTo: 'panel', pathMatch: 'full' },
  {
    path: 'panel',
    component: PanelComponent,
    canActivate: [authGuard]
  },
  {
    path: 'ingreso',
    component: ControlIngresoComponent,
    canActivate: [authGuard]
  },
  {
    path: 'carriles',
    loadComponent: () =>
      import('./funcionalidades/carriles/paginas/gestion-carriles/gestion-carriles')
        .then(m => m.GestionCarriles),
    canActivate: [authGuard],
    data: { rol: 'ADMINISTRADOR' }
  },
  {
    path: 'tarifas',
    loadComponent: () =>
      import('./funcionalidades/tarifas/paginas/gestion-tarifas/gestion-tarifas')
        .then(m => m.GestionTarifas),
    canActivate: [authGuard],
    data: { rol: 'ADMINISTRADOR' }
  },
  { path: '**', redirectTo: 'panel' }
];
