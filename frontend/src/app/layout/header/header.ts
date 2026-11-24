import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './header.html',
  styleUrls: ['./header.css']
})
export class HeaderComponent {
  @Input() titulo: string = 'Panel general';
  @Input() subtitulo: string = 'Resumen operativo · Sede principal';

  constructor(
    public authService: AuthService,
    private router: Router
  ) {}

  get nombreUsuario(): string {
    return this.authService.usuarioActual?.nombreCompleto || 'Operador UAM';
  }

  get rolUsuario(): string {
    return this.authService.usuarioActual?.rol || 'OPERADOR';
  }

  cerrarSesion(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
