import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PanelService, MetricasPanel, ActividadReciente, VehiculoActivo } from '../../core/services/panel.service';
import { Subscription, interval } from 'rxjs';

@Component({
  selector: 'app-panel',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="panel-header">
      <div class="header-titles">
        <h1 class="sede-title">{{ metricas?.sede_nombre || 'Sede Principal UAM' }}</h1>
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-bar bar-blue"></div>
        <span class="kpi-label">Vehículos dentro</span>
        <span class="kpi-value">{{ metricas?.vehiculos_dentro ?? 0 }}</span>
      </div>
      <div class="kpi-card">
        <div class="kpi-bar bar-cyan"></div>
        <span class="kpi-label">Cupos disponibles</span>
        <span class="kpi-value">{{ metricas?.cupos_disponibles ?? 0 }}</span>
        <span class="kpi-subdetail">
          🚗 {{ metricas?.cupos_carro_disponibles ?? 0 }} carros | 🏍️ {{ metricas?.cupos_moto_disponibles ?? 0 }} motos
        </span>
      </div>
      <div class="kpi-card">
        <div class="kpi-bar bar-amber"></div>
        <span class="kpi-label">Ingresos del día</span>
        <span class="kpi-value">{{ metricas?.ingresos_hoy ?? 0 }}</span>
      </div>
      <div class="kpi-card">
        <div class="kpi-bar bar-green"></div>
        <span class="kpi-label">Salidas del día</span>
        <span class="kpi-value">{{ metricas?.salidas_hoy ?? 0 }}</span>
      </div>
    </div>

    <div class="middle-grid">
      <div class="panel-card">
        <h2 class="panel-title">Ocupación del parqueadero</h2>
        <p class="panel-sub">
          {{ metricas?.vehiculos_dentro ?? 0 }} de {{ metricas?.total_cupos ?? 200 }} espacios ocupados
        </p>
        <div class="progress-track">
          <div
            class="progress-fill"
            [style.width.%]="metricas?.porcentaje_ocupacion ?? 0"
            [class.progress-high]="(metricas?.porcentaje_ocupacion ?? 0) >= 90"
          ></div>
        </div>
        <p class="progress-info">{{ metricas?.porcentaje_ocupacion ?? 0 }} % de ocupación</p>
      </div>

      <div class="panel-card">
        <h2 class="panel-title">Actividad reciente</h2>
        <div *ngIf="metricas?.actividad_reciente && metricas!.actividad_reciente.length > 0; else sinActividad">
          <div class="activity-row" *ngFor="let item of metricas!.actividad_reciente">
            <span>
              <span class="activity-badge" [class.badge-in]="item.tipo === 'INGRESO'" [class.badge-out]="item.tipo === 'SALIDA'">
                {{ item.tipo === 'SALIDA' ? '🔴 Salida:' : '🟢 ' + (item.tipo === 'INGRESO' ? 'Ingreso:' : 'Lectura:') }}
              </span>
              <b> {{ item.placa }}</b>
            </span>
            <span class="activity-time">{{ item.hora }}</span>
          </div>
        </div>
        <ng-template #sinActividad>
          <p class="sin-datos">No hay actividad reciente registrada hoy.</p>
        </ng-template>
      </div>
    </div>

    <div class="table-card">
      <div class="table-header-flex">
        <h2 class="panel-title">Vehículos dentro del parqueadero</h2>
        <span class="count-pill">{{ metricas?.vehiculos_activos?.length ?? 0 }} activos</span>
      </div>

      <table *ngIf="metricas?.vehiculos_activos && metricas!.vehiculos_activos.length > 0; else sinVehiculos">
        <thead>
          <tr>
            <th>Placa</th>
            <th>Tipo</th>
            <th>Ingreso</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let v of metricas!.vehiculos_activos">
            <td><b>{{ v.placa }}</b></td>
            <td>{{ v.tipo_vehiculo }}</td>
            <td>{{ v.ingreso }}</td>
            <td><span class="badge-in">Dentro</span></td>
          </tr>
        </tbody>
      </table>
      <ng-template #sinVehiculos>
        <p class="sin-datos">Actualmente no hay vehículos dentro del parqueadero.</p>
      </ng-template>
    </div>
  `,
  styles: [`
    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }
    .header-titles {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }
    .sede-title {
      font-size: 1.5rem;
      font-weight: 800;
      color: #0f172a;
      margin: 0;
    }
    .live-indicator {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.85rem;
      color: #059669;
      font-weight: 600;
    }
    .pulsing-dot {
      width: 8px;
      height: 8px;
      background-color: #10b981;
      border-radius: 50%;
      display: inline-block;
      box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
      }
      70% {
        transform: scale(1);
        box-shadow: 0 0 0 6px rgba(16, 185, 129, 0);
      }
      100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
      }
    }
    .btn-refresh {
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 0.45rem 0.9rem;
      font-size: 0.85rem;
      font-weight: 600;
      color: #334155;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-refresh:hover {
      background: #e2e8f0;
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1.5rem;
      margin-bottom: 1.75rem;
    }
    .kpi-card {
      background: #ffffff;
      padding: 1.5rem;
      border-radius: 12px;
      border: 1px solid #e2e8f0;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-label { font-size: 0.85rem; font-weight: 600; color: #64748b; }
    .kpi-value { font-size: 2rem; font-weight: 800; color: #0f172a; }
    .kpi-subdetail { font-size: 0.75rem; color: #64748b; font-weight: 500; }
    .kpi-bar { height: 4px; border-radius: 2px; width: 40px; margin-bottom: 0.25rem; }
    .bar-blue { background-color: #0284c7; }
    .bar-cyan { background-color: #06b6d4; }
    .bar-amber { background-color: #f59e0b; }
    .bar-green { background-color: #10b981; }

    .middle-grid {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 1.5rem;
      margin-bottom: 1.75rem;
    }
    .panel-card, .table-card {
      background: #ffffff;
      padding: 1.5rem;
      border-radius: 12px;
      border: 1px solid #e2e8f0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .table-header-flex {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }
    .count-pill {
      background: #f1f5f9;
      color: #475569;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 0.2rem 0.6rem;
      border-radius: 9999px;
    }
    .panel-title { font-size: 1.1rem; font-weight: 700; color: #0f172a; margin: 0; }
    .panel-sub { font-size: 0.85rem; color: #64748b; margin-top: 0.5rem; }
    .progress-track {
      background: #e2e8f0;
      height: 12px;
      border-radius: 6px;
      overflow: hidden;
      margin: 1rem 0 0.5rem 0;
    }
    .progress-fill {
      background: #0284c7;
      height: 100%;
      border-radius: 6px;
      transition: width 0.5s ease;
    }
    .progress-high {
      background: #ef4444;
    }
    .progress-info { font-size: 0.9rem; font-weight: 700; color: #0284c7; }

    .activity-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.6rem 0;
      border-bottom: 1px solid #f1f5f9;
      font-size: 0.85rem;
    }
    .activity-badge {
      font-weight: 600;
    }
    .activity-time { color: #64748b; font-size: 0.8rem; }
    .sin-datos {
      color: #94a3b8;
      font-size: 0.85rem;
      font-style: italic;
      padding: 1rem 0;
      text-align: center;
    }

    table { width: 100%; border-collapse: collapse; margin-top: 0.75rem; }
    th { text-align: left; font-size: 0.8rem; font-weight: 700; color: #64748b; padding: 0.75rem 1rem; border-bottom: 1px solid #e2e8f0; }
    td { padding: 0.85rem 1rem; font-size: 0.9rem; border-bottom: 1px solid #f1f5f9; }
    .badge-in { background: #ecfdf5; color: #059669; padding: 0.25rem 0.65rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; }
    .badge-out { background: #fef2f2; color: #dc2626; padding: 0.25rem 0.65rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; }
  `]
})
export class PanelComponent implements OnInit, OnDestroy {
  metricas: MetricasPanel | null = null;
  cargando = false;
  private refrescoSub?: Subscription;

  constructor(
    private panelService: PanelService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.cargarMetricas();
    // Auto-refresco cada 10 segundos para ver cambios en tiempo real
    this.refrescoSub = interval(10000).subscribe(() => {
      this.cargarMetricas();
    });
  }

  ngOnDestroy(): void {
    if (this.refrescoSub) {
      this.refrescoSub.unsubscribe();
    }
  }

  cargarMetricas(): void {
    this.cargando = true;
    this.panelService.obtenerResumen().subscribe({
      next: (datos) => {
        this.metricas = datos;
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar métricas del panel:', err);
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }
}
