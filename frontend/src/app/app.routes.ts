import { Routes } from '@angular/router';
import { PanelComponent } from './features/panel/panel';

export const routes: Routes = [
  { path: '', redirectTo: 'panel', pathMatch: 'full' },
  { path: 'panel', component: PanelComponent },
  {
    path: 'carriles',
    loadComponent: () =>
      import('./funcionalidades/carriles/paginas/gestion-carriles/gestion-carriles')
        .then(m => m.GestionCarriles)
  },
  { path: '**', redirectTo: 'panel' }
];
