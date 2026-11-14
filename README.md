# Sistema de Parqueadero con Reconocimiento de Placas

Repositorio del MVP organizado en dos aplicaciones: `backend/` (Python + FastAPI) y `frontend/` (Angular + TypeScript). La base de datos será PostgreSQL.

## Arquitectura
Backend como monolito modular con arquitectura hexagonal. Cada módulo separa `dominio`, `aplicacion`, `infraestructura` y `presentacion`. Frontend organizado por funcionalidades, con núcleo, componentes compartidos y estructura visual.

## Tecnologías
- Python 3.12+, FastAPI, Pydantic
- PostgreSQL, SQLAlchemy 2, Alembic
- Angular, TypeScript
- Docker Compose
- Pytest

## Inicio local
1. Copiar `backend/.env.example` a `backend/.env` y revisar sus valores.
2. Ejecutar `docker compose up -d` desde la raíz.
3. En `backend/`: crear entorno virtual, instalar `pip install -e '.[dev]'` y ejecutar `uvicorn app.main:aplicacion --reload`.
4. Swagger estará en http://localhost:8000/docs.
5. Inicializar Angular dentro de `frontend/` con `npx @angular/cli new . --routing --style=scss --standalone --skip-git`.

Esta es la estructura inicial. Los casos de uso y reglas se desarrollarán por historias; no es todavía el sistema terminado.
