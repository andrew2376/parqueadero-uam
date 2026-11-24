import { TipoVehiculo } from './vehiculo.model';

export type EstadoBarrera = 'ABIERTA' | 'CERRADA';
export type OrigenLectura = 'CAMARA' | 'SIMULADOR' | 'MANUAL';

export interface LecturaPlaca {
  id?: string;
  placa: string;
  confianza: number; // Porcentaje de 0 a 100
  origen: OrigenLectura;
  requiereValidacionManual: boolean;
  fechaHora: string;
}

export interface ResultadoAcceso {
  permitido: boolean;
  estadoBarrera: EstadoBarrera;
  tipoVehiculo: TipoVehiculo;
  placa: string;
  mensaje: string; // "BIENVENIDO", "LLENO", "COBRO_PENDIENTE", "PASE_VIGENTE"
  cobroGenerado?: {
    id: string;
    valor: number;
    franja: 'DIURNA' | 'NOCTURNA';
  };
  cuposDisponibles?: {
    carros: number;
    motos: number;
  };
  fechaHora: string;
}
