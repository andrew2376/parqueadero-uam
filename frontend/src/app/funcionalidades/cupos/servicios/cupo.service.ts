
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timeout } from 'rxjs';

import {
  Cupo,
  ActualizarCupos,
  CuposConfiguracion
} from '../modelos/cupo.model';

@Injectable({
  providedIn: 'root'
})
export class CupoService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8001/api/v1/cupos';

  consultarPorSede(sedeId: string): Observable<Cupo[]> {
    return this.http
      .get<Cupo[]>(`${this.apiUrl}/sede/${sedeId}`)
      .pipe(timeout({ first: 10000 }));
  }

  actualizar(
    sedeId: string,
    datos: ActualizarCupos
  ): Observable<CuposConfiguracion> {
    return this.http
      .put<CuposConfiguracion>(
        `${this.apiUrl}/sede/${sedeId}`,
        datos
      )
      .pipe(timeout({ first: 10000 }));
  }
}
