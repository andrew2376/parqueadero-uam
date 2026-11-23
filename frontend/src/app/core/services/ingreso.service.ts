import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { LecturaPlaca, ResultadoAcceso } from '../models/acceso.model';

export interface SolicitudIngreso {
  carrilId: string;
  placa: string;
  tipoVehiculo?: 'CARRO' | 'MOTO';
  confianzaLectura?: number;
}

export interface PlacaSimulada {
  placa: string;
  tipo: 'CARRO' | 'MOTO';
  confianza: number;
}

@Injectable({
  providedIn: 'root'
})
export class IngresoService {
  private readonly apiUrl = 'http://localhost:8001/api/v1/accesos';

  // Catálogo de placas demo para la simulación LPR académica
  private readonly catalogoDemo: PlacaSimulada[] = [
    { placa: 'ABC123', tipo: 'CARRO', confianza: 96 },
    { placa: 'KLR65A', tipo: 'MOTO', confianza: 94 },
    { placa: 'XYZ789', tipo: 'CARRO', confianza: 98 },
    { placa: 'UAM001', tipo: 'CARRO', confianza: 99 },
    { placa: 'MTO45B', tipo: 'MOTO', confianza: 88 },
    { placa: 'DEF456', tipo: 'CARRO', confianza: 62 } // Lectura de baja confianza (<70%)
  ];

  private indiceDemo = 0;

  constructor(private http: HttpClient) {}

  /**
   * Simula la lectura automática de la cámara LPR
   */
  simularLectura(): PlacaSimulada {
    const item = this.catalogoDemo[this.indiceDemo % this.catalogoDemo.length];
    this.indiceDemo++;
    return { ...item };
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
   * Registra el ingreso en el backend (POST /api/v1/accesos/ingreso)
   * con soporte de fallback para desarrollo / demostración.
   */
  registrarIngreso(solicitud: SolicitudIngreso): Observable<ResultadoAcceso> {
    const sedeDefault = '03793b27-4b34-42ea-9bb0-28f8bc5b330d';
    const carrilDefault = 'a0000000-0000-0000-0000-000000000001';

    return this.http.post<any>(`${this.apiUrl}/ingreso`, {
      sede_id: sedeDefault,
      carril_id: carrilDefault,
      placa: solicitud.placa.trim().toUpperCase()
    }).pipe(
      map(res => {
        const respuesta: ResultadoAcceso = {
          permitido: res.autorizado,
          estadoBarrera: res.decision_barrera === 'ABRIR' ? 'ABIERTA' : 'CERRADA',
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
        // En caso de conflicto de negocio (409 anti-passback) o error de backend
        if (error.status === 409 || error.status === 400) {
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
