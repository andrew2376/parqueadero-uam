# Reglas de negocio

| ID | Regla |
|---|---|
| RN-01 | Las motos se registran y usan una tarifa configurable de cero. |
| RN-02 | La tarifa nocturna es menor que la diurna. |
| RN-03 | Un pago permite reingresos durante el día operativo vigente. |
| RN-04 | Máximo un cobro por placa, sede y día operativo. |
| RN-05 | La tarifa corresponde a la franja del primer ingreso del día operativo. |
| RN-06 | No se autoriza la salida si existe un cobro pendiente. |
| RN-07 | Cada cobro conserva el valor y la tarifa aplicados al crearse. |

## Supuestos iniciales del contexto
- Diurna: 06:00–17:59.
- Nocturna: 18:00–05:59.
- Día operativo: 06:00 hasta 05:59 del día siguiente.
- Pase diario, no cobro por horas.
- El cobro se genera al ingreso y se paga antes de salir.
- Zona horaria de la sede; Colombia: `America/Bogota`.
- Si el vehículo sigue dentro al iniciar un nuevo día operativo, se genera el cobro del nuevo día.

Estos supuestos deben validarse con el cliente.
