
import {
  Component,
  OnInit,
  inject,
  ChangeDetectorRef
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';

import { CupoService } from '../../servicios/cupo.service';

import {
  Cupo,
  ActualizarCupos
} from '../../modelos/cupo.model';

@Component({
  selector: 'app-gestion-cupos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './gestion-cupos.html',
  styleUrl: './gestion-cupos.css'
})
export class GestionCupos implements OnInit {

  private readonly cupoService = inject(CupoService);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly sedeId = '03793b27-4b34-42ea-9bb0-28f8bc5b330d';

  cupos: Cupo[] = [];

  formulario: ActualizarCupos = {
    cupos_carro: 0,
    cupos_moto: 0
  };

  cargando = false;
  guardando = false;
  error = '';
  mensaje = '';

  ngOnInit(): void {
    this.consultarCupos();
  }

  get cuposCarro(): Cupo | undefined {
    return this.cupos.find(
      cupo => cupo.tipo_vehiculo === 'CARRO'
    );
  }

  get cuposMoto(): Cupo | undefined {
    return this.cupos.find(
      cupo => cupo.tipo_vehiculo === 'MOTO'
    );
  }

  get totalCapacidad(): number {
    return this.cupos.reduce(
      (total, cupo) => total + cupo.capacidad,
      0
    );
  }

  get totalOcupados(): number {
    return this.cupos.reduce(
      (total, cupo) => total + cupo.ocupados,
      0
    );
  }

  get totalDisponibles(): number {
    return this.cupos.reduce(
      (total, cupo) => total + cupo.disponibles,
      0
    );
  }

  consultarCupos(): void {
    this.cargando = true;
    this.error = '';
    this.mensaje = '';

    this.cdr.detectChanges();

    this.cupoService.consultarPorSede(this.sedeId)
      .pipe(
        finalize(() => {
          this.cargando = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: respuesta => {
          this.cupos = respuesta;

          this.formulario = {
            cupos_carro: this.cuposCarro?.capacidad ?? 0,
            cupos_moto: this.cuposMoto?.capacidad ?? 0
          };

          this.cdr.detectChanges();
        },

        error: error => {
          this.cupos = [];

          this.error = error.error?.detail
            || `No fue posible consultar los cupos. Código HTTP: ${error.status || 'sin conexión'}`;

          this.cdr.detectChanges();
        }
      });
  }

  guardarCambios(): void {
    this.error = '';
    this.mensaje = '';

    if (
      !Number.isInteger(this.formulario.cupos_carro) ||
      !Number.isInteger(this.formulario.cupos_moto) ||
      this.formulario.cupos_carro < 0 ||
      this.formulario.cupos_moto < 0
    ) {
      this.error = 'Las capacidades deben ser números enteros mayores o iguales a cero.';
      return;
    }

    if (
      this.formulario.cupos_carro <
      (this.cuposCarro?.ocupados ?? 0)
    ) {
      this.error = 'La capacidad de carros no puede ser inferior a los vehículos ocupados.';
      return;
    }

    if (
      this.formulario.cupos_moto <
      (this.cuposMoto?.ocupados ?? 0)
    ) {
      this.error = 'La capacidad de motos no puede ser inferior a las motocicletas ocupadas.';
      return;
    }

    this.guardando = true;
    this.cdr.detectChanges();

    this.cupoService.actualizar(
      this.sedeId,
      this.formulario
    )
      .pipe(
        finalize(() => {
          this.guardando = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: () => {
          this.mensaje = 'La capacidad de los cupos se actualizó correctamente.';
          this.consultarCupos();
        },

        error: error => {
          this.error = error.error?.detail
            || `No fue posible actualizar los cupos. Código HTTP: ${error.status || 'sin conexión'}`;

          this.cdr.detectChanges();
        }
      });
  }

  porcentajeOcupacion(cupo: Cupo | undefined): number {
    if (!cupo || cupo.capacidad === 0) {
      return 0;
    }

    return Math.round(
      (cupo.ocupados / cupo.capacidad) * 100
    );
  }
}
