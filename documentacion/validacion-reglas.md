# P04 – Validación de reglas de negocio y supuestos

**Proyecto:** Sistema de Parqueadero con Reconocimiento de Placas (LPR)  
**Asignatura:** Ingeniería de Software II  
**Actividad:** P04 – Validar reglas, supuestos y discrepancia RN-02  
**Rama:** `docs/p04-validacion-reglas`

## 1. Objetivo

Revisar las reglas de negocio RN-01 a RN-07 y los supuestos S-01 a S-07 definidos en el documento de contexto del problema, contrastándolos con los criterios establecidos en la guía de entrega del tercer corte.

El propósito es identificar inconsistencias, aclarar las condiciones que deben considerarse durante el desarrollo y registrar las decisiones que todavía requieren confirmación del cliente o del equipo.

## 2. Documentos revisados

| Documento | Información utilizada |
|---|---|
| `01-contexto-del-problema.md` | Reglas de negocio, supuestos, escenarios, casos borde y preguntas abiertas. |
| Entrega final: tercer corte | Alcance del MVP, requisitos funcionales, criterios de aceptación y pruebas obligatorias. |
| `documentacion/reglas-negocio.md` | Resumen de reglas y supuestos que ya se encuentran incorporados al repositorio. |

## 3. Validación de reglas de negocio

| ID | Regla revisada | Resultado de la revisión | Observación |
|---|---|---|---|
| RN-01 | Las motos se registran, pero no generan cobro. Se recomienda una tarifa configurable de valor cero. | Consistente | La regla coincide con el criterio F-03 de la guía. Se debe conservar el registro de ingreso y salida de las motos. |
| RN-02 | La tarifa nocturna siempre debe ser menor que la diurna. | Consistente | El criterio F-08 establece que se rechacen tarifas nocturnas mayores o iguales a las diurnas. |
| RN-03 | Un pago permite salir y reingresar durante el día operativo vigente sin generar otro cobro. | Consistente | La guía F-04 contempla un pase vigente hasta el final del día operativo. |
| RN-04 | Solo puede existir un cobro por placa, sede y día operativo. | Consistente | La guía F-03 exige garantizar la unicidad mediante una restricción en la base de datos. |
| RN-05 | La tarifa aplicada depende de la franja del primer ingreso del día operativo. | Consistente | El contexto establece ejemplos de ingreso diurno y nocturno. Debe evitarse recalcular la tarifa en cada reingreso. |
| RN-06 | No se autoriza la salida si existe un cobro pendiente. | Consistente | El criterio F-05 establece que la barrera solo abre si el cobro está pagado o no existe. |
| RN-07 | Las tarifas se versionan y cada cobro conserva los valores utilizados al generarse. | Consistente | El criterio F-08 exige conservar la tarifa aplicada al cobro. |

**Resultado:** En los documentos comparados no se identificaron contradicciones entre las siete reglas de negocio y los criterios de aceptación de la guía.

## 4. Validación de supuestos

Los supuestos siguientes se encuentran definidos en el documento de contexto. Su coherencia documental no significa que hayan sido aprobados por el cliente.

| ID | Supuesto | Resultado | Observación o pendiente |
|---|---|---|---|
| S-01 | Franja diurna de 06:00 a 17:59 y nocturna de 18:00 a 05:59. | Coherente | Los horarios están definidos y deben mantenerse configurables. Confirmar con el cliente si corresponden a la operación real. |
| S-02 | El día operativo comprende desde las 06:00 hasta las 05:59 del día siguiente. | Coherente | La guía F-03 también utiliza este periodo. Confirmar que el cliente acepta el día operativo en lugar del calendario. |
| S-03 | El cobro corresponde a un pase diario y no depende del tiempo de permanencia. | Pendiente de confirmación | El contexto señala que debe verificarse la regulación local de tarifas antes de adoptar definitivamente este modelo. |
| S-04 | El cobro se genera al ingresar y debe pagarse antes de salir. | Coherente | Coincide con el flujo de cobro y salida descrito en el contexto. |
| S-05 | Si el vehículo continúa dentro al iniciar un nuevo día operativo, se genera un nuevo cobro diurno. | Coherente | El nuevo periodo comienza a las 06:00 y se aplica la tarifa correspondiente a ese día. |
| S-06 | El pago solo tiene validez en la sede donde se realizó. | Pendiente de confirmación | Es una decisión comercial que debe confirmarse si se contempla la operación con varias sedes. |
| S-07 | Se utiliza la zona horaria de cada sede; para Colombia, `America/Bogota`. | Coherente | El contexto establece almacenar fechas en UTC y convertirlas a la zona horaria de la sede. |

## 5. Revisión específica de RN-02

Esta revisión se realiza debido a que la tarea P04 solicita validar una posible discrepancia relacionada con las tarifas diurna y nocturna.

**Regla RN-02 del documento de contexto:**

La tarifa nocturna siempre debe ser menor que la tarifa diurna. El sistema debe impedir que un administrador guarde una configuración que incumpla esta condición.

**Criterio F-08 de la guía de entrega:**

El sistema debe rechazar una tarifa nocturna mayor o igual a la diurna.

**Comparación:**

| Condición | Documento de contexto | Guía del tercer corte |
|---|---|---|
| Tarifa nocturna menor que la diurna | Permitida | Permitida |
| Tarifa nocturna igual a la diurna | No permitida | Rechazada |
| Tarifa nocturna mayor que la diurna | No permitida | Rechazada |

**Resultado de la revisión:**

No se identifica una discrepancia entre las dos fuentes consultadas. Ambas establecen la misma condición para validar las tarifas.

**Condición que debe respetar el sistema:**

`tarifa_nocturna < tarifa_diurna`

La validación debe realizarse al guardar la configuración de tarifas, evitando que se almacenen valores que incumplan la regla.

Si el equipo dispone de otra versión del documento o de una indicación del docente que señale una condición diferente, deberá incorporarse como fuente adicional y revisarse antes de modificar esta conclusión.

## 6. Revisión de preguntas abiertas

El documento de contexto contiene nueve preguntas que deben resolverse con el cliente. Se registran a continuación para evitar que los supuestos se interpreten como decisiones definitivas.

| ID | Tema pendiente | Supuesto actual | Acción requerida |
|---|---|---|---|
| P-01 | Modelo de cobro | Pase diario. | Confirmar si el cobro será fijo o dependerá del tiempo de permanencia. |
| P-02 | Vigencia del día | Día operativo de 06:00 a 05:59. | Confirmar el uso del día operativo. |
| P-03 | Franjas horarias | Diurna 06:00–17:59 y nocturna 18:00–05:59. | Confirmar los horarios con el cliente. |
| P-04 | Validez entre sedes | El pago solo vale en la sede donde se realizó. | Confirmar si habrá convenios o validez entre sedes. |
| P-05 | Permanencia durante la noche | Se genera un nuevo cobro diurno al iniciar el día operativo. | Confirmar el comportamiento para vehículos que permanecen durante varios días. |
| P-06 | Momento del cobro | Se genera al ingresar y se paga antes de salir. | Confirmar el flujo de pago. |
| P-07 | Cupos por tipo | Se consideran cupos separados para motos y carros. | Confirmar la distribución de capacidad. |
| P-08 | Otros vehículos y tarifas especiales | No se contemplan inicialmente, pero el modelo debe permitir configurarlos. | Confirmar si existen otros tipos de vehículos o convenios. |
| P-09 | Retención de fotografías | Se propone conservarlas durante 30 días. | Confirmar el periodo de retención y las condiciones de tratamiento de los datos. |

### Observaciones adicionales

- Para P-01, el contexto indica que debe verificarse la regulación local antes de adoptar definitivamente el pase diario.
- Para P-07, la separación de cupos por tipo debe confirmarse con el cliente.
- Para P-09, los 30 días aparecen como supuesto actual, mientras que la sección de protección de datos menciona un rango de ejemplo de 30 a 90 días. Por tanto, no debe considerarse un periodo aprobado.
- Las decisiones comerciales y operativas pendientes no deben cerrarse únicamente por conveniencia técnica.

## 7. Revisión de escenarios del contexto

Se verificó que los nueve escenarios de ejemplo del documento de contexto representan las reglas y supuestos descritos.

| Escenario | Comportamiento esperado | Reglas relacionadas |
|---|---|---|
| 1. Una moto ingresa y sale. | Se registran los movimientos sin generar cobro. | RN-01 |
| 2. Un carro ingresa a las 08:00. | Se genera un cobro diurno pendiente. | RN-02, RN-05 |
| 3. Un carro paga, sale y vuelve a ingresar. | Se permite el reingreso sin un nuevo cobro. | RN-03, RN-04 |
| 4. El mismo carro vuelve a ingresar a las 22:00. | No se genera otro cobro si el pase sigue vigente. | RN-03 |
| 5. Un carro ingresa por primera vez a las 19:00. | Se genera un cobro nocturno menor que el diurno. | RN-02, RN-05 |
| 6. Un carro ingresa a las 23:00 y sale a la 01:00. | Se conserva un solo cobro nocturno dentro del mismo día operativo. | RN-04, S-02 |
| 7. Un carro ingresa a las 05:50 y permanece después de las 06:00. | Se genera el cobro diurno del nuevo día operativo. | S-05 |
| 8. Un carro pagó el lunes y regresa el martes a las 07:00. | Se genera un nuevo cobro diurno. | RN-03, S-02 |
| 9. La cámara no logra leer la placa. | El operador valida o digita la placa y el evento queda marcado como lectura manual. | Consideraciones LPR |

## 8. Hallazgos y decisiones registradas

1. Las reglas RN-01 a RN-07 son coherentes entre el documento de contexto y la guía de entrega.
2. Los supuestos S-01 a S-07 se encuentran documentados, pero deben diferenciarse de las decisiones aprobadas por el cliente.
3. No se encontró una contradicción en RN-02 entre las fuentes revisadas.
4. La condición de RN-02 debe aplicarse tanto en la lógica de validación como en las pruebas automatizadas.
5. El modelo de cobro diario de S-03 requiere verificar la regulación local antes de considerarse una decisión definitiva.
6. Las preguntas P-01 a P-09 permanecen registradas como puntos de validación pendientes.
7. Los escenarios del contexto permiten identificar los comportamientos que posteriormente deben cubrir las pruebas automatizadas.

## 9. Pendientes de validación

| Pendiente | Responsable sugerido | Estado |
|---|---|---|
| Confirmar reglas RN-01 a RN-07 con el cliente. | Product Owner / equipo | Pendiente |
| Confirmar supuestos S-01 a S-07. | Product Owner / equipo | Pendiente |
| Resolver preguntas P-01 a P-09. | Product Owner / cliente | Pendiente |
| Confirmar si existe otra fuente que contradiga RN-02. | Equipo | Pendiente |
| Verificar la regulación local aplicable al modelo de cobro. | Equipo / responsable del análisis | Pendiente |

Los responsables son una propuesta de asignación; deben ajustarse a los roles reales del equipo.

## 10. Conclusión

La comparación documental permitió verificar que las reglas de negocio RN-01 a RN-07 mantienen coherencia con los criterios de aceptación de la guía del tercer corte.

En particular, la revisión de RN-02 no evidenció contradicciones: tanto el documento de contexto como la guía establecen que la tarifa nocturna debe ser estrictamente menor que la diurna.

Los supuestos S-01 a S-07 y las preguntas P-01 a P-09 quedan registrados para su validación con el cliente y el equipo. Se recomienda conservar esta distinción durante el desarrollo para evitar implementar como decisiones definitivas aspectos que todavía no han sido confirmados.
