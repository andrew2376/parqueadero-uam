
import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { CarrilService } from '../../servicios/carril.service';
import {
  Carril,
  CrearCarril,
  TipoCarril
} from '../../modelos/carril.model';

@Component({
  selector: 'app-gestion-carriles',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './gestion-carriles.html',
  styleUrl: './gestion-carriles.css'
})
export class GestionCarriles implements OnInit {

  private readonly carrilService = inject(CarrilService);

  readonly sedeId = '03793b27-4b34-42ea-9bb0-28f8bc5b330d';

  carriles: Carril[] = [];

  cargando = false;
  guardando = false;
  error = '';

  mostrarFormulario = false;
  carrilEditando: string | null = null;

  formulario: CrearCarril = this.nuevoFormulario();

  ngOnInit(): void {
    this.listarCarriles();
  }

  listarCarriles(): void {
    this.cargando = true;
    this.error = '';

    this.carrilService.listarPorSede(this.sedeId).subscribe({
      next: (respuesta) => {
        this.carriles = respuesta;
        this.cargando = false;
      },
      error: () => {
        this.error = 'No fue posible cargar los carriles.';
        this.cargando = false;
      }
    });
  }

  nuevoFormulario(): CrearCarril {
    return {
      sede_id: this.sedeId,
      nombre: '',
      tipo: 'ENTRADA'
    };
  }

  abrirFormulario(): void {
    this.carrilEditando = null;
    this.formulario = this.nuevoFormulario();
    this.mostrarFormulario = true;
  }

  editarCarril(carril: Carril): void {
    this.carrilEditando = carril.id;

    this.formulario = {
      sede_id: carril.sede_id,
      nombre: carril.nombre,
      tipo: carril.tipo
    };

    this.mostrarFormulario = true;
  }

  guardarCarril(): void {
    if (!this.formulario.nombre.trim()) {
      this.error = 'El nombre del carril es obligatorio.';
      return;
    }

    this.guardando = true;
    this.error = '';

    const operacion = this.carrilEditando
      ? this.carrilService.actualizar(
          this.carrilEditando,
          this.formulario
        )
      : this.carrilService.crear(this.formulario);

    operacion.subscribe({
      next: () => {
        this.guardando = false;
        this.mostrarFormulario = false;
        this.listarCarriles();
      },
      error: () => {
        this.guardando = false;
        this.error = 'No fue posible guardar el carril.';
      }
    });
  }

  cambiarEstado(carril: Carril): void {
    this.carrilService
      .cambiarEstado(carril.id, !carril.activo)
      .subscribe({
        next: () => this.listarCarriles(),
        error: () => {
          this.error = 'No fue posible cambiar el estado del carril.';
        }
      });
  }

  cancelarFormulario(): void {
    this.mostrarFormulario = false;
    this.carrilEditando = null;
    this.formulario = this.nuevoFormulario();
    this.error = '';
  }
}
