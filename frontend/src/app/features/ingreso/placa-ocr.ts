import { clasificarPlaca, normalizarPlaca } from '../../core/models/vehiculo.model';

export const zonaLectura = { ancho: 0.72, alto: 0.32 };
export const umbralConfianzaOCR = 70;

export interface LecturaOCR {
  variante: 'original' | 'contraste y nitidez' | 'umbral';
  texto: string;
  confianza?: number;
}

export type ResultadoOCR =
  | { estado: 'valida'; placa: string; confianza: number }
  | { estado: 'sin-texto' | 'invalida' | 'ambigua' };

export function compararLecturas(lecturas: readonly LecturaOCR[]): ResultadoOCR {
  const candidatas = new Map<string, number>();
  for (const { texto, confianza } of lecturas) {
    const puntuacion = typeof confianza === 'number' && Number.isFinite(confianza)
      && confianza >= 0 && confianza <= 100 ? confianza : 0;
    for (const coincidencia of texto.toUpperCase().matchAll(
      /(?<![A-Z0-9])[A-Z]{3}[ \t-]*\d{2}[ \t-]*[A-Z0-9](?![A-Z0-9])/g,
    )) {
      const placa = normalizarPlaca(coincidencia[0]);
      if (clasificarPlaca(placa)) {
        candidatas.set(placa, Math.min(candidatas.get(placa) ?? puntuacion, puntuacion));
      }
    }
  }
  if (candidatas.size === 1) {
    const [[placa, confianza]] = candidatas;
    return { estado: 'valida', placa, confianza };
  }
  if (candidatas.size > 1) return { estado: 'ambigua' };
  return { estado: lecturas.some(lectura => lectura.texto.trim()) ? 'invalida' : 'sin-texto' };
}

function contextoCanvas(ancho: number, alto: number): CanvasRenderingContext2D {
  const canvas = document.createElement('canvas');
  canvas.width = ancho;
  canvas.height = alto;
  const contexto = canvas.getContext('2d');
  if (!contexto) throw new Error('No se pudo preparar la captura.');
  return contexto;
}

function umbralOtsu(histograma: Uint32Array, total: number, suma: number): number {
  let cantidad = 0;
  let sumaInferior = 0;
  let maximaVarianza = -1;
  let umbral = 127;
  for (let nivel = 0; nivel < histograma.length; nivel++) {
    cantidad += histograma[nivel];
    sumaInferior += nivel * histograma[nivel];
    const restante = total - cantidad;
    if (!restante) break;
    if (!cantidad) continue;
    const diferencia = sumaInferior / cantidad - (suma - sumaInferior) / restante;
    const varianza = cantidad * restante * diferencia ** 2;
    if (varianza > maximaVarianza) {
      maximaVarianza = varianza;
      umbral = nivel;
    }
  }
  return umbral;
}

export function prepararVariantes(video: HTMLVideoElement): {
  variante: LecturaOCR['variante'];
  imagen: HTMLCanvasElement;
}[] {
  const proporcionVisor = 16 / 10;
  const anchoVisible = Math.min(video.videoWidth, video.videoHeight * proporcionVisor);
  const altoVisible = Math.min(video.videoHeight, video.videoWidth / proporcionVisor);
  const ancho = Math.max(1, Math.round(anchoVisible * zonaLectura.ancho));
  const alto = Math.max(1, Math.round(altoVisible * zonaLectura.alto));
  const original = contextoCanvas(ancho, alto);
  original.drawImage(video, (video.videoWidth - ancho) / 2, (video.videoHeight - alto) / 2,
    ancho, alto, 0, 0, ancho, alto);

  const fuente = original.getImageData(0, 0, ancho, alto);
  const niveles = new Uint8Array(ancho * alto);
  const histograma = new Uint32Array(256);
  let suma = 0;
  for (let pos = 0; pos < niveles.length; pos++) {
    const offset = pos * 4;
    const gris = Math.round(0.299 * fuente.data[offset] + 0.587 * fuente.data[offset + 1]
      + 0.114 * fuente.data[offset + 2]);
    niveles[pos] = gris;
    histograma[gris]++;
    suma += gris;
  }
  const media = suma / niveles.length;
  const umbral = umbralOtsu(histograma, niveles.length, suma);
  const contraste = contextoCanvas(ancho, alto);
  const binario = contextoCanvas(ancho, alto);
  const nitida = contraste.createImageData(ancho, alto);
  const umbralizada = binario.createImageData(ancho, alto);
  for (let y = 0; y < alto; y++) {
    for (let x = 0; x < ancho; x++) {
      const i = y * ancho + x;
      const gris = niveles[i];
      const promedio = (
        niveles[x > 0 ? i - 1 : i] + niveles[x < ancho - 1 ? i + 1 : i]
        + niveles[y > 0 ? i - ancho : i] + niveles[y < alto - 1 ? i + ancho : i]
      ) / 4;
      const realce = 128 + 1.6 * (gris - media) + 0.7 * (gris - promedio);
      const blancoNegro = gris > umbral ? 255 : 0;
      const offset = i * 4;
      for (let canal = 0; canal < 3; canal++) {
        nitida.data[offset + canal] = realce;
        umbralizada.data[offset + canal] = blancoNegro;
      }
      nitida.data[offset + 3] = umbralizada.data[offset + 3] = 255;
    }
  }
  contraste.putImageData(nitida, 0, 0);
  binario.putImageData(umbralizada, 0, 0);

  return [
    { variante: 'original', imagen: original.canvas },
    { variante: 'contraste y nitidez', imagen: contraste.canvas },
    { variante: 'umbral', imagen: binario.canvas },
  ];
}
