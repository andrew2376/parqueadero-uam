import { Routes } from '@angular/router';
import { PanelComponent } from './features/panel/panel';

export const routes: Routes = [
  { path: '', redirectTo: 'panel', pathMatch: 'full' },
  { path: 'panel', component: PanelComponent },
  { path: '**', redirectTo: 'panel' }
];
