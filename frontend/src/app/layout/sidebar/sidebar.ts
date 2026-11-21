import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.html',
  styleUrls: ['./sidebar.css']
})
export class SidebarComponent {
  menuItems = [
    { label: 'Panel general', route: '/panel', icon: 'dashboard' },
    { label: 'Administración de carriles', route: '/carriles', icon: 'alt_route' },
    { label: 'Control de ingreso', route: '/ingreso', icon: 'login' },
    { label: 'Control de salida', route: '/salida', icon: 'logout' },
    { label: 'Caja y pagos', route: '/caja', icon: 'payments' },
    { label: 'Gestión de tarifas', route: '/tarifas', icon: 'tune' },
    { label: 'Cupos y sedes', route: '/cupos', icon: 'garage' },
    { label: 'Historial', route: '/historial', icon: 'history' },
  ];
}
