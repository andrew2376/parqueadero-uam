import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs/operators';

import {
  CajaService,
  CobroConsulta,
  PagoRegistrado
} from '../../core/services/caja.service';

@Component({
  selector: 'app-caja',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './caja.html',
  styleUrls: ['./caja.css']
})
export class CajaComponent {
  placa = '';
  efectivoRecibido: number | null = null;

  cobro: CobroConsulta | null = null;
  pagoRegistrado: PagoRegistrado | null = null;

  consultando = false;
  procesandoPago = false;

  mensajeError = '';
  mensajeExito = '';

  private claveIdempotencia = '';

  constructor(private cajaService: CajaService) {}

  get totalCobro(): number {
    return this.cobro ? Number(this.cobro.valor_tarifa) : 0;
  }

  get cambio(): number {
    if (this.efectivoRecibido === null) {
      return 0;
    }

    return Math.max(0, this.efectivoRecibido - this.totalCobro);
  }

  get efectivoInsuficiente(): boolean {
    return (
      this.efectivoRecibido !== null &&
      this.efectivoRecibido < this.totalCobro
    );
  }

  get puedeConfirmarPago(): boolean {
    return (
      !!this.cobro &&
      !this.cobro.pagado &&
      !this.procesandoPago &&
      this.efectivoRecibido !== null &&
      this.efectivoRecibido >= this.totalCobro &&
      this.efectivoRecibido > 0
    );
  }

  consultarCobro(): void {
    const placaNormalizada = this.placa.trim().toUpperCase();

    if (!/^[A-Z0-9]{5,6}$/.test(placaNormalizada)) {
      this.limpiarMensajes();
      this.mensajeError = 'Ingresa una placa válida de 5 o 6 caracteres.';
      return;
    }

    this.consultando = true;
    this.cobro = null;
    this.pagoRegistrado = null;
    this.efectivoRecibido = null;
    this.claveIdempotencia = '';
    this.limpiarMensajes();

    this.cajaService.consultarCobro(placaNormalizada)
      .pipe(finalize(() => {
        this.consultando = false;
      }))
      .subscribe({
        next: (respuesta) => {
          this.cobro = respuesta;
          this.placa = respuesta.placa;

          if (respuesta.pagado) {
            this.mensajeExito = 'Este cobro ya se encuentra pagado.';
          } else {
            this.claveIdempotencia = this.generarClaveIdempotencia();
            this.mensajeExito = 'Cobro encontrado correctamente.';
          }
        },
        error: (error) => {
          this.mensajeError =
            error.error?.detail ||
            'No fue posible consultar el cobro. Verifica la placa e intenta nuevamente.';
        }
      });
  }

  confirmarPago(): void {
    if (!this.cobro || !this.puedeConfirmarPago) {
      return;
    }

    if (!this.claveIdempotencia) {
      this.claveIdempotencia = this.generarClaveIdempotencia();
    }

    this.procesandoPago = true;
    this.limpiarMensajes();

    this.cajaService.registrarPagoEfectivo({
      cobro_id: this.cobro.cobro_id,
      clave_idempotencia: this.claveIdempotencia,
      valor: this.cobro.valor_tarifa
    })
    .pipe(finalize(() => {
      this.procesandoPago = false;
    }))
    .subscribe({
      next: (respuesta) => {
        this.pagoRegistrado = respuesta;

        if (this.cobro) {
          this.cobro = {
            ...this.cobro,
            pagado: true,
            pago_id: respuesta.id,
            fecha_hora_pago: respuesta.fecha_hora_pago
          };
        }

        this.mensajeExito = '¡Pago registrado correctamente!';
      },
      error: (error) => {
        this.mensajeError =
          error.error?.detail ||
          'No fue posible registrar el pago. Puedes volver a intentarlo.';
      }
    });
  }

  nuevaConsulta(): void {
    this.placa = '';
    this.cobro = null;
    this.pagoRegistrado = null;
    this.efectivoRecibido = null;
    this.claveIdempotencia = '';
    this.limpiarMensajes();
  }

  formatearMoneda(valor: number | string): string {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0
    }).format(Number(valor));
  }

  formatearFecha(fecha: string | null): string {
    if (!fecha) {
      return 'No registrada';
    }

    return new Date(fecha).toLocaleString('es-CO');
  }

  private generarClaveIdempotencia(): string {
    return crypto.randomUUID();
  }

  private limpiarMensajes(): void {
    this.mensajeError = '';
    this.mensajeExito = '';
  }
}