
import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'carriles',
    loadComponent: () =>
      import('./funcionalidades/carriles/paginas/gestion-carriles/gestion-carriles')
        .then(m => m.GestionCarriles)
  },
  {
    path: '',
    redirectTo: 'carriles',
    pathMatch: 'full'
  },
  {
    path: '**',
    redirectTo: 'carriles'
  }
];
