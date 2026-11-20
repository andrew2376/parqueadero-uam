\# P05 — Historias de usuario del sistema de parqueadero LPR



\## 1. Objetivo



Documentar las historias de usuario correspondientes al sistema de parqueadero con reconocimiento de placas (LPR), describiendo las funcionalidades del MVP desde la perspectiva de sus actores, sus necesidades, los flujos de operación y los criterios de aceptación.



\## 2. Alcance



El sistema contempla una aplicación web desarrollada con Angular, un backend construido con FastAPI y una base de datos PostgreSQL. Su arquitectura corresponde a un monolito modular con arquitectura hexagonal.



El MVP contempla la administración del parqueadero, identificación de vehículos, control de accesos, reconocimiento de placas simulado, gestión de tarifas, cobros, pagos, cupos, reingresos, salidas, auditoría y consultas.



Las historias descritas en este documento se estructuran a partir del alcance y las reglas de negocio documentadas en el repositorio.



\---



\## F-01. Autenticación y control de acceso



\*\*Actor principal:\*\* Usuario autorizado.



\*\*Historia de usuario:\*\*



Como usuario autorizado, quiero iniciar sesión en el sistema mediante mis credenciales, para acceder de forma segura a las funcionalidades que corresponden a mis permisos.



\### Flujo normal

1\. El usuario ingresa a la aplicación.

2\. Introduce sus credenciales.

3\. El sistema valida la información.

4\. El sistema identifica al usuario y sus permisos.

5\. Se permite el acceso a las funcionalidades autorizadas.



\### Flujos alternativos y errores

\- Si las credenciales son incorrectas, el sistema informa que no fue posible iniciar sesión.

\- Si faltan campos obligatorios, el sistema solicita completar la información.

\- Si el usuario no cuenta con permisos, el sistema restringe el acceso a la funcionalidad solicitada.



\### Criterios de aceptación

\- El sistema permite iniciar sesión con credenciales válidas.

\- Las credenciales inválidas no permiten el acceso.

\- Las funcionalidades protegidas requieren autenticación.

\- Se respetan los permisos asignados al usuario.



\---



\## F-02. Administración de sedes y carriles



\*\*Actor principal:\*\* Administrador.



\*\*Historia de usuario:\*\*



Como administrador, quiero gestionar las sedes y sus carriles, para mantener configurados los puntos de acceso y operación del parqueadero.



\### Flujo normal

1\. El administrador ingresa al módulo de sedes y carriles.

2\. Consulta la información disponible.

3\. Selecciona la sede correspondiente.

4\. Consulta los carriles asociados.

5\. Registra o modifica la información permitida.

6\. El sistema valida y guarda los cambios.



\### Flujos alternativos y errores

\- Si faltan datos obligatorios, el sistema impide guardar.

\- Si la sede no existe, el sistema informa la situación.

\- Si se intenta registrar información duplicada, el sistema valida y evita inconsistencias.



\### Criterios de aceptación

\- Se pueden consultar las sedes registradas.

\- Se pueden consultar los carriles asociados a una sede.

\- Los campos obligatorios son validados.

\- Los cambios se guardan correctamente.

\- La información de los carriles corresponde a la sede seleccionada.



\---



\## F-03. Registro e identificación de vehículos



\*\*Actor principal:\*\* Operador del parqueadero.



\*\*Historia de usuario:\*\*



Como operador, quiero registrar e identificar los vehículos mediante su placa y clasificación, para mantener información confiable de los vehículos que utilizan el parqueadero.



\### Flujo normal

1\. El operador ingresa la placa del vehículo.

2\. El sistema valida la información.

3\. Consulta si el vehículo ya se encuentra registrado.

4\. Si corresponde, registra el vehículo.

5\. Asocia la clasificación del vehículo.

6\. Guarda la información.



\### Flujos alternativos y errores

\- Si la placa está vacía, el sistema impide continuar.

\- Si la placa no cumple el formato establecido, informa el error.

\- Si el vehículo ya existe, el sistema recupera su información para evitar registros innecesarios.



\### Criterios de aceptación

\- Los vehículos pueden identificarse por su placa.

\- Se almacena la clasificación correspondiente.

\- La información ingresada es validada.

\- Se evita duplicar vehículos de manera injustificada.

\- El vehículo registrado puede utilizarse en los procesos de acceso y cobro.



\---



\## F-04. Reconocimiento de placas



\*\*Actor principal:\*\* Sistema de reconocimiento LPR.



\*\*Historia de usuario:\*\*



Como sistema de parqueadero, quiero procesar el reconocimiento de las placas de los vehículos, para facilitar su identificación durante las operaciones de ingreso y salida.



\### Flujo normal

1\. El sistema recibe una captura o una entrada de reconocimiento simulada.

2\. Procesa la información recibida.

3\. Obtiene la placa detectada.

4\. Determina el resultado de la lectura y su nivel de confianza, cuando esté disponible.

5\. Entrega el resultado al proceso de control de acceso.



\### Flujos alternativos y errores

\- Si no se detecta una placa, el sistema registra o informa la lectura fallida.

\- Si la confianza de la lectura es insuficiente, se contempla la validación correspondiente.

\- Si el mecanismo de reconocimiento no está disponible, se informa el inconveniente.



\### Criterios de aceptación

\- El sistema procesa una lectura de placa.

\- La lectura puede relacionarse con el evento de acceso.

\- Se contempla el caso de lectura fallida.

\- Se contempla el nivel de confianza cuando el mecanismo lo proporcione.

\- El reconocimiento inicial puede realizarse mediante simulación.



\---



\## F-05. Control de ingreso de vehículos



\*\*Actor principal:\*\* Operador del parqueadero.



\*\*Historia de usuario:\*\*



Como operador, quiero registrar y validar el ingreso de los vehículos, para controlar su entrada y mantener información consistente de los accesos.



\### Flujo normal

1\. Se identifica el vehículo mediante su placa.

2\. El sistema consulta la información del vehículo.

3\. Verifica las condiciones de ingreso.

4\. Consulta la disponibilidad de cupos.

5\. Registra el ingreso autorizado.

6\. Actualiza el estado del acceso y la ocupación.



\### Flujos alternativos y errores

\- Si no existen cupos disponibles, el sistema no autoriza el ingreso.

\- Si el vehículo no puede identificarse, se contempla el procedimiento de validación.

\- Si existe un ingreso activo, el sistema evita registrar un nuevo ingreso inconsistente.

\- Si ocurre un error durante el registro, se evita dejar estados inconsistentes.



\### Criterios de aceptación

\- El ingreso autorizado queda registrado.

\- Se valida la disponibilidad de cupos.

\- El ingreso se relaciona con el vehículo correspondiente.

\- No se permiten ingresos que generen estados inconsistentes.

\- La información del ingreso puede utilizarse en los procesos de cobro y salida.



\---



\## F-06. Administración y consulta de cupos



\*\*Actor principal:\*\* Operador del parqueadero.



\*\*Historia de usuario:\*\*



Como operador, quiero consultar la disponibilidad de cupos por tipo de vehículo, para conocer la ocupación y evitar superar la capacidad configurada del parqueadero.



\### Flujo normal

1\. El operador accede a la consulta de cupos.

2\. El sistema obtiene la capacidad configurada.

3\. Consulta los vehículos que se encuentran dentro.

4\. Calcula los cupos disponibles.

5\. Presenta la disponibilidad por tipo de vehículo.



\### Flujos alternativos y errores

\- Si la capacidad no está configurada, el sistema informa la situación.

\- Si la capacidad está completa, muestra que no hay cupos disponibles.

\- Si ocurre un error de consulta, informa que no fue posible obtener la disponibilidad.



\### Criterios de aceptación

\- La disponibilidad se consulta por clasificación de vehículo.

\- La ocupación se actualiza con los movimientos registrados.

\- No se supera la capacidad configurada.

\- Los ingresos y salidas se reflejan en la disponibilidad.

\- La información de cupos corresponde al estado registrado del parqueadero.



\---



\## F-07. Gestión de tarifas y generación de cobros



\*\*Actor principal:\*\* Administrador y sistema de cobros.



\*\*Historia de usuario:\*\*



Como administrador del parqueadero, quiero gestionar las tarifas y generar los cobros de acuerdo con las reglas del día operativo, para garantizar que los valores aplicados a los vehículos sean correctos.



\### Flujo normal

1\. El sistema identifica el vehículo y su placa.

2\. Determina el día operativo correspondiente.

3\. Identifica la franja tarifaria aplicable al primer ingreso.

4\. Consulta la tarifa configurada.

5\. Genera el cobro correspondiente.

6\. Conserva el valor y la tarifa aplicados al cobro.



\### Flujos alternativos y errores

\- Si no existe una tarifa configurada, el sistema evita generar un cobro incorrecto.

\- Si ya existe un cobro para la misma placa, sede y día operativo, evita duplicarlo.

\- Si una tarifa cambia posteriormente, los cobros anteriores conservan sus valores históricos.



\### Criterios de aceptación

\- Se aplica la tarifa correspondiente al día operativo.

\- Se considera la franja del primer ingreso.

\- Se evita generar más de un cobro por placa, sede y día operativo.

\- El cobro conserva el valor y la tarifa aplicada.

\- Las motos utilizan la tarifa configurada de cero, conforme a la regla RN-01.



\---



\## F-08. Registro y confirmación de pagos



\*\*Actor principal:\*\* Cajero u operador autorizado.



\*\*Historia de usuario:\*\*



Como cajero, quiero registrar y confirmar los pagos de los cobros pendientes, para mantener control de las transacciones y permitir que los vehículos completen su proceso de salida.



\### Flujo normal

1\. El cajero consulta el cobro asociado al vehículo.

2\. Verifica el valor pendiente.

3\. Selecciona el medio de pago habilitado.

4\. Registra la transacción.

5\. El sistema valida el pago.

6\. Confirma la transacción.

7\. Actualiza el estado del cobro.



\### Flujos alternativos y errores

\- Si el cobro no existe, el sistema informa el error.

\- Si el cobro ya está pagado, evita registrar un pago duplicado.

\- Si ocurre un error durante la operación, informa el resultado y mantiene la consistencia.

\- Si se recibe una solicitud repetida, evita duplicar la transacción.



\### Criterios de aceptación

\- Se puede registrar el pago de un cobro pendiente.

\- El pago queda relacionado con el cobro correspondiente.

\- Se evita duplicar pagos.

\- El estado del cobro se actualiza correctamente.

\- Es posible verificar si el cobro se encuentra pagado.



\---



\## F-09. Control de reingresos y salida de vehículos



\*\*Actor principal:\*\* Operador y sistema de control de accesos.



\*\*Historia de usuario:\*\*



Como operador, quiero validar los reingresos y las salidas de los vehículos, para garantizar que los movimientos se realicen conforme a las reglas de pago, acceso y disponibilidad del parqueadero.



\### Flujo normal de salida

1\. El sistema identifica el vehículo.

2\. Consulta su estado de acceso y cobro.

3\. Verifica las condiciones de salida.

4\. Valida que no exista un cobro pendiente.

5\. Autoriza la salida.

6\. Registra el movimiento.

7\. Libera el cupo correspondiente.



\### Flujo normal de reingreso

1\. El sistema identifica el vehículo.

2\. Consulta el pago vigente.

3\. Verifica que el pago corresponda al día operativo vigente.

4\. Valida las condiciones de reingreso.

5\. Verifica la disponibilidad de cupos.

6\. Autoriza el reingreso cuando se cumplen las condiciones.



\### Flujos alternativos y errores

\- Si existe un cobro pendiente, no se autoriza la salida.

\- Si el pago ya no es válido para el día operativo, se rechaza el reingreso.

\- Si el vehículo ya salió, se evita registrar otra salida inconsistente.

\- Si el cupo ya fue liberado, se evita liberar nuevamente.

\- Si no existen cupos disponibles, se rechaza el reingreso.



\### Criterios de aceptación

\- La salida se autoriza cuando se cumplen las condiciones establecidas.

\- No se autoriza la salida con cobros pendientes.

\- Los reingresos se validan según el pago y el día operativo vigente.

\- Las salidas quedan registradas.

\- Los cupos se liberan una sola vez.

\- Los estados de acceso, pago y ocupación permanecen consistentes.



\---



\## F-10. Historial, auditoría y reportes



\*\*Actor principal:\*\* Administrador u operador autorizado.



\*\*Historia de usuario:\*\*



Como administrador del parqueadero, quiero consultar el historial de accesos, cobros, pagos y acciones realizadas, para verificar la operación y disponer de información que facilite el seguimiento y control del sistema.



\### Flujo normal

1\. El usuario autorizado ingresa al módulo de consultas.

2\. Selecciona los filtros disponibles.

3\. El sistema procesa los criterios de búsqueda.

4\. Consulta los registros relacionados.

5\. Presenta los resultados.

6\. El usuario revisa la información.



\### Flujos alternativos y errores

\- Si no existen registros, el sistema presenta un resultado vacío.

\- Si los filtros son inválidos, informa el error.

\- Si ocurre un error de consulta, informa que no fue posible recuperar la información.

\- Si el usuario no tiene permisos, restringe la consulta.



\### Criterios de aceptación

\- Se pueden consultar los registros históricos disponibles.

\- Las consultas permiten utilizar los filtros habilitados.

\- Se puede consultar información relacionada con accesos, cobros y pagos.

\- Las acciones sensibles pueden registrarse en auditoría.

\- Se contemplan resultados vacíos y errores de consulta.

\- La información presentada corresponde a los registros almacenados.



\---



\## 3. Reglas de negocio relacionadas



Las historias de usuario deben respetar las siguientes reglas definidas en la documentación del proyecto:



| Código | Regla |

|---|---|

| RN-01 | Las motos se registran y usan una tarifa configurable de cero. |

| RN-02 | La tarifa nocturna es menor que la diurna. |

| RN-03 | Un pago permite reingresos durante el día operativo vigente. |

| RN-04 | Máximo un cobro por placa, sede y día operativo. |

| RN-05 | La tarifa corresponde a la franja del primer ingreso del día operativo. |

| RN-06 | No se autoriza la salida si existe un cobro pendiente. |

| RN-07 | Cada cobro conserva el valor y la tarifa aplicados al crearse. |



\### Supuestos operativos documentados

\- Franja diurna: 06:00 a 17:59.

\- Franja nocturna: 18:00 a 05:59.

\- Día operativo: 06:00 hasta 05:59 del día siguiente.

\- El modelo de cobro corresponde a un pase diario y no a cobro por horas.

\- El cobro se genera al ingreso y se paga antes de salir.

\- Se utiliza la zona horaria de la sede.

\- Si un vehículo permanece dentro al comenzar un nuevo día operativo, se genera el cobro del nuevo día.



Estos supuestos deben validarse con el cliente antes de considerarse definitivos.



\---



\## 4. Consideraciones del MVP



\- El sistema se desarrolla inicialmente para una sede.

\- El reconocimiento LPR se contempla inicialmente mediante simulación.

\- La lógica de negocio debe permanecer en el backend.

\- Angular consume los servicios REST del backend.

\- PostgreSQL es la fuente de persistencia.

\- El sistema contempla pagos en caja en la primera fase.

\- El OCR real, operación sin conexión y pasarela de pagos externa se consideran evoluciones posteriores.



\---



\## 5. Estado del documento



Este documento organiza las historias de usuario del MVP a partir de la arquitectura, las reglas de negocio y los módulos identificados en el repositorio.



La distribución F-01 a F-10 constituye la organización funcional de las historias para el desarrollo y revisión del proyecto. Debe verificarse con el equipo antes de considerarse una nomenclatura definitiva de requisitos.



\*\*Tarea relacionada:\*\* P05 — Redactar historias de usuario F-01 a F-10.



\*\*Responsable:\*\* Yulian.



\*\*Estado:\*\* Documento en elaboración y revisión.
