import { compararLecturas, LecturaOCR } from './placa-ocr';

function lecturas(original: string, nitida = '', umbral = ''): LecturaOCR[] {
  return [
    { variante: 'original', texto: original },
    { variante: 'contraste y nitidez', texto: nitida },
    { variante: 'umbral', texto: umbral },
  ];
}

describe('Comparación de lecturas OCR', () => {
  it('propone una placa de carro que solo se distingue en una variante', () => {
    expect(compararLecturas(lecturas('', 'abc-123\n', ''))).toEqual({
      estado: 'valida', placa: 'ABC123', confianza: 0,
    });
  });

  it('conserva la confianza menor para una candidata de moto repetida', () => {
    const variantes = lecturas('ABC12D', 'ABC12D');
    variantes[0].confianza = 95;
    variantes[1].confianza = 60;
    expect(compararLecturas(variantes)).toEqual({
      estado: 'valida', placa: 'ABC12D', confianza: 60,
    });
  });

  it('distingue ausencia de texto', () => {
    expect(compararLecturas(lecturas('\n', '\t', ' '))).toEqual({ estado: 'sin-texto' });
  });

  it('rechaza texto inválido sin convertir letras en números', () => {
    expect(compararLecturas(lecturas('ABCO23', 'XABC123X', 'AB1 123'))).toEqual({ estado: 'invalida' });
  });

  it('no sugiere una placa si las variantes discrepan, aunque dos coincidan', () => {
    expect(compararLecturas(lecturas('ABC123', 'ABC123', 'ABC12D'))).toEqual({ estado: 'ambigua' });
  });
});
