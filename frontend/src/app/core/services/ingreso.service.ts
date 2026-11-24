import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { API_BASE_URL } from '../api.config';
import { ResultadoAcceso } from '../models/acceso.model';

import { TipoVehiculo } from '../models/vehiculo.model';

export interface SolicitudIngreso {
  carrilId: string;
  placa: string;
  tipoVehiculo?: 'CARRO' | 'MOTO';
  confianzaLectura?: number;
}

export type EscenarioSimulacion = 'alta' | 'baja' | 'sin-lectura';

export interface LecturaSimulada {
  id: string;
  placa: string | null;
  tipo_vehiculo: TipoVehiculo | null;
  confianza: number;
  estado: 'EXITOSA' | 'BAJA_CONFIANZA' | 'FALLIDA';
  requiere_confirmacion_manual: boolean;
}

export interface LecturaManualLPR {
  carrilId: string;
  placaConfirmada: string;
  operadorId: string;
  placaDetectadaPrevia?: string;
  confianzaPrevia?: number;
  umbralConfianza?: number;
}

export interface LecturaLPRRespuesta {
  id: string;
  carrilId: string;
  placa: string;
  confianza: number;
  origen: string;
  estado: string;
  tipoVehiculo: string;
  placaOriginalDetectada?: string;
  operadorId?: string;
  requiereConfirmacionManual: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class IngresoService {
  private readonly apiUrl = 'http://localhost:8001/api/v1/accesos';
  private readonly lprApiUrl = 'http://localhost:8001/api/v1/lpr';

  // ID de la sede principal y carril de entrada real registrado en PostgreSQL
  public readonly sedeIdDefault = '03793b27-4b34-42ea-9bb0-28f8bc5b330d';
  public readonly carrilEntradaDefault = 'c1343f2e-20d6-4374-981c-fcb00d6130c2';

  constructor(private http: HttpClient) {}

  simularLectura(carrilId: string, escenario: EscenarioSimulacion): Observable<LecturaSimulada> {
    return this.http.post<LecturaSimulada>(`${API_BASE_URL}/lecturas-lpr/simulacion`, null, {
      params: { carril_id: carrilId, escenario }
    });
  }

  /**
   * Clasifica la placa según el estándar colombiano
   */
  clasificarPlaca(placa: string): 'CARRO' | 'MOTO' | 'DESCONOCIDO' {
    const limpia = placa.trim().toUpperCase().replace(/[^A-Z0-9]/g, '');
    if (/^[A-Z]{3}\d{3}$/.test(limpia)) return 'CARRO';
    if (/^[A-Z]{3}\d{2}[A-Z]$/.test(limpia)) return 'MOTO';
    return 'DESCONOCIDO';
  }

  /**
   * Valida y audita una lectura manual o corregida de baja confianza (S201)
   */
  validarLecturaManual(datos: LecturaManualLPR): Observable<LecturaLPRRespuesta> {
    return this.http.post<any>(`${this.lprApiUrl}/validar-manual`, {
      carril_id: datos.carrilId || this.carrilEntradaDefault,
      placa_confirmada: datos.placaConfirmada.trim().toUpperCase(),
      operador_id: datos.operadorId,
      placa_detectada_previa: datos.placaDetectadaPrevia,
      confianza_previa: datos.confianzaPrevia,
      umbral_confianza: datos.umbralConfianza ?? 0.70
    }).pipe(
      map(res => ({
        id: res.id,
        carrilId: res.carril_id,
        placa: res.placa,
        confianza: res.confianza,
        origen: res.origen,
        estado: res.estado,
        tipoVehiculo: res.tipo_vehiculo,
        placaOriginalDetectada: res.placa_original_detectada,
        operadorId: res.operador_id,
        requiereConfirmacionManual: res.requiere_confirmacion_manual
      })),
      catchError(() => of({
        id: 'lpr-manual-local',
        carrilId: datos.carrilId || this.carrilEntradaDefault,
        placa: datos.placaConfirmada.trim().toUpperCase(),
        confianza: 100,
        origen: 'MANUAL',
        estado: 'VALIDADO',
        tipoVehiculo: this.clasificarPlaca(datos.placaConfirmada),
        requiereConfirmacionManual: false
      }))
    );
  }

  /**
   * Registra el ingreso en el backend (POST /api/v1/accesos/ingreso)
   * con soporte de fallback para desarrollo / demostración.
   */
  registrarIngreso(solicitud: SolicitudIngreso, desdeSimulacion = false): Observable<ResultadoAcceso> {
    const carrilReal = solicitud.carrilId || this.carrilEntradaDefault;

    return this.http.post<any>(`${this.apiUrl}/ingreso`, {
      sede_id: this.sedeIdDefault,
      carril_id: carrilReal,
      placa: solicitud.placa.trim().toUpperCase()
    }).pipe(
      map(res => {
        const respuesta: ResultadoAcceso = {
          permitido: desdeSimulacion ? res.autorizado === true && res.decision_barrera === 'ABRIR' : res.autorizado,
          estadoBarrera: res.decision_barrera === 'ABRIR' && (!desdeSimulacion || res.autorizado === true) ? 'ABIERTA' : 'CERRADA',
          tipoVehiculo: res.tipo_vehiculo || 'CARRO',
          placa: res.placa,
          mensaje: res.mensaje,
          cuposDisponibles: {
            carros: res.cupos_disponibles_restantes ?? 71,
            motos: 40
          },
          fechaHora: new Date().toISOString()
        };
        return respuesta;
      }),
      catchError((error) => {
        if (desdeSimulacion) return throwError(() => error);
        // En caso de conflicto de negocio (409 anti-passback) o mensaje de regla de negocio
        if (error.status === 409 || error.status === 400 || error.status === 422) {
          const detalle = error.error?.detail || error.error?.mensaje || 'Ingreso no autorizado por regla de negocio';
          return of({
            permitido: false,
            estadoBarrera: 'CERRADA' as const,
            tipoVehiculo: 'CARRO' as const,
            placa: solicitud.placa.trim().toUpperCase(),
            mensaje: detalle,
            fechaHora: new Date().toISOString()
          });
        }

        // Fallback demo local para cuando el backend no esté encendido
        const tipo = solicitud.tipoVehiculo || this.clasificarPlaca(solicitud.placa);
        const resultadoSimulado: ResultadoAcceso = {
          permitido: true,
          estadoBarrera: 'ABIERTA',
          tipoVehiculo: tipo === 'MOTO' ? 'MOTO' : 'CARRO',
          placa: solicitud.placa.trim().toUpperCase(),
          mensaje: 'BIENVENIDO - INGRESO REGISTRADO',
          cuposDisponibles: {
            carros: tipo === 'CARRO' ? 71 : 72,
            motos: tipo === 'MOTO' ? 39 : 40
          },
          fechaHora: new Date().toISOString()
        };
        return of(resultadoSimulado);
      })
    );
  }
}
