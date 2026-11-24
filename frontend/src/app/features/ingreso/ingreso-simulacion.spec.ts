import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { API_BASE_URL } from '../../core/api.config';
import { AuthService } from '../../core/services/auth.service';
import { IngresoService, LecturaSimulada } from '../../core/services/ingreso.service';
import { ControlIngresoComponent } from './ingreso';

describe('Simulador LPR de entrada', () => {
  let fixture: ComponentFixture<ControlIngresoComponent>;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ControlIngresoComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: { usuarioActual: null } }
      ]
    });
    fixture = TestBed.createComponent(ControlIngresoComponent);
    http = TestBed.inject(HttpTestingController);
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
    expect(solicitud.request.params.get('carril_id')).toBe(TestBed.inject(IngresoService).carrilEntradaDefault);
    return solicitud;
  }

  const casos: Array<[string, Omit<LecturaSimulada, 'id'>, string]> = [
    ['alta', { placa: 'ABC123', tipo_vehiculo: 'CARRO', estado: 'EXITOSA',
      confianza: 95, requiere_confirmacion_manual: false }, 'Automóvil'],
    ['baja', { placa: 'DEF45A', tipo_vehiculo: 'MOTO', estado: 'BAJA_CONFIANZA',
      confianza: 55, requiere_confirmacion_manual: true }, 'Motocicleta'],
    ['sin-lectura', { placa: null, tipo_vehiculo: null, estado: 'FALLIDA',
      confianza: 0, requiere_confirmacion_manual: true }, 'Desconocido']
  ];

  it.each(casos)('muestra la captura %s sin solicitar un ingreso', (escenario, lectura, tipo) => {
    capturar(escenario).flush({ id: 'evento', ...lectura });
    fixture.detectChanges();
    const componente = fixture.componentInstance;
    expect(componente.ingresoForm.get('placa')?.value).toBe(lectura.placa ?? '');
    expect(componente.ingresoForm.get('tipoVehiculoTexto')?.value).toBe(tipo);
    expect(componente.confianzaActual).toBe(lectura.confianza);
    expect(componente.esBajaConfianza).toBe(lectura.requiere_confirmacion_manual);
    expect(componente.resultadoIngreso).toBeNull();
    if (lectura.placa === null) {
      expect(fixture.nativeElement.querySelector('[role="status"]').textContent).toContain('detectó');
    }
    http.expectNone(req => req.url.endsWith('/accesos/ingreso'));
  });

  it('descarta la lectura anterior y presenta el fallo sin autorizar un ingreso', () => {
    capturar('alta').flush({ id: 'evento', ...casos[0][1] });
    capturar('alta').flush(null, { status: 503, statusText: 'Service Unavailable' });
    fixture.componentInstance.onRegistrarIngreso();
    fixture.detectChanges();
    expect(fixture.componentInstance.placaActual).toBe('');
    expect(fixture.componentInstance.resultadoIngreso).toBeNull();
    expect(fixture.nativeElement.querySelector('[role="status"]').textContent).toContain('servidor');
    http.expectNone(req => req.url.endsWith('/accesos/ingreso'));
  });

  it('mantiene cerrada la barrera si falla un ingreso solicitado tras la captura', () => {
    capturar('alta').flush({ id: 'evento', ...casos[0][1] });
    fixture.componentInstance.onRegistrarIngreso();
    http.expectOne(`${API_BASE_URL}/accesos/ingreso`).flush(null, {
      status: 503, statusText: 'Service Unavailable'
    });
    expect(fixture.componentInstance.resultadoIngreso?.estadoBarrera).toBe('CERRADA');
  });
});
