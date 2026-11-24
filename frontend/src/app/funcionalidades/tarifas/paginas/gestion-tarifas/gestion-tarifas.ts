
import {
  Component,
  OnInit,
  inject,
  ChangeDetectorRef
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { TarifaService } from '../../servicios/tarifa.service';

import {
  Tarifa,
  CrearTarifa,
  TipoVehiculoTarifa
} from '../../modelos/tarifa.model';

@Component({
  selector: 'app-gestion-tarifas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './gestion-tarifas.html',
  styleUrl: './gestion-tarifas.css'
})
export class GestionTarifas implements OnInit {

  private readonly tarifaService = inject(TarifaService);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly sedeId = '03793b27-4b34-42ea-9bb0-28f8bc5b330d';

  tarifas: Tarifa[] = [];
  versiones: Tarifa[] = [];

  tipoFiltro: 'TODOS' | TipoVehiculoTarifa = 'TODOS';
  tipoHistorial: TipoVehiculoTarifa = 'CARRO';

  cargando = true;
  cargandoHistorial = false;
  guardando = false;
  cerrando = false;

  error = '';
  errorFormulario = '';
  mensaje = '';

  mostrarFormulario = false;
  mostrarHistorial = false;
  mostrarCierre = false;

  tarifaACerrar: Tarifa | null = null;

  vigenciaDesdeLocal = '';
  vigenciaHastaLocal = '';

  formulario: CrearTarifa = this.nuevoFormulario();

  // Inicialización del componente

  ngOnInit(): void {
    this.listarTarifas();
  }

  // Información calculada para la interfaz

  get tarifasFiltradas(): Tarifa[] {
    if (this.tipoFiltro === 'TODOS') {
      return this.tarifas;
    }

    return this.tarifas.filter(
      tarifa => tarifa.tipo_vehiculo === this.tipoFiltro
    );
  }

  get totalActivas(): number {
    return this.tarifas.filter(
      tarifa => tarifa.activa
    ).length;
  }

  get totalCarros(): number {
    return this.tarifas.filter(
      tarifa => tarifa.tipo_vehiculo === 'CARRO'
    ).length;
  }

  get totalMotos(): number {
    return this.tarifas.filter(
      tarifa => tarifa.tipo_vehiculo === 'MOTO'
    ).length;
  }

  // Formulario

  nuevoFormulario(): CrearTarifa {
    return {
      sede_id: this.sedeId,
      tipo_vehiculo: 'CARRO',
      tarifa_diurna: 0,
      tarifa_nocturna: 0
    };
  }

  abrirFormulario(): void {
    this.formulario = this.nuevoFormulario();
    this.vigenciaDesdeLocal = '';
    this.errorFormulario = '';
    this.mensaje = '';
    this.mostrarFormulario = true;

    this.cdr.markForCheck();
  }

  cancelarFormulario(): void {
    this.mostrarFormulario = false;
    this.formulario = this.nuevoFormulario();
    this.vigenciaDesdeLocal = '';
    this.errorFormulario = '';

    this.cdr.markForCheck();
  }

  // Consultar tarifas de la sede

  listarTarifas(): void {
    this.cargando = true;
    this.error = '';

    this.cdr.markForCheck();

    this.tarifaService.listarPorSede(this.sedeId).subscribe({
      next: respuesta => {
        this.tarifas = respuesta;
        this.cargando = false;
        this.error = '';

        console.log('Tarifas cargadas:', this.tarifas);

        this.cdr.markForCheck();
      },
      error: error => {
        console.error('Error al cargar tarifas:', error);

        this.tarifas = [];
        this.cargando = false;
        this.error = 'No fue posible cargar las tarifas.';

        this.cdr.markForCheck();
      }
    });
  }

  // Crear una nueva versión de tarifa

  guardarTarifa(): void {
    this.errorFormulario = '';

    if (
      this.formulario.tarifa_diurna < 0 ||
      this.formulario.tarifa_nocturna < 0
    ) {
      this.errorFormulario = 'Las tarifas no pueden ser negativas.';
      return;
    }

    const motoGratuita =
      this.formulario.tipo_vehiculo === 'MOTO' &&
      this.formulario.tarifa_diurna === 0 &&
      this.formulario.tarifa_nocturna === 0;

    if (
      !motoGratuita &&
      this.formulario.tarifa_nocturna >= this.formulario.tarifa_diurna
    ) {
      this.errorFormulario =
        'La tarifa nocturna debe ser menor que la tarifa diurna.';
      return;
    }

    const datos: CrearTarifa = {
      ...this.formulario,
      ...(this.vigenciaDesdeLocal
        ? {
            vigencia_desde: new Date(
              this.vigenciaDesdeLocal
            ).toISOString()
          }
        : {})
    };

    this.guardando = true;
    this.cdr.markForCheck();

    this.tarifaService.crear(datos).subscribe({
      next: respuesta => {
        console.log('Tarifa creada correctamente:', respuesta);

        this.guardando = false;
        this.mostrarFormulario = false;

        this.formulario = this.nuevoFormulario();
        this.vigenciaDesdeLocal = '';

        this.mensaje =
          'La nueva versión de tarifa fue creada correctamente.';

        this.cdr.markForCheck();

        // Actualizar automáticamente el listado
        this.listarTarifas();
      },

      error: respuesta => {
        console.error('Error al crear tarifa:', respuesta);

        this.guardando = false;

        this.errorFormulario =
          respuesta?.error?.detail ||
          'No fue posible crear la tarifa. Verifica los datos e inténtalo nuevamente.';

        this.cdr.markForCheck();
      }
    });
  }

  // Consultar historial de versiones

  abrirHistorial(tipo: TipoVehiculoTarifa): void {
    this.tipoHistorial = tipo;
    this.versiones = [];
    this.error = '';

    this.mostrarHistorial = true;
    this.cargandoHistorial = true;

    this.cdr.markForCheck();

    this.tarifaService.listarVersiones(
      this.sedeId,
      tipo
    ).subscribe({
      next: respuesta => {
        this.versiones = respuesta;
        this.cargandoHistorial = false;

        this.cdr.markForCheck();
      },

      error: error => {
        console.error('Error al consultar historial:', error);

        this.versiones = [];
        this.cargandoHistorial = false;
        this.error = 'No fue posible consultar el historial de versiones.';

        this.cdr.markForCheck();
      }
    });
  }

  cerrarHistorial(): void {
    this.mostrarHistorial = false;
    this.versiones = [];

    this.cdr.markForCheck();
  }

  // Cerrar vigencia de una tarifa

  abrirCierre(tarifa: Tarifa): void {
    this.tarifaACerrar = tarifa;
    this.vigenciaHastaLocal = this.obtenerFechaHoraLocal();
    this.errorFormulario = '';
    this.mostrarCierre = true;

    this.cdr.markForCheck();
  }

  confirmarCierre(): void {
    if (!this.tarifaACerrar || !this.vigenciaHastaLocal) {
      this.errorFormulario =
        'Debes indicar la fecha y hora de finalización.';
      return;
    }

    const fechaCierre = new Date(this.vigenciaHastaLocal);

    if (Number.isNaN(fechaCierre.getTime())) {
      this.errorFormulario = 'La fecha indicada no es válida.';
      return;
    }

    const fechaInicio = new Date(
      this.tarifaACerrar.vigencia_desde
    );

    if (fechaCierre <= fechaInicio) {
      this.errorFormulario =
        'La fecha de finalización debe ser posterior al inicio de vigencia.';
      return;
    }

    this.cerrando = true;
    this.errorFormulario = '';

    this.cdr.markForCheck();

    this.tarifaService.cerrarVigencia(
      this.tarifaACerrar.id,
      {
        vigencia_hasta: fechaCierre.toISOString()
      }
    ).subscribe({
      next: () => {
        this.cerrando = false;
        this.mostrarCierre = false;
        this.tarifaACerrar = null;

        this.vigenciaHastaLocal = '';

        this.mensaje =
          'La vigencia de la tarifa fue cerrada correctamente.';

        this.cdr.markForCheck();

        // Actualizar el listado principal
        this.listarTarifas();

        // Actualizar historial si está abierto
        if (this.mostrarHistorial) {
          this.abrirHistorial(this.tipoHistorial);
        }
      },

      error: respuesta => {
        console.error('Error al cerrar vigencia:', respuesta);

        this.cerrando = false;

        this.errorFormulario =
          respuesta?.error?.detail ||
          'No fue posible cerrar la vigencia de esta tarifa.';

        this.cdr.markForCheck();
      }
    });
  }

  cancelarCierre(): void {
    this.mostrarCierre = false;
    this.tarifaACerrar = null;
    this.vigenciaHastaLocal = '';
    this.errorFormulario = '';

    this.cdr.markForCheck();
  }

  // Obtener fecha y hora local para los formularios

  private obtenerFechaHoraLocal(): string {
    const ahora = new Date();
    const zona = ahora.getTimezoneOffset() * 60000;

    return new Date(ahora.getTime() - zona)
      .toISOString()
      .slice(0, 16);
  }

  // Formato de valores monetarios

  formatoMoneda(valor: number): string {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0
    }).format(valor);
  }
}
