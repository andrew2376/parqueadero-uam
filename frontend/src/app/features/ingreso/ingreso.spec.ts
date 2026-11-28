import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { API_BASE_URL } from '../../core/api.config';
import { ControlIngresoComponent } from './ingreso';

describe('Control de acceso', () => {
  let http: HttpTestingController;
  let pantalla: ControlIngresoComponent;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ControlIngresoComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    http = TestBed.inject(HttpTestingController);
    const fixture = TestBed.createComponent(ControlIngresoComponent);
    pantalla = fixture.componentInstance;
    fixture.detectChanges();
    http.expectOne(`${API_BASE_URL}/panel/resumen`).flush({ sede_id: 'sede', sede_nombre: 'UAM' });
    http.expectOne(`${API_BASE_URL}/carriles/sede/sede`).flush([
      { id: 'entrada', sede_id: 'sede', nombre_sede: 'UAM', nombre: 'Portería entrada', tipo: 'ENTRADA', activo: true },
      { id: 'salida', sede_id: 'sede', nombre_sede: 'UAM', nombre: 'Portería salida', tipo: 'SALIDA', activo: true },
    ]);
    http.expectOne(`${API_BASE_URL}/cupos/sede/sede`).flush([{ tipo_vehiculo: 'CARRO', disponibles: 3 }]);
    expect(pantalla.sedes()).toEqual([{ id: 'sede', nombre: 'UAM' }]);
  });

  afterEach(() => http.verify());

  const urlEvidencia = `${API_BASE_URL}/lecturas-lpr/manual`;

  function confirmarIngreso() {
    const registro = http.expectOne({ method: 'POST', url: `${API_BASE_URL}/accesos/ingreso` });
    registro.flush({ autorizado: true, decision_barrera: 'ABRIR', mensaje: 'Ingreso autorizado.' });
    http.expectOne(`${API_BASE_URL}/cupos/sede/sede`).flush([{ tipo_vehiculo: 'CARRO', disponibles: 2 }]);
    return registro;
  }

  function confirmarEvidencia(placa: string) {
    const evidencia = http.expectOne({ method: 'POST', url: urlEvidencia });
    expect(evidencia.request.body).toEqual({ carril_id: 'entrada', placa });
    evidencia.flush({ sede_id: 'sede', carril_id: 'entrada', placa, origen: 'MANUAL' });
  }

  it('registra una placa manual sin cámara, sin casilla y sin doble envío', () => {
    expect(pantalla.camara()).toBe('apagada');
    pantalla.editarPlaca('inválida');
    pantalla.registrar();
    http.expectNone(`${API_BASE_URL}/accesos/ingreso`);
    pantalla.editarPlaca('abc-123');

    pantalla.registrar();
    pantalla.registrar();
    const registro = http.expectOne({ method: 'POST', url: `${API_BASE_URL}/accesos/ingreso` });
    expect(registro.request.body).toEqual({ sede_id: 'sede', carril_id: 'entrada', placa: 'ABC123' });
    registro.flush({ autorizado: true, decision_barrera: 'ABRIR', mensaje: 'Ingreso autorizado.' });
    http.expectOne(`${API_BASE_URL}/cupos/sede/sede`).flush([{ tipo_vehiculo: 'CARRO', disponibles: 2 }]);
    pantalla.registrar();
    http.expectNone(`${API_BASE_URL}/accesos/ingreso`);
    confirmarEvidencia('ABC123');
    expect(pantalla.barreraAbierta()).toBe(true);
    expect(pantalla.cupos()[0].disponibles).toBe(2);
  });

  it('requiere pulsar Registrar con una lectura confiable y omite evidencia si no hubo edición', () => {
    pantalla.aplicarLecturaOCR([{ variante: 'original', texto: 'ABC123', confianza: 70 }]);
    expect(pantalla.puedeRegistrar()).toBe(true);
    http.expectNone(`${API_BASE_URL}/accesos/ingreso`);
    pantalla.registrar();
    confirmarIngreso();
    http.expectNone(urlEvidencia);
  });

  it('bloquea lectura bajo el umbral hasta digitar, aunque coincida con la propuesta', () => {
    pantalla.aplicarLecturaOCR([{ variante: 'original', texto: 'ABC123', confianza: 69 }]);
    expect(pantalla.puedeRegistrar()).toBe(false);
    pantalla.registrar();
    http.expectNone(`${API_BASE_URL}/accesos/ingreso`);
    pantalla.editarPlaca('ABC123');
    pantalla.registrar();
    confirmarIngreso();
    confirmarEvidencia('ABC123');
  });

  it('exige digitación ante ambigüedad y registra solo la placa elegida', () => {
    pantalla.aplicarLecturaOCR([
      { variante: 'original', texto: 'ABC123', confianza: 95 },
      { variante: 'umbral', texto: 'ABC128', confianza: 93 },
    ]);
    expect(pantalla.placa()).toBe('');
    expect(pantalla.puedeRegistrar()).toBe(false);
    pantalla.editarPlaca('ABC128');
    pantalla.registrar();
    expect(confirmarIngreso().request.body.placa).toBe('ABC128');
    confirmarEvidencia('ABC128');
  });

  it('guarda evidencia si el operador corrige incluso una lectura confiable', () => {
    pantalla.aplicarLecturaOCR([{ variante: 'original', texto: 'ABO123', confianza: 91 }]);
    pantalla.editarPlaca('ABC123');
    pantalla.registrar();
    expect(confirmarIngreso().request.body.placa).toBe('ABC123');
    confirmarEvidencia('ABC123');
  });

  it('conserva el ingreso confirmado si la evidencia falla y no reintenta', () => {
    pantalla.editarPlaca('ABC123');
    pantalla.registrar();
    confirmarIngreso();
    http.expectOne(urlEvidencia).flush(null, { status: 500, statusText: 'Error' });
    http.expectNone(urlEvidencia);
    http.expectNone(`${API_BASE_URL}/accesos/ingreso`);
    expect(pantalla.barreraAbierta()).toBe(true);
    expect(pantalla.mensaje()).toBe('Ingreso autorizado. No se pudo confirmar la evidencia manual del ingreso.');
  });

  it('avisa si la sede devuelta en la evidencia difiere de la sede del ingreso', () => {
    pantalla.editarPlaca('ABC123');
    pantalla.registrar();
    confirmarIngreso();
    http.expectOne(urlEvidencia).flush({
      sede_id: 'otra-sede', carril_id: 'entrada', placa: 'ABC123', origen: 'MANUAL',
    });
    expect(pantalla.mensaje()).toContain('No se pudo confirmar la evidencia manual');
  });

  it('usa la placa editada y el endpoint de salida al cambiar de dirección', () => {
    pantalla.editarPlaca('ABC12D');
    pantalla.seleccionarDireccion('SALIDA');
    expect(pantalla.tipo()).toBe('MOTO');
    pantalla.editarPlaca('ABC12E');
    pantalla.registrar();
    http.expectOne(`${API_BASE_URL}/carriles/salida`)
      .flush({ id: 'salida', sede_id: 'sede', tipo: 'SALIDA', activo: true });
    const registro = http.expectOne({ method: 'POST', url: `${API_BASE_URL}/estancias/salida` });
    expect(registro.request.body).toEqual({ sede_id: 'sede', placa: 'ABC12E' });
    registro.flush({ autorizado: false, decision_barrera: 'DENEGAR', motivo: 'Pago pendiente.' });
    expect(pantalla.barreraAbierta()).toBe(false);
    expect(pantalla.mensaje()).toBe('Pago pendiente.');
    http.expectNone(urlEvidencia);
  });

  it('bloquea la salida si el carril ya no está activo', () => {
    pantalla.seleccionarDireccion('SALIDA');
    pantalla.editarPlaca('ABC123');
    pantalla.registrar();
    http.expectOne(`${API_BASE_URL}/carriles/salida`)
      .flush({ id: 'salida', sede_id: 'sede', tipo: 'SALIDA', activo: false });
    http.expectNone(`${API_BASE_URL}/estancias/salida`);
    expect(pantalla.barreraAbierta()).toBe(false);
    expect(pantalla.mensaje()).toContain('ya no está habilitado');
  });

  it('deja la barrera cerrada y muestra el error real si falla el registro', () => {
    pantalla.editarPlaca('ABC123');
    pantalla.registrar();
    http.expectOne(`${API_BASE_URL}/accesos/ingreso`)
      .flush({ detail: 'Carril inactivo.' }, { status: 422, statusText: 'Unprocessable Content' });
    expect(pantalla.barreraAbierta()).toBe(false);
    expect(pantalla.mensaje()).toBe('Carril inactivo.');
    http.expectNone(urlEvidencia);
  });

  it('mantiene cerrada la barrera ante una respuesta inconsistente', () => {
    pantalla.editarPlaca('ABC123');
    pantalla.registrar();
    http.expectOne(`${API_BASE_URL}/accesos/ingreso`)
      .flush({ autorizado: true, decision_barrera: 'MANTENER_CERRADA', mensaje: 'Acceso bloqueado.' });
    expect(pantalla.barreraAbierta()).toBe(false);
    http.expectNone(urlEvidencia);
  });
});
