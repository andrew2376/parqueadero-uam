
export type TipoVehiculoTarifa = 'CARRO' | 'MOTO';

export interface Tarifa {
  id: string;
  sede_id: string;
  tipo_vehiculo: TipoVehiculoTarifa;
  version: number;
  tarifa_diurna: number;
  tarifa_nocturna: number;
  vigencia_desde: string;
  vigencia_hasta: string | null;
  activa: boolean;
}

export interface CrearTarifa {
  sede_id: string;
  tipo_vehiculo: TipoVehiculoTarifa;
  tarifa_diurna: number;
  tarifa_nocturna: number;
  vigencia_desde?: string | null;
}

export interface CerrarVigenciaTarifa {
  vigencia_hasta: string;
}

export interface TarifaCalculo {
  sede_id: string;
  tarifa_id: string;
  version_tarifa: number;
  tipo_vehiculo: TipoVehiculoTarifa;
  franja_horaria: string;
  tarifa_aplicada: string;
  valor_tarifa: number;
  fecha_hora: string;
}
