import { ChangeDetectorRef, Component, DestroyRef, OnInit, inject } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormBuilder, FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { Observable, finalize, map, of, switchMap } from 'rxjs';
import { AuthService } from '../../core/services/auth.service';
import {
  CarrilCamara, DireccionCamara, EscenarioSimulacion, IngresoService, LecturaSimulada,
  ResultadoIngreso, ResultadoSalida
} from '../../core/services/ingreso.service';
import { TipoVehiculo } from '../../core/models/vehiculo.model';

@Component({
  selector: 'app-control-ingreso',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './ingreso.html',
  styleUrls: ['./ingreso.css']
})
export class ControlIngresoComponent implements OnInit {
  private readonly destroyRef = inject(DestroyRef);
  private readonly ingresoService = inject(IngresoService);
  private readonly authService = inject(AuthService);
  private readonly route = inject(ActivatedRoute);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly ingresoForm = inject(FormBuilder).nonNullable.group({
    placa: ['', [Validators.required, Validators.maxLength(10)]],
    tipoVehiculoTexto: ['']
  });
  readonly escenario = new FormControl<EscenarioSimulacion>('alta', { nonNullable: true });
  readonly identificadorCarril = new FormControl('', { nonNullable: true });
  direccion: DireccionCamara = 'ENTRADA';
  carril: CarrilCamara | null = null;
  estadoCarril = 'Introduce el UUID del carril MIXTO para habilitar las cámaras.';
  confirmandoAcceso = false;
  lectura: LecturaSimulada | null = null;
  resultadoIngreso: ResultadoSalida | null = null;
  mensaje = '';
  procesando = false;
  cupos: Partial<Record<TipoVehiculo, number>> = {};

  ngOnInit(): void {
    const id = this.route.snapshot.queryParamMap.get('carril');
    if (id) {
      this.identificadorCarril.setValue(id);
      this.cargarCarril();
    }
  }

  get operacion(): string {
    return this.direccion === 'ENTRADA' ? 'ingreso' : 'salida';
  }

  cargarCarril(): void {
    if (this.procesando) return;
    this.carril = null;
    this.cupos = {};
    this.limpiarCaptura();
    this.estadoCarril = 'Validando carril en el servidor...';
    const id = this.identificadorCarril.value.trim();
    if (!/^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(id)) {
      this.estadoCarril = 'Introduce un UUID de carril válido.';
      return;
    }
    this.ejecutar(this.ingresoService.consultarCarril(id), carril => {
      if (!carril.activo || carril.tipo !== 'MIXTO') {
        this.estadoCarril = 'El carril debe estar activo y ser de tipo MIXTO.';
        return;
      }
      this.carril = carril;
      this.estadoCarril = 'Carril MIXTO activo y verificado';
      this.actualizarCupos(carril);
    }, error => {
      this.estadoCarril = error instanceof HttpErrorResponse && error.status === 404
        ? 'El carril no existe. Revisa el UUID.'
        : 'No se pudo verificar el carril con el servidor.';
    });
  }

  seleccionarCamara(direccion: DireccionCamara): void {
    if (this.procesando || this.direccion === direccion) return;
    this.direccion = direccion;
    this.limpiarCaptura();
  }

  get tipoDetectado(): string {
    if (this.lectura?.tipo_vehiculo === 'CARRO') return 'Automóvil';
    if (this.lectura?.tipo_vehiculo === 'MOTO') return 'Motocicleta';
    return 'Sin clasificar';
  }

  onSimularLectura(): void {
    if (this.procesando || !this.carril) return;
    this.limpiarCaptura();
    this.ejecutar(
      this.ingresoService.simularLectura(this.carril.id, this.escenario.value, this.direccion),
      lectura => {
        if (lectura.direccion !== this.direccion) {
          this.mensaje = 'La respuesta no corresponde a la cámara seleccionada.';
          return;
        }
        this.lectura = lectura;
        this.ingresoForm.setValue({
          placa: lectura.placa ?? '',
          tipoVehiculoTexto: lectura.placa ? this.tipoDetectado : ''
        });

      }
    );
  }

  onPlacaManualChange(): void {
    this.resultadoIngreso = null;
    this.mensaje = '';
    this.ingresoForm.controls.tipoVehiculoTexto.setValue('Por confirmar');
  }

  onRegistrarIngreso(): void {
    const carril = this.carril;
    if (this.procesando || !carril || this.ingresoForm.invalid) return;

    this.resultadoIngreso = null;
    this.mensaje = '';
    if (!this.authService.usuarioActual?.id) {
      this.mensaje = 'Inicia sesión para registrar el acceso.';
      return;
    }

    const placa = this.ingresoForm.controls.placa.value;
    const requiereConfirmacion = this.lectura?.estado !== 'EXITOSA'
      || this.lectura.requiere_confirmacion_manual || placa !== this.lectura.placa;
    const confirmada$ = requiereConfirmacion
      ? this.ingresoService.confirmarPlaca(carril.id, placa).pipe(map(lectura => {
          if (lectura.estado !== 'EXITOSA' || !lectura.placa) {
            throw new Error('La placa no quedó confirmada.');
          }
          this.ingresoForm.patchValue({ placa: lectura.placa, tipoVehiculoTexto: 'Placa confirmada' });
          return lectura.placa;
        }))
      : of(placa);

    this.confirmandoAcceso = true;
    this.ejecutar<ResultadoIngreso | ResultadoSalida>(confirmada$.pipe(
      switchMap(placaValidada => this.direccion === 'ENTRADA'
        ? this.ingresoService.registrarIngreso({
            sedeId: carril.sede_id, carrilId: carril.id, placa: placaValidada
          })
        : this.ingresoService.registrarSalida(carril.sede_id, placaValidada)
      ),
      finalize(() => { this.confirmandoAcceso = false; })
    ), resultado => {
      this.resultadoIngreso = resultado;
      if (!resultado.permitido) return;
      if ('cuposRestantes' in resultado && resultado.tipoVehiculo && resultado.cuposRestantes !== null) {
        this.cupos = { ...this.cupos, [resultado.tipoVehiculo]: resultado.cuposRestantes };
      } else {
        this.cupos = {};
      }
      this.actualizarCupos(carril);
    });
  }

  private actualizarCupos(carril: CarrilCamara): void {
    if (this.authService.usuarioActual?.rol !== 'ADMINISTRADOR') return;
    this.ingresoService.consultarCupos(carril.sede_id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: cupos => {
          if (this.carril?.id !== carril.id) return;
          this.cupos = Object.fromEntries(cupos.map(cupo => [cupo.tipo_vehiculo, cupo.disponibles]));
          this.cdr.markForCheck();
        },
        error: () => {}
      });
  }

  private limpiarCaptura(): void {
    this.lectura = null;
    this.resultadoIngreso = null;
    this.mensaje = '';
    this.ingresoForm.reset();
  }

  private ejecutar<T>(
    solicitud: Observable<T>, recibir: (valor: T) => void, fallar?: (error: unknown) => void
  ): void {
    this.procesando = true;
    solicitud.pipe(takeUntilDestroyed(this.destroyRef), finalize(() => {
      this.procesando = false;
      this.cdr.markForCheck();
    })).subscribe({
      next: recibir,
      error: (error: unknown) => {
        if (fallar) {
          fallar(error);
        } else if (error instanceof HttpErrorResponse && typeof error.error?.detail === 'string') {
          this.mensaje = error.error.detail;
        } else if (error instanceof Error && !(error instanceof HttpErrorResponse)) {
          this.mensaje = error.message;
        } else if (error instanceof HttpErrorResponse && error.status === 422) {
          this.mensaje = 'Revisa la placa o el carril seleccionado.';
        } else {
          this.mensaje = 'No se pudo completar la solicitud con el servidor.';
        }
      }
    });
  }
}
