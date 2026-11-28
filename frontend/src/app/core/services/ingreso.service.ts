import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { map, switchMap } from 'rxjs';
import { API_BASE_URL } from '../api.config';
import { TipoVehiculo } from '../models/vehiculo.model';

export type Direccion = 'ENTRADA' | 'SALIDA';

export interface CarrilActivo {
  id: string;
  sede_id: string;
  nombre_sede: string;
  nombre: string;
  tipo: Direccion | 'MIXTO';
  activo: boolean;
}

export interface Cupo {
  tipo_vehiculo: TipoVehiculo;
  disponibles: number;
}

export interface ResultadoOperacion {
  abierta: boolean;
  mensaje: string;
}

@Injectable({ providedIn: 'root' })
export class IngresoService {
  private readonly http = inject(HttpClient);

  listarCarriles() {
    return this.http.get<{ sede_id: string; sede_nombre: string }>(
      `${API_BASE_URL}/panel/resumen`,
    ).pipe(switchMap(sede => {
      const url = `${API_BASE_URL}/carriles/sede/${encodeURIComponent(sede.sede_id)}`;
      return this.http.get<Omit<CarrilActivo, 'nombre_sede'>[]>(url).pipe(
        map(carriles => carriles
          .filter(carril => carril.activo && carril.sede_id === sede.sede_id)
          .map(carril => ({ ...carril, nombre_sede: sede.sede_nombre }))),
      );
    }));
  }

  consultarCupos(sedeId: string) {
    return this.http.get<Cupo[]>(`${API_BASE_URL}/cupos/sede/${encodeURIComponent(sedeId)}`);
  }

  guardarLecturaManual(carril: CarrilActivo, placa: string) {
    return this.http.post<{ sede_id: string; carril_id: string; placa: string; origen: string }>(
      `${API_BASE_URL}/lecturas-lpr/manual`, { carril_id: carril.id, placa },
    ).pipe(map(evento => {
      if (evento.sede_id !== carril.sede_id || evento.carril_id !== carril.id
        || evento.placa !== placa || evento.origen !== 'MANUAL') {
        throw new Error('La evidencia no coincide con el ingreso.');
      }
    }));
  }

  registrar(direccion: Direccion, carril: CarrilActivo, placa: string) {
    const datos = { sede_id: carril.sede_id, carril_id: carril.id, placa };
    if (direccion === 'ENTRADA') {
      return this.http.post<{
        autorizado: boolean;
        decision_barrera: string;
        mensaje: string;
      }>(`${API_BASE_URL}/accesos/ingreso`, datos).pipe(map(res => ({
        abierta: res.autorizado === true && res.decision_barrera === 'ABRIR',
        mensaje: res.mensaje,
      })));
    }
    return this.http.get<Omit<CarrilActivo, 'nombre_sede'>>(
      `${API_BASE_URL}/carriles/${encodeURIComponent(carril.id)}`,
    ).pipe(switchMap(actual => {
      if (actual.id !== carril.id || actual.sede_id !== carril.sede_id || !actual.activo
        || (actual.tipo !== 'SALIDA' && actual.tipo !== 'MIXTO')) {
        throw new Error('El carril ya no está habilitado para salida en esta sede.');
      }
      return this.http.post<{
        autorizado: boolean;
        decision_barrera: string;
        motivo: string;
      }>(`${API_BASE_URL}/estancias/salida`, { sede_id: carril.sede_id, placa });
    }), map(res => ({
      abierta: res.autorizado === true && res.decision_barrera === 'AUTORIZAR',
      mensaje: res.motivo,
    })));
  }
}
