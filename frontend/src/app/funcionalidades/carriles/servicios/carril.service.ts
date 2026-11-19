
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  Carril,
  CrearCarril
} from '../modelos/carril.model';

@Injectable({
  providedIn: 'root'
})
export class CarrilService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://localhost:8000/api/v1/carriles';

  listarPorSede(sedeId: string): Observable<Carril[]> {
    return this.http.get<Carril[]>(
      `${this.apiUrl}/sede/${sedeId}`
    );
  }

  obtenerPorId(carrilId: string): Observable<Carril> {
    return this.http.get<Carril>(
      `${this.apiUrl}/${carrilId}`
    );
  }

  crear(datos: CrearCarril): Observable<Carril> {
    return this.http.post<Carril>(
      this.apiUrl,
      datos
    );
  }

  actualizar(
    carrilId: string,
    datos: CrearCarril
  ): Observable<Carril> {
    return this.http.put<Carril>(
      `${this.apiUrl}/${carrilId}`,
      datos
    );
  }

  cambiarEstado(
    carrilId: string,
    activo: boolean
  ): Observable<Carril> {
    return this.http.patch<Carril>(
      `${this.apiUrl}/${carrilId}/estado`,
      { activo }
    );
  }
}
