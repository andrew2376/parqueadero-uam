# Backend

API REST FastAPI como monolito modular con arquitectura hexagonal.

Cada módulo sigue esta estructura:

```text
modulo/
├── dominio/
│   ├── entidades/
│   ├── objetos_valor/
│   ├── puertos/
│   └── excepciones/
├── aplicacion/
│   ├── casos_uso/
│   └── dto/
├── infraestructura/
│   ├── persistencia/
│   └── adaptadores/
└── presentacion/
    ├── rutas/
    └── esquemas/
```

El dominio no importa FastAPI, SQLAlchemy ni SDK de proveedores. Aplicación coordina casos de uso mediante puertos. Infraestructura implementa adaptadores. Presentación traduce HTTP a operaciones de aplicación.
