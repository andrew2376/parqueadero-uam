import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-panel',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-bar bar-blue"></div>
        <span class="kpi-label">Vehículos dentro</span>
        <span class="kpi-value">128</span>
      </div>
      <div class="kpi-card">
        <div class="kpi-bar bar-cyan"></div>
        <span class="kpi-label">Cupos disponibles</span>
        <span class="kpi-value">72</span>
      </div>
      <div class="kpi-card">
        <div class="kpi-bar bar-amber"></div>
        <span class="kpi-label">Ingresos del día</span>
        <span class="kpi-value">186</span>
      </div>
      <div class="kpi-card">
        <div class="kpi-bar bar-green"></div>
        <span class="kpi-label">Salidas del día</span>
        <span class="kpi-value">58</span>
      </div>
    </div>

    <div class="middle-grid">
      <div class="panel-card">
        <h2 class="panel-title">Ocupación del parqueadero</h2>
        <p class="panel-sub">128 de 200 espacios ocupados</p>
        <div class="progress-track">
          <div class="progress-fill"></div>
        </div>
        <p class="progress-info">64 % de ocupación</p>
      </div>

      <div class="panel-card">
        <h2 class="panel-title">Actividad reciente</h2>
        <div class="activity-row">
          <span>🟢 Ingreso: <b>ABC123</b></span>
          <span class="activity-time">10:42</span>
        </div>
        <div class="activity-row">
          <span>🔴 Salida: <b>XYZ789</b></span>
          <span class="activity-time">10:38</span>
        </div>
        <div class="activity-row">
          <span>🟢 Ingreso: <b>MOT456</b></span>
          <span class="activity-time">10:15</span>
        </div>
      </div>
    </div>

    <div class="table-card">
      <h2 class="panel-title">Vehículos dentro del parqueadero</h2>
      <table>
        <thead>
          <tr>
            <th>Placa</th>
            <th>Tipo</th>
            <th>Ingreso</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><b>ABC123</b></td>
            <td>Automóvil</td>
            <td>10:42</td>
            <td><span class="badge-in">Dentro</span></td>
          </tr>
          <tr>
            <td><b>MOT456</b></td>
            <td>Motocicleta</td>
            <td>10:15</td>
            <td><span class="badge-in">Dentro</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  `,
  styles: [`
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
    .panel-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.75rem; color: #0f172a; }
    .panel-sub { font-size: 0.85rem; color: #64748b; }
    .progress-track {
      background: #e2e8f0;
      height: 12px;
      border-radius: 6px;
      overflow: hidden;
      margin: 1rem 0 0.5rem 0;
    }
    .progress-fill { background: #0284c7; height: 100%; width: 64%; border-radius: 6px; }
    .progress-info { font-size: 0.9rem; font-weight: 700; color: #0284c7; }

    .activity-row {
      display: flex;
      justify-content: space-between;
      padding: 0.6rem 0;
      border-bottom: 1px solid #f1f5f9;
      font-size: 0.85rem;
    }
    .activity-time { color: #64748b; }

    table { width: 100%; border-collapse: collapse; margin-top: 0.75rem; }
    th { text-align: left; font-size: 0.8rem; font-weight: 700; color: #64748b; padding: 0.75rem 1rem; border-bottom: 1px solid #e2e8f0; }
    td { padding: 0.85rem 1rem; font-size: 0.9rem; border-bottom: 1px solid #f1f5f9; }
    .badge-in { background: #ecfdf5; color: #059669; padding: 0.25rem 0.65rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; }
  `]
})
export class PanelComponent {}
