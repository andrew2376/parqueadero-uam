import { HttpErrorResponse } from '@angular/common/http';
import {
  Component, DestroyRef, ElementRef, OnInit, computed, inject, signal, viewChild,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { EMPTY, Subscription, catchError, finalize, switchMap } from 'rxjs';
import type { Worker } from 'tesseract.js';
import { clasificarPlaca, normalizarPlaca } from '../../core/models/vehiculo.model';
import { CarrilActivo, Cupo, Direccion, IngresoService } from '../../core/services/ingreso.service';
import { compararLecturas, LecturaOCR, prepararVariantes, umbralConfianzaOCR, zonaLectura } from './placa-ocr';

const mensajesOCR = {
  'sin-texto': 'No se detectó texto en el recuadro. Acerca la placa o mejora la iluminación.',
  invalida: 'Se detectó texto, pero no corresponde a una placa válida. Repite la captura o escríbela.',
  ambigua: 'Se encontraron placas distintas. Verifica y escribe la placa correcta.',
};

@Component({
  selector: 'app-control-ingreso',
  standalone: true,
  templateUrl: './ingreso.html',
  styleUrl: './ingreso.css',
})
export class ControlIngresoComponent implements OnInit {
  private readonly servicio = inject(IngresoService);
  private readonly destruccion = inject(DestroyRef);
  private readonly video = viewChild.required<ElementRef<HTMLVideoElement>>('video');
  private readonly carriles = signal<CarrilActivo[]>([]);
  private consultaCupos?: Subscription;
  private flujo?: MediaStream;
  private ocr?: Worker;
  private revisionCamara = 0;
  private revisionPlaca = 0;
  private readonly requiereDigitacion = signal(false);
  private intervencionManual = true;

  readonly direccion = signal<Direccion>('ENTRADA');
  readonly sedeId = signal('');
  readonly carrilId = signal('');
  readonly placa = signal('');
  readonly registrando = signal(false);
  readonly capturando = signal(false);
  readonly zonaLectura = zonaLectura;
  readonly diagnosticoOCR = signal<readonly LecturaOCR[]>([]);
  readonly camara = signal<'apagada' | 'conectando' | 'conectada'>('apagada');
  readonly errorCamara = signal('');
  readonly errorCarriles = signal('');
  readonly errorCupos = signal('');
  readonly mensaje = signal('');
  readonly barreraAbierta = signal(false);
  readonly cupos = signal<Cupo[]>([]);
  readonly sedes = computed(() => Array.from(
    new Map(this.carriles().map(carril => [carril.sede_id, carril.nombre_sede])),
    ([id, nombre]) => ({ id, nombre }),
  ));
  readonly carrilesDisponibles = computed(() => this.carriles().filter(carril =>
    carril.sede_id === this.sedeId() && carril.activo &&
    (carril.tipo === 'MIXTO' || carril.tipo === this.direccion()),
  ));
  readonly carril = computed(() => this.carrilesDisponibles().find(c => c.id === this.carrilId()));
  readonly tipo = computed(() => clasificarPlaca(this.placa()));
  readonly puedeRegistrar = computed(() =>
    !!this.carril() && !!this.tipo() && !this.requiereDigitacion()
    && !this.registrando() && !this.capturando(),
  );

  constructor() {
    this.destruccion.onDestroy(() => {
      this.apagarCamara();
      void this.ocr?.terminate().catch(() => undefined);
      this.ocr = undefined;
    });
  }

  ngOnInit(): void {
    this.servicio.listarCarriles().pipe(takeUntilDestroyed(this.destruccion)).subscribe({
      next: carriles => {
        this.carriles.set(carriles);
        if (this.sedes().length === 1) this.seleccionarSede(this.sedes()[0].id);
        if (!carriles.length) this.errorCarriles.set('No hay carriles activos disponibles.');
      },
      error: error => this.errorCarriles.set(this.detalle(error, 'No se pudieron consultar los carriles.')),
    });
  }

  seleccionarDireccion(direccion: Direccion): void {
    if (this.registrando() || this.direccion() === direccion) return;
    const dispositivoAnterior = this.dispositivo();
    const camaraActiva = this.camara() !== 'apagada';
    this.direccion.set(direccion);
    this.elegirCarrilUnico();
    this.reiniciarResultado();
    this.errorCamara.set('');
    if (camaraActiva && (this.camara() === 'conectando' || dispositivoAnterior !== this.dispositivo())) {
      void this.activarCamara();
    }
  }

  seleccionarSede(id: string): void {
    if (this.registrando() || this.sedeId() === id) return;
    this.sedeId.set(id);
    this.elegirCarrilUnico();
    this.reiniciarResultado();
    this.cargarCupos();
  }

  seleccionarCarril(id: string): void {
    if (this.registrando() || this.carrilId() === id) return;
    this.carrilId.set(id);
    this.reiniciarResultado();
  }

  editarPlaca(placa: string): void {
    if (this.registrando()) return;
    this.intervencionManual = true;
    if (this.requiereDigitacion() && clasificarPlaca(placa)) {
      this.requiereDigitacion.set(false);
      this.errorCamara.set('');
    }
    this.placa.set(placa);
    this.reiniciarResultado();
  }

  registrar(): void {
    const carril = this.carril();
    if (!carril || !this.puedeRegistrar()) return;
    const direccion = this.direccion();
    const placa = normalizarPlaca(this.placa());
    const guardarEvidencia = direccion === 'ENTRADA' && this.intervencionManual;
    this.registrando.set(true);
    this.reiniciarResultado();
    this.servicio.registrar(direccion, carril, placa).pipe(
      switchMap(resultado => {
        this.barreraAbierta.set(resultado.abierta);
        this.mensaje.set(resultado.mensaje);
        if (!resultado.abierta) return EMPTY;
        this.cargarCupos();
        if (!guardarEvidencia) return EMPTY;
        return this.servicio.guardarLecturaManual(carril, placa).pipe(catchError(() => {
          this.mensaje.set(`${resultado.mensaje} No se pudo confirmar la evidencia manual del ingreso.`);
          return EMPTY;
        }));
      }),
      takeUntilDestroyed(this.destruccion),
      finalize(() => this.registrando.set(false)),
    ).subscribe({
      error: error => this.mensaje.set(this.detalle(error, 'No se pudo confirmar el registro con el servidor.')),
    });
  }

  aplicarLecturaOCR(lecturas: readonly LecturaOCR[]): void {
    const resultado = compararLecturas(lecturas);
    const valida = resultado.estado === 'valida';
    const bajaConfianza = valida && resultado.confianza < umbralConfianzaOCR;
    this.intervencionManual = false;
    this.requiereDigitacion.set(!valida || bajaConfianza);
    this.placa.set(valida ? resultado.placa : '');
    this.errorCamara.set(!valida ? mensajesOCR[resultado.estado] : bajaConfianza
      ? 'Lectura de baja confianza. Digita la placa que verificaste antes de registrar.'
      : '');
  }

  alternarCamara(): void {
    if (this.camara() === 'apagada') void this.activarCamara();
    else this.apagarCamara();
  }

  async capturar(): Promise<void> {
    if (this.camara() !== 'conectada' || this.capturando() || this.registrando()) return;
    const video = this.video().nativeElement;
    if (!video.videoWidth || !video.videoHeight) {
      this.errorCamara.set('Espera a que aparezca el video antes de capturar.');
      return;
    }
    this.reiniciarResultado();
    this.diagnosticoOCR.set([]);
    this.requiereDigitacion.set(true);
    const revision = this.revisionCamara;
    const revisionPlaca = this.revisionPlaca;
    const capturaVigente = () => revision === this.revisionCamara && revisionPlaca === this.revisionPlaca;
    this.capturando.set(true);
    this.errorCamara.set('');
    let worker: Worker | undefined;
    let asignado = false;
    let capturaPreparada = false;
    try {
      const variantes = prepararVariantes(video);
      capturaPreparada = true;
      const { createWorker, PSM } = await import('tesseract.js');
      if (!capturaVigente()) return;
      let rechazarOCR!: (error: unknown) => void;
      const falloOCR = new Promise<never>((_, reject) => { rechazarOCR = reject; });
      const espera = setTimeout(() => rechazarOCR(new Error('Tiempo de OCR agotado')), 45_000);
      const recursos = new URL('ocr/', document.baseURI);
      const inicio = createWorker('eng', undefined, {
        workerPath: new URL('worker.min.js', recursos).href,
        corePath: recursos.href,
        langPath: recursos.href,
        errorHandler: rechazarOCR,
      });
      try {
        worker = await Promise.race([inicio, falloOCR]);
        if (!capturaVigente()) return;
        this.ocr = worker;
        asignado = true;
        await Promise.race([worker.setParameters({
          tessedit_char_whitelist: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
          tessedit_pageseg_mode: PSM.SINGLE_LINE,
        }), falloOCR]);
        const lecturas: LecturaOCR[] = [];
        for (const { variante, imagen } of variantes) {
          const { data } = await Promise.race([worker.recognize(imagen), falloOCR]);
          if (!capturaVigente()) return;
          lecturas.push({ variante, texto: data.text, confianza: data.confidence });
          this.diagnosticoOCR.set([...lecturas]);
        }
        this.aplicarLecturaOCR(lecturas);
      } finally {
        clearTimeout(espera);
        if (!worker) void inicio.then(tardio => tardio.terminate()).catch(() => undefined);
      }
    } catch {
      if (capturaVigente()) this.errorCamara.set(capturaPreparada
        ? 'Falló el motor OCR. Puedes digitar la placa.'
        : 'No se pudo preparar la captura de la cámara. Puedes digitar la placa.');
    } finally {
      if (worker && (!asignado || this.ocr === worker)) {
        if (this.ocr === worker) this.ocr = undefined;
        await worker.terminate().catch(() => undefined);
      }
      if (!this.destruccion.destroyed) this.capturando.set(false);
    }
  }

  private dispositivo(): string | null {
    try {
      return localStorage.getItem(`uam.camara.${this.direccion().toLowerCase()}`);
    } catch {
      return null;
    }
  }

  private async activarCamara(): Promise<void> {
    this.apagarCamara();
    this.errorCamara.set('');
    if (!navigator.mediaDevices?.getUserMedia) {
      this.errorCamara.set('La cámara requiere un navegador compatible y una conexión segura.');
      return;
    }
    const revision = this.revisionCamara;
    const dispositivo = this.dispositivo();
    this.camara.set('conectando');
    try {
      const flujo = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: dispositivo ? { deviceId: { exact: dispositivo } } : { facingMode: 'environment' },
      });
      if (revision !== this.revisionCamara) {
        flujo.getTracks().forEach(pista => pista.stop());
        return;
      }
      this.flujo = flujo;
      for (const pista of flujo.getVideoTracks()) {
        pista.addEventListener('ended', () => {
          if (this.flujo !== flujo) return;
          this.apagarCamara();
          this.errorCamara.set('Se perdió la conexión con la cámara.');
        }, { once: true });
      }
      const video = this.video().nativeElement;
      video.srcObject = flujo;
      await video.play();
      if (revision === this.revisionCamara) this.camara.set('conectada');
    } catch (error) {
      if (revision !== this.revisionCamara) return;
      this.apagarCamara();
      this.errorCamara.set(error instanceof DOMException && error.name === 'NotAllowedError'
        ? 'Permite el acceso a la cámara en el navegador.'
        : 'No se pudo conectar la cámara. Comprueba que esté disponible.');
    }
  }

  private apagarCamara(): void {
    this.revisionCamara++;
    this.flujo?.getTracks().forEach(pista => pista.stop());
    this.flujo = undefined;
    this.camara.set('apagada');
    if (!this.destruccion.destroyed) this.video().nativeElement.srcObject = null;
  }

  private elegirCarrilUnico(): void {
    const carriles = this.carrilesDisponibles();
    this.carrilId.set(carriles.length === 1 ? carriles[0].id : '');
  }

  private reiniciarResultado(): void {
    this.revisionPlaca++;
    this.barreraAbierta.set(false);
    this.mensaje.set('');
  }

  private cargarCupos(): void {
    this.consultaCupos?.unsubscribe();
    this.cupos.set([]);
    this.errorCupos.set('');
    if (!this.sedeId()) return;
    this.consultaCupos = this.servicio.consultarCupos(this.sedeId()).pipe(
      takeUntilDestroyed(this.destruccion),
    ).subscribe({
      next: cupos => this.cupos.set(cupos),
      error: error => this.errorCupos.set(this.detalle(error, 'No se pudieron consultar los cupos.')),
    });
  }

  private detalle(error: unknown, alternativa: string): string {
    if (error instanceof HttpErrorResponse) {
      return typeof error.error?.detail === 'string' ? error.error.detail : alternativa;
    }
    return error instanceof Error ? error.message : alternativa;
  }
}
