export type TipoVehiculo = 'CARRO' | 'MOTO';

export interface Vehiculo {
  placa: string;
  tipo: TipoVehiculo;
}

/**
 * Validador y clasificador utilitario de placas colombianas (F-02).
 * - Carro: 3 letras + 3 dígitos (ej: AAA123)
 * - Moto: 3 letras + 2 dígitos + 1 letra (ej: AAA12A)
 */
export function clasificarPlaca(placaRaw: string): TipoVehiculo | null {
  const placa = (placaRaw || '').trim().toUpperCase().replace(/[^A-Z0-9]/g, '');
  if (/^[A-Z]{3}\d{3}$/.test(placa)) {
    return 'CARRO';
  }
  if (/^[A-Z]{3}\d{2}[A-Z]$/.test(placa)) {
    return 'MOTO';
  }
  return null;
}

export function normalizarPlaca(placaRaw: string): string {
  return (placaRaw || '').trim().toUpperCase().replace(/[^A-Z0-9]/g, '');
}
