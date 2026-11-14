# Frontend

Aplicación web Angular + TypeScript. Inicializar con `npx @angular/cli new . --routing --style=scss --standalone --skip-git`.

```text
src/app/
├── nucleo/                 # autenticación, guards, interceptores, configuración
├── compartido/             # componentes, directivas y pipes reutilizables
├── estructura/             # menú, encabezado y contenedor principal
└── funcionalidades/
    ├── inicio/
    ├── accesos/
    ├── vehiculos/
    ├── cobros/
    ├── pagos/
    ├── tarifas/
    ├── cupos/
    ├── sedes/
    ├── carriles/
    ├── reportes/
    └── auditoria/
```

Cada funcionalidad contiene páginas, componentes, modelos y servicios de acceso a la API. Las reglas de negocio autoritativas permanecen en el backend.
