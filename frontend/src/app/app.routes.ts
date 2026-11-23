import { Routes } from '@angular/router';
import { PanelComponent } from './features/panel/panel';
import { LoginComponent } from './features/auth/login/login';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: '', redirectTo: 'panel', pathMatch: 'full' },
  { path: 'panel', component: PanelComponent, canActivate: [authGuard] },
  {
    path: 'carriles',
    loadComponent: () =>
      import('./funcionalidades/carriles/paginas/gestion-carriles/gestion-carriles')
        .then(m => m.GestionCarriles),
    canActivate: [authGuard]
  },
  { path: '**', redirectTo: 'panel' }
];
