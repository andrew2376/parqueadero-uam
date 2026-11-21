import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

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
  @Input() usuario: string = 'Operador UAM';
  @Input() rol: string = 'Operador';
}
