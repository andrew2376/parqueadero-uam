import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EstadoBarrera } from '../../core/models';

@Component({
  selector: 'app-barrera-indicador',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './barrera-indicador.html',
  styleUrls: ['./barrera-indicador.css']
})
export class BarreraIndicadorComponent {
  @Input() estado: EstadoBarrera = 'CERRADA';
  @Input() mensaje: string = 'ESPERANDO VEHÍCULO';
  @Input() subtitulo?: string;

  get esAbierta(): boolean {
    return this.estado === 'ABIERTA';
  }
}
