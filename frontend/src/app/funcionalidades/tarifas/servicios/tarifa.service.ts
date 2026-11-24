
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  Tarifa,
  CrearTarifa,
  CerrarVigenciaTarifa,
  TarifaCalculo,
  TipoVehiculoTarifa
} from '../modelos/tarifa.model';

@Injectable({
  providedIn: 'root'
})
export class TarifaService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8001/api/v1/tarifas';

  listarPorSede(sedeId: string): Observable<Tarifa[]> {
    return this.http.get<Tarifa[]>(`${this.apiUrl}/sede/${sedeId}`);
  }

  listarVersiones(
    sedeId: string,
    tipoVehiculo: TipoVehiculoTarifa
  ): Observable<Tarifa[]> {
    return this.http.get<Tarifa[]>(
      `${this.apiUrl}/sede/${sedeId}/tipo/${tipoVehiculo}/versiones`
    );
  }

  crear(datos: CrearTarifa): Observable<Tarifa> {
    return this.http.post<Tarifa>(this.apiUrl, datos);
  }

  cerrarVigencia(
    tarifaId: string,
    datos: CerrarVigenciaTarifa
  ): Observable<Tarifa> {
    return this.http.patch<Tarifa>(
      `${this.apiUrl}/${tarifaId}/vigencia`,
      datos
    );
  }

  consultarVigente(
    sedeId: string,
    tipoVehiculo: TipoVehiculoTarifa,
    fechaHora: string,
    zonaHoraria = 'America/Bogota'
  ): Observable<TarifaCalculo> {
    const params = new HttpParams()
      .set('sede_id', sedeId)
      .set('tipo_vehiculo', tipoVehiculo)
      .set('fecha_hora', fechaHora)
      .set('zona_horaria', zonaHoraria);

    return this.http.get<TarifaCalculo>(
      `${this.apiUrl}/vigente`,
      { params }
    );
  }

  calcular(
    sedeId: string,
    tipoVehiculo: TipoVehiculoTarifa,
    fechaHora: string,
    zonaHoraria = 'America/Bogota'
  ): Observable<TarifaCalculo> {
    const params = new HttpParams()
      .set('sede_id', sedeId)
      .set('tipo_vehiculo', tipoVehiculo)
      .set('fecha_hora', fechaHora)
      .set('zona_horaria', zonaHoraria);

    return this.http.post<TarifaCalculo>(
      `${this.apiUrl}/calcular`,
      null,
      { params }
    );
  }
}
