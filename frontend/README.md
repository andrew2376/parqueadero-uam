# Sistema de Parqueadero con Reconocimiento de Placas

Sistema de gestión de parqueadero con reconocimiento automático de placas vehiculares (LPR), desarrollado como un MVP académico. El proyecto permite construir una solución modular para administrar el funcionamiento de un parqueadero, sus vehículos, sedes, carriles, cupos, tarifas y procesos relacionados con el acceso y los pagos.

El repositorio está organizado en dos aplicaciones independientes:

- **Backend:** API REST desarrollada con Python y FastAPI.
- **Frontend:** aplicación web desarrollada con Angular y TypeScript.

La persistencia de información se realiza mediante PostgreSQL.

---

## 1. Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Lenguaje backend | Python 3.12+ |
| Framework backend | FastAPI |
| Validación y configuración | Pydantic |
| ORM | SQLAlchemy 2 |
| Base de datos | PostgreSQL 16 |
| Driver de PostgreSQL | Psycopg 3 |
| Migraciones | Alembic |
| Servidor API | Uvicorn |
| Frontend | Angular |
| Lenguaje frontend | TypeScript |
| Contenedores | Docker y Docker Compose |
| Pruebas | Pytest |

---

## 2. Arquitectura del proyecto

El backend utiliza una arquitectura de monolito modular con principios de arquitectura hexagonal. Cada módulo separa las responsabilidades del dominio, la aplicación, la infraestructura y la presentación.

La estructura general del repositorio es:

```text
parqueadero-uam/
│
├── backend/
│   ├── app/
│   │   ├── configuracion.py
│   │   ├── main.py
│   │   ├── infraestructura/
│   │   │   └── base_datos/
│   │   └── modulos/
│   │       ├── accesos/
│   │       ├── auditoria/
│   │       ├── autenticacion/
│   │       ├── carriles/
│   │       ├── cobros/
│   │       ├── cupos/
│   │       ├── estado/
│   │       ├── gateway/
│   │       ├── pagos/
│   │       ├── reconocimiento_placas/
│   │       ├── reportes/
│   │       ├── sedes/
│   │       ├── tarifas/
│   │       └── vehiculos/
│   │
│   ├── migraciones/
│   ├── pruebas/
│   ├── .env.example
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── README.md
│
├── frontend/
│
├── documentacion/
│
├── .env
├── .gitignore
├── docker-compose.yml
└── README.md
```

### Organización del backend

Cada módulo del sistema mantiene una separación de responsabilidades:

- **Dominio:** contiene las entidades, objetos de valor, puertos y reglas de negocio.
- **Aplicación:** contiene los casos de uso y los DTO utilizados por la aplicación.
- **Infraestructura:** implementa los adaptadores, persistencia y comunicación con servicios externos.
- **Presentación:** contiene las rutas y esquemas utilizados para exponer las operaciones mediante HTTP.

Esta separación permite mantener las reglas de negocio independientes de los frameworks y de los mecanismos de persistencia.

---

## 3. Requisitos previos

Antes de ejecutar el proyecto, es necesario contar con las siguientes herramientas:

- Git.
- Python 3.12 o superior.
- Node.js y npm.
- Docker Desktop.
- Docker Compose.
- Un editor de código, como Visual Studio Code.

Para comprobar las instalaciones:

```powershell
git --version
python --version
node --version
npm --version
docker --version
docker compose version
```

---

## 4. Clonar el repositorio

Clonar el proyecto desde GitHub:

```powershell
git clone https://github.com/andrew2376/parqueadero-uam.git
```

Ingresar a la carpeta:

```powershell
cd parqueadero-uam
```

---

## 5. Configuración de variables de entorno

El proyecto utiliza variables de entorno para centralizar la configuración de la aplicación y proteger la información sensible.

El backend lee el archivo `.env` ubicado en la raíz del repositorio mediante `backend/app/configuracion.py`.

### Crear el archivo `.env`

Desde la raíz del proyecto, ejecutar:

```powershell
Copy-Item .\backend\.env.example .\.env
```

Después, abrir el archivo `.env` y revisar sus valores.

### Variables de configuración

| Variable | Descripción |
|---|---|
| `NOMBRE_APLICACION` | Nombre de la aplicación. |
| `ENTORNO` | Entorno de ejecución. |
| `PREFIJO_API` | Prefijo de las rutas de la API. |
| `POSTGRES_DB` | Nombre de la base de datos PostgreSQL. |
| `POSTGRES_USER` | Usuario de PostgreSQL. |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL. |
| `URL_BASE_DATOS` | Cadena de conexión utilizada por SQLAlchemy. |
| `SECRETO_JWT` | Secreto utilizado para la seguridad mediante JWT. |
| `ALGORITMO_JWT` | Algoritmo de firma de los tokens. |
| `UMBRAL_CONFIANZA_LECTURA` | Umbral de confianza para el reconocimiento de placas. |
| `ZONA_HORARIA` | Zona horaria utilizada por la aplicación. |
| `ORIGENES_PERMITIDOS` | Lista de orígenes autorizados para las solicitudes CORS. |

**Importante:**

- Cambiar los valores de ejemplo antes de utilizar el sistema fuera del entorno local.
- Utilizar un secreto JWT seguro y único.
- Mantener las credenciales reales únicamente en el archivo `.env`.
- No subir el archivo `.env` a GitHub.
- Mantener actualizado `backend/.env.example` cuando se agreguen nuevas variables.

---

## 6. Iniciar la base de datos

El proyecto utiliza PostgreSQL mediante Docker Compose.

Desde la raíz del repositorio, ejecutar:

```powershell
docker compose up -d
```

Comprobar el estado de los contenedores:

```powershell
docker compose ps
```

Para consultar los registros del contenedor:

```powershell
docker compose logs -f
```

La configuración del servicio PostgreSQL se encuentra en `docker-compose.yml`.

La base de datos utiliza el puerto `5432` para las conexiones locales.

Para detener los servicios:

```powershell
docker compose down
```

Este comando detiene los contenedores, pero conserva los datos almacenados en el volumen persistente.

---

## 7. Instalación y ejecución del backend

El backend está desarrollado con FastAPI y utiliza SQLAlchemy para la persistencia de datos.

### 7.1. Ingresar a la carpeta

Desde la raíz del proyecto:

```powershell
cd backend
```

### 7.2. Crear el entorno virtual

Si todavía no existe:

```powershell
python -m venv .venv
```

### 7.3. Activar el entorno virtual

En Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 7.4. Instalar las dependencias

```powershell
pip install -e ".[dev]"
```

Este comando instala las dependencias definidas en `pyproject.toml`, incluyendo las herramientas utilizadas durante el desarrollo y las pruebas.

### 7.5. Ejecutar el servidor

```powershell
uvicorn app.main:aplicacion --reload
```

El servidor estará disponible en:

```text
http://localhost:8000
```

### 7.6. Documentación de la API

FastAPI genera automáticamente la documentación interactiva de los endpoints.

Swagger UI:

http://localhost:8000/docs

ReDoc:

http://localhost:8000/redoc

Para detener el servidor, utilizar `Ctrl + C` en la terminal.

---

## 8. Instalación y ejecución del frontend

El frontend utiliza Angular y TypeScript para proporcionar la interfaz web del sistema.

### 8.1. Ingresar a la carpeta

Desde la raíz del repositorio:

```powershell
cd frontend
```

### 8.2. Instalar las dependencias

Si el proyecto Angular ya está inicializado y cuenta con `package.json`:

```powershell
npm install
```

### 8.3. Ejecutar Angular

```powershell
npx ng serve
```

La aplicación estará disponible en:

http://localhost:4200

Para detener el servidor, utilizar `Ctrl + C`.

> Si el frontend todavía no cuenta con un proyecto Angular inicializado, primero será necesario crear su estructura y sus archivos de configuración antes de ejecutar estos comandos.

---

## 9. Ejecución completa del proyecto

Para trabajar con todos los componentes al mismo tiempo, se recomienda utilizar tres terminales independientes.

| Terminal | Servicio | Comando |
|---|---|---|
| 1 | PostgreSQL | `docker compose up -d` |
| 2 | Backend | `uvicorn app.main:aplicacion --reload` |
| 3 | Frontend | `npx ng serve` |

Los servicios estarán disponibles en las siguientes direcciones:

| Servicio | Dirección |
|---|---|
| Frontend Angular | http://localhost:4200 |
| Backend FastAPI | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| PostgreSQL | localhost:5432 |

---

## 10. Pruebas

El proyecto utiliza Pytest para ejecutar las pruebas automatizadas del backend.

Desde la carpeta `backend`, con el entorno virtual activado:

```powershell
pytest
```

Para ejecutar las pruebas mostrando mayor detalle:

```powershell
pytest -v
```

---

## 11. Migraciones de base de datos

El proyecto utiliza Alembic para gestionar los cambios en la estructura de PostgreSQL.

Las migraciones se encuentran en:

```text
backend/migraciones/versions/
```

Las migraciones permiten mantener el esquema de la base de datos controlado y versionado.

Antes de ejecutar comandos de migración, consultar la configuración de `backend/alembic.ini` y las instrucciones vigentes del proyecto.

---

## 12. Seguridad y buenas prácticas

Para mantener una configuración segura y facilitar el trabajo colaborativo:

- No publicar credenciales, contraseñas ni secretos JWT.
- No subir archivos `.env` al repositorio.
- Mantener el archivo `.env.example` actualizado.
- No subir entornos virtuales ni dependencias instaladas.
- Mantener separadas las responsabilidades de cada módulo.
- Utilizar migraciones para controlar los cambios en la base de datos.
- Trabajar mediante ramas de Git para desarrollar nuevas funcionalidades.

---

## 13. Estado del proyecto

El sistema se encuentra en desarrollo como un producto mínimo viable (MVP).

Las funcionalidades se implementan progresivamente mediante historias de usuario y tareas de desarrollo. La estructura actual establece las bases arquitectónicas, tecnológicas y de infraestructura para continuar construyendo el sistema.

---

## 14. Repositorio

Código fuente:

https://github.com/andrew2376/parqueadero-uam