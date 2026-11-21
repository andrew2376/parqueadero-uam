# P08 — Contrato de API REST y Manejo de Errores

## 1. Objetivo y Alcance

Este documento establece el contrato oficial de comunicación HTTP/REST entre el frontend (Angular) y el backend (FastAPI) para el **Sistema de Parqueadero con Reconocimiento de Placas (LPR)** de la Universidad Autónoma de Manizales (UAM).

Define estándares de diseño, convenciones de rutas, formatos de intercambio JSON, códigos de respuesta HTTP, estructura uniforme de errores, autenticación, paginación y manejo de zona horaria.

---

## 2. Convenciones Generales

### 2.1 Protocolo y Prefijo
- Toda la API REST se expone bajo el prefijo:
  ```text
  /api/v1
  ```
- Formato de intercambio de datos: `application/json` con codificación UTF-8.
- Nombres de atributos en cuerpos JSON: **`camelCase`** o **`snake_case`** mapeados consistentemente por esquemas Pydantic/TypeScript. En el frontend se prefiere `camelCase` o `snake_case` transparente según modelos del módulo.

### 2.2 Zona Horaria y Fechas
- **Zona horaria estándar:** `America/Bogota` (UTC-5).
- **Formato ISO-8601:** Todas las fechas y horas transmitidas en los payloads deben seguir el estándar ISO:
  ```text
  YYYY-MM-DDTHH:mm:ss.sssZ  o  YYYY-MM-DDTHH:mm:ss-05:00
  ```
- **Día Operativo (RN-03):** Se computa desde las 06:00:00 hasta las 05:59:59 del día siguiente en hora local de Colombia.

---

## 3. Códigos de Estado HTTP Estándar

| Código | Significado | Cuándo se utiliza |
| :--- | :--- | :--- |
| **`200 OK`** | Éxito | Consultas exitosas (GET), actualizaciones completas (PUT) o parciales (PATCH). |
| **`201 Created`** | Creado | Creación exitosa de recursos (POST), devuelve el objeto creado o identificador. |
| **`204 No Content`** | Sin contenido | Eliminación exitosa (DELETE) o acciones que no retornan cuerpo. |
| **`400 Bad Request`** | Solicitud incorrecta | Error de lógica de negocio (placa inválida, tarifa nocturna mayor que diurna, etc.). |
| **`401 Unauthorized`** | No autenticado | Token ausente, expirado o credenciales de inicio de sesión inválidas. |
| **`403 Forbidden`** | No autorizado | El usuario autenticado carece de permisos para la acción (ej. operador intentando cambiar tarifas). |
| **`404 Not Found`** | No encontrado | El recurso solicitado por ID o placa no existe en el sistema. |
| **`409 Conflict`** | Conflicto | Registro duplicado o violación de unicidad (ej. vehículo ya ingresado, sede duplicada). |
| **`422 Unprocessable Entity`** | Error de validación | Tipos de datos inválidos en el esquema Pydantic (ej. UUID mal formado, campo requerido faltante). |
| **`500 Internal Server Error`** | Error interno | Error no controlado del servidor (falla de base de datos o excepción no atrapada). |

---

## 4. Estructura Estándar de Errores

Para garantizar que el Frontend (Angular) maneje las excepciones de forma consistente y amigable para el operador, todo error devuelto por la API debe adherirse al siguiente esquema:

```json
{
  "codigo": "FORMATO_PLACA_INVALIDO",
  "mensaje": "La placa 'XYZ' no cumple con el formato colombiano válido (AAA123 para carro o AAA12A para moto).",
  "detalle": {
    "campo": "placa",
    "valorRecibido": "XYZ"
  },
  "timestamp": "2026-11-21T11:35:00-05:00"
}
```

### Catálogo de Códigos de Error de Negocio

| Código de Error | HTTP Status | Causa / Regla de Negocio |
| :--- | :--- | :--- |
| `CREDENTIALES_INVALIDAS` | 401 | Usuario o contraseña incorrectos en Login. |
| `TOKEN_EXPIRADO` | 401 | La sesión del operador expiró. |
| `PERMISO_DENEGADO` | 403 | Acción reservada solo para rol Administrador. |
| `FORMATO_PLACA_INVALIDO` | 400 | Placa no cumple formato de 3 letras + 3 dígitos o 3 letras + 2 dígitos + 1 letra. |
| `VEHICULO_NO_ENCONTRADO` | 404 | No se encuentra el vehículo consultado. |
| `VEHICULO_YA_DENTRO` | 409 | Regla de anti-passback: el vehículo ya registra un ingreso activo sin salida. |
| `PARQUEADERO_LLENO` | 400 | Cupos agotados para la categoría de vehículo (CARRO o MOTO). |
| `TARIFA_NOCTURNA_INVALIDA` | 400 | RN-04: La tarifa nocturna no puede ser mayor o igual a la tarifa diurna. |
| `COBRO_YA_EXISTE` | 409 | RN-05: Ya existe un cobro registrado para el vehículo en este día operativo. |
| `PAGO_YA_CONFIRMADO` | 400 | Intento de pagar un cobro que ya se encuentra pagado. |

---

## 5. Autenticación y Seguridad (F-01 / S115 / S207)

### 5.1 Mecanismo
- **Esquema:** Bearer Token (JWT).
- **Cabecera HTTP requerida en solicitudes protegidas:**
  ```http
  Authorization: Bearer <token_jwt>
  ```

### 5.2 Roles Soportados
1. **`OPERADOR`**:
   - Acceso a pantalla de control de ingreso y salida.
   - Consulta de cupos disponibles.
   - Registro de cobros y pagos en efectivo.
2. **`ADMINISTRADOR`**:
   - Todas las funciones del Operador.
   - Configuración de sedes y carriles.
   - Configuración y versionamiento de tarifas.
   - Auditoría y reportes del sistema.

---

## 6. Paginación y Filtrado

Para consultas de listados (eventos, historial, auditoría, cobros):

### Parámetros Query estándar:
- `pagina` (int, default: 1): Número de página solicitada.
- `limite` (int, default: 20, max: 100): Cantidad de elementos por página.
- `desde` (datetime opcional): Fecha/hora inicio de búsqueda.
- `hasta` (datetime opcional): Fecha/hora fin de búsqueda.
- `placa` (string opcional): Filtro por coincidencia de placa.

### Estructura de Respuesta Paginada:
```json
{
  "datos": [
    { ... },
    { ... }
  ],
  "paginacion": {
    "totalRegistros": 150,
    "paginaActual": 1,
    "totalPaginas": 8,
    "limitePorPagina": 20
  }
}
```

---

## 7. Mapa de Endpoints Principales del MVP

### 7.1 Autenticación (`/api/v1/auth`)
- `POST /api/v1/auth/login`: Autenticación con credenciales y entrega de token.
- `GET /api/v1/auth/perfil`: Datos del usuario autenticado y su rol.

### 7.2 Sedes y Carriles (`/api/v1/sedes`, `/api/v1/carriles`)
- `GET /api/v1/sedes`: Listado de sedes activas y sus cupos.
- `GET /api/v1/carriles/sede/{sedeId}`: Listar carriles de una sede.
- `POST /api/v1/carriles`: Crear nuevo carril (Entrada/Salida).
- `PATCH /api/v1/carriles/{carrilId}/estado`: Activar o desactivar carril.

### 7.3 Vehículos (`/api/v1/vehiculos`)
- `POST /api/v1/vehiculos/clasificar`: Clasificar placa en tiempo real sin persistir.
- `GET /api/v1/vehiculos/{placa}`: Obtener datos de vehículo registrado.

### 7.4 Control de Acceso y LPR (`/api/v1/accesos`)
- `POST /api/v1/accesos/ingreso`: Registrar ingreso de vehículo (valida cupos, clasifica placa y autoriza barrera).
- `POST /api/v1/accesos/salida`: Registrar salida de vehículo (valida estado de cobro/pago).

### 7.5 Tarifas, Cobros y Pagos (`/api/v1/tarifas`, `/api/v1/cobros`, `/api/v1/pagos`)
- `GET /api/v1/tarifas/vigente`: Tarifas actuales diurnas/nocturnas para carro y moto ($0).
- `POST /api/v1/tarifas`: Actualizar tarifas cumpliendo RN-04.
- `GET /api/v1/cobros/vehiculo/{placa}`: Consultar cobro activo del día operativo.
- `POST /api/v1/pagos`: Registrar pago en efectivo (idempotente).
