
export type TipoVehiculoCupo = 'CARRO' | 'MOTO';

export interface Cupo {
  sede_id: string;
  tipo_vehiculo: TipoVehiculoCupo;
  capacidad: number;
  ocupados: number;
  disponibles: number;
}

export interface ActualizarCupos {
  cupos_carro: number;
  cupos_moto: number;
}

export interface CuposConfiguracion {
  sede_id: string;
  cupos_carro: number;
  cupos_moto: number;
}
