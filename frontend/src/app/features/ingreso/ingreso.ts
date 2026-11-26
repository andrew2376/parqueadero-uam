import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { IngresoService, PlacaSimulada } from '../../core/services/ingreso.service';
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

  placaActual = 'ABC123';
  confianzaActual = 96;
  cuposActuales = 72;

  placaOriginalLPR = 'ABC123';
  confianzaOriginalLPR = 96;

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
      tipoVehiculoTexto: ['Automóvil'],
      sede: ['Sede principal']
    });
  }

  get esBajaConfianza(): boolean {
    return this.confianzaActual < 70;
  }

  onSimularLectura(): void {
    const lectura: PlacaSimulada = this.ingresoService.simularLectura();
    this.placaActual = lectura.placa;
    this.confianzaActual = lectura.confianza;
    this.placaOriginalLPR = lectura.placa;
    this.confianzaOriginalLPR = lectura.confianza;
    this.resultadoIngreso = null;
    this.mensajeValidacionManual = null;

    const tipoTexto = lectura.tipo === 'MOTO' ? 'Motocicleta' : 'Automóvil';
    this.ingresoForm.patchValue({
      placa: lectura.placa,
      tipoVehiculoTexto: tipoTexto
    });
  }

  onPlacaManualChange(): void {
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
    if (this.ingresoForm.invalid) return;

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
    }).subscribe({
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
