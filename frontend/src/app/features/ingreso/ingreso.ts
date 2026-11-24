import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { EscenarioSimulacion, IngresoService } from '../../core/services/ingreso.service';
import { AuthService } from '../../core/services/auth.service';
import { ResultadoAcceso } from '../../core/models';

@Component({
  selector: 'app-control-ingreso',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './ingreso.html',
  styleUrls: ['./ingreso.css']
})
export class ControlIngresoComponent implements OnInit {
  ingresoForm!: FormGroup;

  placaActual = '';
  confianzaActual = 0;
  cuposActuales = 72;

  placaOriginalLPR = '';
  confianzaOriginalLPR = 0;

  escenario: EscenarioSimulacion = 'alta';
  simulando = false;
  mensajeSimulacion: string | null = null;
  private simulacionSolicitada = false;
  private simulacionFallida = false;
  private requiereConfirmacionManual = false;

  procesando = false;
  resultadoIngreso: ResultadoAcceso | null = null;
  mensajeValidacionManual: string | null = null;

  constructor(
    private fb: FormBuilder,
    private ingresoService: IngresoService,
    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.ingresoForm = this.fb.group({
      placa: [this.placaActual, [Validators.required, Validators.pattern(/^[a-zA-Z0-9]{5,6}$/)]],
      tipoVehiculoTexto: ['Desconocido'],
      sede: ['Sede principal']
    });
  }

  get esBajaConfianza(): boolean {
    return this.requiereConfirmacionManual;
  }

  seleccionarEscenario(valor: string): void {
    if (valor === 'alta' || valor === 'baja' || valor === 'sin-lectura') {
      this.escenario = valor;
    }
  }

  onSimularLectura(): void {
    if (this.simulando || this.procesando) return;

    this.simulando = true;
    this.simulacionSolicitada = true;
    this.simulacionFallida = false;
    this.requiereConfirmacionManual = false;
    this.placaActual = this.placaOriginalLPR = '';
    this.confianzaActual = this.confianzaOriginalLPR = 0;
    this.ingresoForm.patchValue({ placa: '', tipoVehiculoTexto: 'Desconocido' });
    this.resultadoIngreso = null;
    this.mensajeValidacionManual = null;
    this.mensajeSimulacion = null;

    this.ingresoService.simularLectura(this.ingresoService.carrilEntradaDefault, this.escenario)
      .subscribe({
        next: lectura => {
          this.simulando = false;
          this.placaActual = this.placaOriginalLPR = lectura.placa ?? '';
          this.confianzaActual = this.confianzaOriginalLPR = lectura.confianza;
          this.requiereConfirmacionManual = lectura.requiere_confirmacion_manual;
          if (lectura.estado === 'FALLIDA') this.mensajeSimulacion = 'No se detectó una placa.';
          const tipoTexto = lectura.tipo_vehiculo === 'MOTO' ? 'Motocicleta' :
            lectura.tipo_vehiculo === 'CARRO' ? 'Automóvil' : 'Desconocido';
          this.ingresoForm.patchValue({ placa: this.placaActual, tipoVehiculoTexto: tipoTexto });
          this.cdr.markForCheck();
        },
        error: () => {
          this.simulando = false;
          this.simulacionFallida = true;
          this.mensajeSimulacion = 'No fue posible obtener la lectura del servidor.';
          this.cdr.markForCheck();
        }
      });
  }

  onPlacaManualChange(): void {
    this.simulacionFallida = false;
    const valor = this.ingresoForm.get('placa')?.value || '';
    const placaLimpia = valor.toUpperCase().trim();
    this.placaActual = placaLimpia;
    this.resultadoIngreso = null;

    const tipo = this.ingresoService.clasificarPlaca(placaLimpia);
    let tipoTexto = 'Desconocido';
    if (tipo === 'CARRO') tipoTexto = 'Automóvil';
    if (tipo === 'MOTO') tipoTexto = 'Motocicleta';

    this.ingresoForm.patchValue({
      tipoVehiculoTexto: tipoTexto
    }, { emitEvent: false });
  }

  onRegistrarIngreso(): void {
    if (this.ingresoForm.invalid || this.procesando || this.simulando || this.simulacionFallida) return;

    this.procesando = true;
    const placa = (this.ingresoForm.get('placa')?.value || '').toUpperCase().trim();
    const operadorId = this.authService.usuarioActual?.id || 'operador-demo-01';

    // Si hubo baja confianza previa o corrección manual, auditamos la validación manual (S201)
    if (this.esBajaConfianza || placa !== this.placaOriginalLPR) {
      this.ingresoService.validarLecturaManual({
        carrilId: this.ingresoService.carrilEntradaDefault,
        placaConfirmada: placa,
        operadorId: operadorId,
        placaDetectadaPrevia: this.placaOriginalLPR,
        confianzaPrevia: this.confianzaOriginalLPR
      }).subscribe({
        next: (res) => {
          this.mensajeValidacionManual = `Lectura auditada por operador (${res.estado})`;
        }
      });
    }

    // Registramos el ingreso formal (S113 / S116)
    this.ingresoService.registrarIngreso({
      carrilId: this.ingresoService.carrilEntradaDefault,
      placa: placa,
      confianzaLectura: this.confianzaActual
    }, this.simulacionSolicitada).subscribe({
      next: (res) => {
        this.procesando = false;
        this.resultadoIngreso = res;
        if (res.cuposDisponibles?.carros !== undefined) {
          this.cuposActuales = res.cuposDisponibles.carros;
        }
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.procesando = false;
        this.resultadoIngreso = {
          permitido: false,
          estadoBarrera: 'CERRADA',
          tipoVehiculo: 'CARRO',
          placa: placa,
          mensaje: 'Error de comunicación con el servidor',
          fechaHora: new Date().toISOString()
        };
        this.cdr.detectChanges();
      }
    });
  }
}
