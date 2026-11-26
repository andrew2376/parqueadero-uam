import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../api.config';

export interface CobroConsulta {
  cobro_id: string;
  sede_id: string;
  sede_nombre: string;
  placa: string;
  dia_operativo: string;
  tarifa_aplicada: string;
  valor_tarifa: string | number;
  pagado: boolean;
  pago_id: string | null;
  fecha_hora_pago: string | null;
  vehiculo_dentro: boolean;
}

export interface PagoEfectivoSolicitud {
  cobro_id: string;
  clave_idempotencia: string;
  valor: string | number;
}

export interface PagoRegistrado {
  id: string;
  cobro_id: string;
  medio_pago: string;
  valor: string | number;
  fecha_hora_pago: string;
  clave_idempotencia: string;
}

@Injectable({
  providedIn: 'root'
})
export class CajaService {
  private readonly apiUrl = `${API_BASE_URL}/pagos`;

  constructor(private http: HttpClient) {}

  consultarCobro(placa: string): Observable<CobroConsulta> {
    const params = new HttpParams().set('placa', placa.trim().toUpperCase());

    return this.http.get<CobroConsulta>(
      `${this.apiUrl}/cobros/consulta`,
      { params }
    );
  }

  registrarPagoEfectivo(
    datos: PagoEfectivoSolicitud
  ): Observable<PagoRegistrado> {
    return this.http.post<PagoRegistrado>(
      `${this.apiUrl}/efectivo`,
      datos
    );
  }
}