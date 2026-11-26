import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ActividadReciente {
  tipo: string;
  placa: string;
  hora: string;
  estado: string;
}

export interface VehiculoActivo {
  placa: string;
  tipo_vehiculo: string;
  ingreso: string;
  estado: string;
}

export interface MetricasPanel {
  sede_id: string;
  sede_nombre: string;
  vehiculos_dentro: int_number;
  cupos_disponibles: number;
  total_cupos: number;
  cupos_carro_disponibles: number;
  cupos_moto_disponibles: number;
  ingresos_hoy: number;
  salidas_hoy: number;
  porcentaje_ocupacion: number;
  actividad_reciente: ActividadReciente[];
  vehiculos_activos: VehiculoActivo[];
}

type int_number = number;

@Injectable({
  providedIn: 'root'
})
export class PanelService {
  private readonly apiUrl = 'http://localhost:8001/api/v1/panel';

  constructor(private http: HttpClient) {}

  obtenerResumen(sedeId?: string): Observable<MetricasPanel> {
    const url = sedeId ? `${this.apiUrl}/resumen?sede_id=${sedeId}` : `${this.apiUrl}/resumen`;
    return this.http.get<MetricasPanel>(url);
  }
}
