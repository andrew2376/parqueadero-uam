
export type TipoCarril = 'ENTRADA' | 'SALIDA';

export interface Carril {
  id: string;
  sede_id: string;
  nombre: string;
  tipo: TipoCarril;
  activo: boolean;
}

export interface CrearCarril {
  sede_id: string;
  nombre: string;
  tipo: TipoCarril;
}
