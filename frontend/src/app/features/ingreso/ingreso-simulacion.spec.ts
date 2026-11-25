import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { API_BASE_URL } from '../../core/api.config';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { LecturaSimulada } from '../../core/services/ingreso.service';
import { ControlIngresoComponent } from './ingreso';

describe('Camaras LPR del carril mixto', () => {
  let fixture: ComponentFixture<ControlIngresoComponent>;
  let http: HttpTestingController;
  const carril = '12345678-1234-1234-1234-123456789abc';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ControlIngresoComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: ActivatedRoute, useValue: { snapshot: { queryParamMap: convertToParamMap({ carril }) } } },
        { provide: AuthService, useValue: { usuarioActual: { id: 'operador', rol: 'OPERADOR' } } }
      ]
    });
    fixture = TestBed.createComponent(ControlIngresoComponent);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(`${API_BASE_URL}/carriles/${carril}`).flush({
      id: carril, sede_id: 'sede', activo: true, tipo: 'MIXTO', nombre: 'Mixto'
    });
    fixture.detectChanges();
  });

  afterEach(() => http.verify());

  function capturar(escenario: string) {
    const selector: HTMLSelectElement = fixture.nativeElement.querySelector('#escenario-lpr');
    selector.value = escenario;
    selector.dispatchEvent(new Event('change'));
    fixture.nativeElement.querySelector('.btn-simulate').click();
    const solicitud = http.expectOne(req => req.url === `${API_BASE_URL}/lecturas-lpr/simulacion`);
    expect(solicitud.request.method).toBe('POST');
    expect(solicitud.request.params.get('escenario')).toBe(escenario);
    expect(solicitud.request.params.get('carril_id')).toBe(carril);
    return solicitud;
  }

  const casos: Array<[string, Omit<LecturaSimulada, 'id' | 'direccion'>, string]> = [
    ['alta', { placa: 'ABC123', tipo_vehiculo: 'CARRO', estado: 'EXITOSA',
      confianza: 95, requiere_confirmacion_manual: false }, 'Automóvil'],
    ['baja', { placa: 'DEF45A', tipo_vehiculo: 'MOTO', estado: 'BAJA_CONFIANZA',
      confianza: 55, requiere_confirmacion_manual: true }, 'Motocicleta'],
    ['sin-lectura', { placa: null, tipo_vehiculo: null, estado: 'FALLIDA',
      confianza: 0, requiere_confirmacion_manual: true }, '']
  ];

  it.each(casos)('muestra la captura %s sin solicitar un ingreso', (escenario, lectura, tipo) => {
    capturar(escenario).flush({ id: 'evento', direccion: 'ENTRADA', ...lectura });
    fixture.detectChanges();
    const componente = fixture.componentInstance;
    expect(componente.ingresoForm.get('placa')?.value).toBe(lectura.placa ?? '');
    expect(componente.ingresoForm.get('tipoVehiculoTexto')?.value).toBe(tipo);
    expect(componente.lectura?.confianza).toBe(lectura.confianza);
    expect(componente.lectura?.requiere_confirmacion_manual).toBe(lectura.requiere_confirmacion_manual);
    expect(componente.resultadoIngreso).toBeNull();
    if (lectura.placa === null) {
      expect(fixture.nativeElement.querySelector('.status-banner').textContent).toContain('Sin lectura');
    }
    http.expectNone(req => req.url.endsWith('/accesos/ingreso'));
  });

  it('descarta la lectura anterior y presenta el fallo sin autorizar un ingreso', () => {
    capturar('alta').flush({ id: 'evento', direccion: 'ENTRADA', ...casos[0][1] });
    capturar('alta').flush(null, { status: 503, statusText: 'Service Unavailable' });
    fixture.componentInstance.onRegistrarIngreso();
    fixture.detectChanges();
    expect(fixture.componentInstance.lectura).toBeNull()
    expect(fixture.componentInstance.resultadoIngreso).toBeNull();
    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain('servidor');
    http.expectNone(req => req.url.endsWith('/accesos/ingreso'));
  });

  it('mantiene cerrada la barrera si falla un ingreso solicitado tras la captura', () => {
    capturar('alta').flush({ id: 'evento', direccion: 'ENTRADA', ...casos[0][1] });
    fixture.componentInstance.onRegistrarIngreso();
    http.expectOne(`${API_BASE_URL}/accesos/ingreso`).flush(null, {
      status: 503, statusText: 'Service Unavailable'
    });
    fixture.detectChanges();
    expect(fixture.componentInstance.resultadoIngreso).toBeNull();
    expect(fixture.nativeElement.querySelector('.barrier-result-box').textContent).toContain('BARRERA CERRADA');
  });
  it('confirma la placa de salida antes de solicitar la decision real', () => {
    fixture.componentInstance.seleccionarCamara('SALIDA');
    const captura = capturar('baja');
    expect(captura.request.params.get('direccion')).toBe('SALIDA');
    captura.flush({ id: 'evento', direccion: 'SALIDA', ...casos[1][1] });
    fixture.componentInstance.onRegistrarIngreso();
    const manual = http.expectOne(`${API_BASE_URL}/lecturas-lpr/manual`);
    http.expectNone(`${API_BASE_URL}/estancias/salida`);
    manual.flush({ placa: 'DEF45A', estado: 'EXITOSA' });
    http.expectOne(`${API_BASE_URL}/estancias/salida`).flush({
      autorizado: false, decision_barrera: 'DENEGAR', motivo: 'Pago pendiente'
    });
    expect(fixture.componentInstance.resultadoIngreso).toEqual({
      permitido: false, estadoBarrera: 'CERRADA', mensaje: 'Pago pendiente'
    });
  });
  it('habilita la digitacion con el carril validado y detiene el ingreso si falla la confirmacion', () => {
    expect(fixture.nativeElement.querySelector('#carril-lpr').value).toBe(carril);
    expect(fixture.nativeElement.querySelector('#estado-carril').textContent).toContain('activo y verificado');
    const placa: HTMLInputElement = fixture.nativeElement.querySelector('#placa');
    expect(placa.readOnly).toBe(false);
    placa.value = 'abc-123';
    placa.dispatchEvent(new Event('input'));
    fixture.componentInstance.onRegistrarIngreso();
    const manual = http.expectOne(`${API_BASE_URL}/lecturas-lpr/manual`);
    expect(manual.request.body).toEqual({ carril_id: carril, placa: 'abc-123' });
    manual.flush({ detail: 'Placa invalida' }, { status: 422, statusText: 'Unprocessable Content' });
    http.expectNone(`${API_BASE_URL}/accesos/ingreso`);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain('Placa invalida');
    expect(fixture.nativeElement.querySelector('.barrier-result-box').textContent).toContain('BARRERA CERRADA');
  });

  it('informa cuando el carril no existe y bloquea los controles de captura', () => {
    fixture.componentInstance.cargarCarril();
    http.expectOne(`${API_BASE_URL}/carriles/${carril}`).flush(
      null, { status: 404, statusText: 'Not Found' }
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('#estado-carril').textContent).toContain('no existe');
    expect(fixture.nativeElement.querySelector('.btn-simulate').disabled).toBe(true);
    expect(fixture.nativeElement.querySelector('#placa').readOnly).toBe(true);
  });
});
