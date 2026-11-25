import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { API_BASE_URL } from '../api.config';
import { ResultadoAcceso } from '../models/acceso.model';
import { TipoVehiculo } from '../models/vehiculo.model';

export interface CarrilCamara {
  id: string;
  sede_id: string;
  nombre: string;
  tipo: 'ENTRADA' | 'SALIDA' | 'MIXTO';
  activo: boolean;
}

export interface SolicitudIngreso {
  sedeId: string;
  carrilId: string;
  placa: string;
}

export type ResultadoIngreso = Omit<ResultadoAcceso, 'tipoVehiculo' | 'cuposDisponibles'> & {
  tipoVehiculo: TipoVehiculo | null;
  cuposRestantes: number | null;
};

export type ResultadoSalida = Pick<ResultadoAcceso, 'permitido' | 'estadoBarrera' | 'mensaje'>;

export type DireccionCamara = 'ENTRADA' | 'SALIDA';

export type EscenarioSimulacion = 'alta' | 'baja' | 'sin-lectura';

export interface LecturaSimulada {
  id: string;
  direccion: DireccionCamara;
  placa: string | null;
  tipo_vehiculo: TipoVehiculo | null;
  confianza: number;
  estado: 'EXITOSA' | 'BAJA_CONFIANZA' | 'FALLIDA';
  requiere_confirmacion_manual: boolean;
}

interface IngresoRespuesta {
  autorizado: boolean;
  decision_barrera: 'ABRIR' | 'MANTENER_CERRADA';
  placa: string;
  tipo_vehiculo: TipoVehiculo | null;
  mensaje: string;
  cupos_disponibles_restantes: number | null;
}

interface SalidaRespuesta {
  autorizado: boolean;
  decision_barrera: 'AUTORIZAR' | 'DENEGAR';
  motivo: string;
}

@Injectable({ providedIn: 'root' })
export class IngresoService {
  private readonly apiUrl = `${API_BASE_URL}/accesos`;

  constructor(private http: HttpClient) {}

  consultarCarril(id: string): Observable<CarrilCamara> {
    return this.http.get<CarrilCamara>(`${API_BASE_URL}/carriles/${encodeURIComponent(id)}`);
  }

  simularLectura(carrilId: string, escenario: EscenarioSimulacion, direccion: DireccionCamara): Observable<LecturaSimulada> {
    return this.http.post<LecturaSimulada>(`${API_BASE_URL}/lecturas-lpr/simulacion`, null, {
      params: { carril_id: carrilId, escenario, direccion }
    });
  }

  confirmarPlaca(carril_id: string, placa: string) {
    return this.http.post<{ placa: string | null; estado: string }>(
      `${API_BASE_URL}/lecturas-lpr/manual`, { carril_id, placa }
    );
  }

  consultarCupos(sedeId: string) {
    return this.http.get<{ tipo_vehiculo: TipoVehiculo; disponibles: number }[]>(
      `${API_BASE_URL}/cupos/sede/${encodeURIComponent(sedeId)}`
    );
  }

  registrarIngreso(solicitud: SolicitudIngreso): Observable<ResultadoIngreso> {
    return this.http.post<IngresoRespuesta>(`${this.apiUrl}/ingreso`, {
      sede_id: solicitud.sedeId,
      carril_id: solicitud.carrilId,
      placa: solicitud.placa
    }).pipe(
      map(res => {
        const permitido = res.autorizado === true && res.decision_barrera === 'ABRIR';
        const cupos = res.cupos_disponibles_restantes;
        return {
          permitido,
          estadoBarrera: permitido ? 'ABIERTA' : 'CERRADA',
          tipoVehiculo: res.tipo_vehiculo,
          placa: res.placa,
          mensaje: res.mensaje,
          cuposRestantes: typeof cupos === 'number' && Number.isInteger(cupos) && cupos >= 0
            ? cupos : null,
          fechaHora: new Date().toISOString()
        };
      })
    );
  }

  registrarSalida(sedeId: string, placa: string): Observable<ResultadoSalida> {
    return this.http.post<SalidaRespuesta>(`${API_BASE_URL}/estancias/salida`, {
      sede_id: sedeId,
      placa
    }).pipe(map(res => {
      const permitido = res.autorizado === true && res.decision_barrera === 'AUTORIZAR';
      return { permitido, estadoBarrera: permitido ? 'ABIERTA' : 'CERRADA', mensaje: res.motivo };
    }));
  }
}
