# Frontend — Sistema de Parqueadero con Reconocimiento de Placas (LPR)

Aplicación web desarrollada en **Angular 21 + TypeScript** para la gestión operativa y administrativa del sistema de parqueadero UAM.

---

## 1. Requisitos previos

- **Node.js**: v20 o superior (recomendado v24+)
- **npm**: v10 o superior
- **Angular CLI**: v21 (opcional globalmente, ejecutable mediante `npx ng` o scripts npm)

---

## 2. Instalación de dependencias

Desde la raíz de la carpeta `frontend/`, ejecutar:

```bash
npm install
```

---

## 3. Servidor de desarrollo local

Para levantar el servidor de desarrollo:

```bash
npm start
# O directamente:
ng serve
```

La aplicación quedará disponible en:
👉 `http://localhost:4200/`

El servidor se recargará automáticamente ante cualquier cambio realizado en el código fuente.

---

## 4. Compilación (Build)

Para generar los archivos de producción optimizados:

```bash
npm run build
```

Los artefactos compilados se almacenan en el directorio `dist/`.

---

## 5. Pruebas unitarias

Para ejecutar la suite de pruebas unitarias:

```bash
npm test
```

---

## 6. Estructura del proyecto

La arquitectura del frontend sigue el enfoque modular por funcionalidades (*feature-based*):

- `src/app/core/`: Servicios transversales, interceptores HTTP, guards de autenticación y modelos de datos.
- `src/app/shared/`: Componentes reutilizables (indicador visual de barrera, badges de vehículos, alertas).
- `src/app/features/` (o `funcionalidades/`): Módulos funcionales de la aplicación:
  - `auth/`: Inicio de sesión y control de acceso por roles (Operador / Administrador).
  - `carril/`: Panel de carril con lectura simulada, confianza y control de barrera.
  - `caja/`: Búsqueda de vehículos y cobro/pago en efectivo.
  - `tarifas/`: Configuración y versionamiento de tarifas diurnas/nocturnas.
  - `cupos/`: Monitoreo y ajuste de cupos por tipo de vehículo.
  - `eventos/`: Consulta y reportes de entradas, salidas y cobros con filtros.
