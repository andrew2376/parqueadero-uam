import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { RolUsuario } from '../../core/models';

export interface MenuItem {
  label: string;
  route: string;
  icon: string;
  rolMinimo?: RolUsuario;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.html',
  styleUrls: ['./sidebar.css']
})
export class SidebarComponent {
  todosLosItems: MenuItem[] = [
    { label: 'Panel general', route: '/panel', icon: 'dashboard' },
    { label: 'Control de ingreso', route: '/ingreso', icon: 'login' },
    { label: 'Control de salida', route: '/salida', icon: 'logout' },
    { label: 'Caja y pagos', route: '/caja', icon: 'payments' },
    { label: 'Administración de carriles', route: '/carriles', icon: 'alt_route', rolMinimo: 'ADMINISTRADOR' },
    { label: 'Gestión de tarifas', route: '/tarifas', icon: 'tune', rolMinimo: 'ADMINISTRADOR' },
  { label: 'Administración de cupos', route: '/cupos', icon: 'garage', rolMinimo: 'ADMINISTRADOR' },
    { label: 'Historial', route: '/historial', icon: 'history' },
  ];

  constructor(private authService: AuthService) {}

  get menuItems(): MenuItem[] {
    return this.todosLosItems.filter(item => {
      if (!item.rolMinimo) return true;
      return this.authService.tieneRol(item.rolMinimo);
    });
  }
}
