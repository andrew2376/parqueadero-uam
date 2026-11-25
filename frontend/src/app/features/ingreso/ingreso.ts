import { ChangeDetectorRef, Component, DestroyRef, OnInit, inject } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormBuilder, FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { Observable, catchError, finalize, map, of, switchMap } from 'rxjs';
import { AuthService } from '../../core/services/auth.service';
import {
  CarrilCamara, CarrilMixtoDisponible, DireccionCamara, EscenarioSimulacion, IngresoService, LecturaSimulada,
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
  readonly placaSimulada = new FormControl('', { nonNullable: true });
  readonly nombresEscenario: Record<EscenarioSimulacion, string> = {
    alta: 'Confianza alta',
    baja: 'Confianza baja',
    'sin-lectura': 'Sin lectura'
  };
  carriles: CarrilMixtoDisponible[] = [];
  nombreSede: string | null = null;
  ultimaSimulacion: { escenario: EscenarioSimulacion; placa: string } | null = null;
  direccion: DireccionCamara = 'ENTRADA';
  carril: CarrilCamara | null = null;
  estadoCarril = 'Buscando carriles MIXTO activos...';
  confirmandoAcceso = false;
  lectura: LecturaSimulada | null = null;
  resultadoIngreso: ResultadoSalida | null = null;
  mensaje = '';
  procesando = false;
  cupos: Partial<Record<TipoVehiculo, number>> = {};

  ngOnInit(): void {
    const parametros = this.route.snapshot.queryParamMap;
    if (parametros.has('carril')) {
      this.cargarCarril(parametros.get('carril')!);
      return;
    }
    this.cargarCarriles();
  }

  cargarCarriles(): void {
    if (this.procesando) return;
    this.estadoCarril = 'Buscando carriles MIXTO activos...';
    this.ejecutar(
      this.ingresoService.listarCarrilesMixtos(this.route.snapshot.queryParamMap.get('sede')),
      carriles => {
        this.carriles = carriles;
        if (carriles.length === 1) {
          const carril = carriles[0];
          this.activarCarril({ ...carril, tipo: 'MIXTO', activo: true }, carril.nombre_sede);
        } else {
          this.estadoCarril = carriles.length
            ? 'Selecciona un carril por nombre.'
            : 'No hay carriles MIXTO activos disponibles.';
        }
      },
      () => { this.estadoCarril = 'No se pudieron consultar los carriles.'; }
    );
  }

  get operacion(): string {
    return this.direccion === 'ENTRADA' ? 'ingreso' : 'salida';
  }

  cargarCarril(id: string): void {
    if (this.procesando) return;
    this.carril = null;
    this.nombreSede = null;
    this.cupos = {};
    this.limpiarCaptura();
    this.estadoCarril = 'Validando carril en el servidor...';
    if (!id) {
      this.estadoCarril = 'Selecciona un carril por nombre.';
      return;
    }
    this.ejecutar(this.ingresoService.consultarCarril(id), carril => {
      if (!carril.activo || carril.tipo !== 'MIXTO') {
        this.estadoCarril = 'El carril debe estar activo y ser de tipo MIXTO.';
        return;
      }
      const opcion = this.carriles.find(item => item.id === carril.id);
      this.activarCarril(carril, opcion?.nombre_sede ?? null);
      if (!opcion) {
        this.ingresoService.listarCarrilesMixtos(carril.sede_id).pipe(
          map(carriles => carriles.find(item => item.id === carril.id)?.nombre_sede ?? null),
          catchError(() => of(null)),
          takeUntilDestroyed(this.destroyRef)
        ).subscribe(nombre => {
          if (this.carril?.id !== carril.id) return;
          this.nombreSede = nombre;
          this.cdr.markForCheck();
        });
      }
    }, error => {
      this.estadoCarril = error instanceof HttpErrorResponse && error.status === 404
        ? 'El carril no existe. Vuelve a elegir un carril.'
        : 'No se pudo verificar el carril con el servidor.';
    });
  }

  private activarCarril(carril: CarrilCamara, nombreSede: string | null): void {
    this.carril = carril;
    this.nombreSede = nombreSede;
    this.estadoCarril = 'Carril MIXTO activo y verificado';
    this.actualizarCupos(carril);
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

  get ajustesPendientes(): boolean {
    return this.ultimaSimulacion !== null && (
      this.ultimaSimulacion.escenario !== this.escenario.value
      || this.ultimaSimulacion.placa !== this.placaDeProximaSimulacion
    );
  }

  private get placaDeProximaSimulacion(): string {
    return this.escenario.value === 'sin-lectura' ? '' : this.placaSimulada.value.trim();
  }

  onSimularLectura(): void {
    if (this.procesando || !this.carril) return;
    this.limpiarCaptura();
    const escenario = this.escenario.value;
    const placa = this.placaDeProximaSimulacion;
    this.ejecutar(
      this.ingresoService.simularLectura(this.carril.id, escenario, this.direccion, placa),
      lectura => {
        if (lectura.direccion !== this.direccion) {
          this.mensaje = 'La respuesta no corresponde a la cámara seleccionada.';
          return;
        }
        this.lectura = lectura;
        this.ultimaSimulacion = { escenario, placa };
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
    this.ultimaSimulacion = null;
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
