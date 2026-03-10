# ADR-003: Saga Orchestration sobre Choreography para Payment Service

## Estado

Aceptada

## Contexto

El flujo de pago requiere una transacción distribuida coordinada entre múltiples servicios que abarca varios pasos: reservar booking → procesar pago → confirmar booking → notificar al usuario. Si algún paso falla, los pasos anteriores deben ser compensados (revertidos). Se consideraron dos patrones:

- **Choreography**: Cada servicio reacciona a eventos y publica sus propios eventos. No existe un coordinador central.
- **Orchestration**: Un orquestador central dirige los pasos del saga y gestiona la compensación.

Choreography fue descartado porque el flujo de pago tiene un orden secuencial estricto y una lógica de compensación que se vuelve difícil de rastrear y depurar a través de múltiples servicios independientes.

## Decisión

Utilizar el patrón Saga Orchestration donde el Payment Service actúa como orquestador central. Una state machine rastrea el progreso del saga a través de estados bien definidos:

```
STARTED → BOOKING_RESERVED → PAYMENT_PROCESSED → BOOKING_CONFIRMED → COMPLETED
```

Ante un fallo en cualquier paso, el orquestador dispara acciones de compensación para revertir los pasos completados previamente (por ejemplo, cancelar la reserva del booking, emitir un reembolso del pago).

## Consecuencias

- **Punto central de control** para la transacción distribuida, lo que hace que el flujo sea explícito y fácil de razonar.
- **Flujo de compensación claro**: Cada transición de estado tiene una acción de rollback definida, garantizando la consistencia de datos entre servicios en caso de fallo.
- **Depuración y monitoreo más sencillos**: La state machine del saga proporciona una vista única del progreso de la transacción, facilitando la identificación del punto donde ocurren los fallos.
- **Compromiso — punto único de coordinación**: El Payment Service se convierte en una dependencia crítica para el flujo de pago. Si falla, los sagas en curso pueden detenerse. Esto se mitiga persistiendo el estado del saga en DynamoDB y soportando la recuperación del saga al reiniciar.
- **Compromiso — acoplamiento más estrecho**: El orquestador debe conocer los pasos involucrados, lo que genera cierto acoplamiento con las APIs de los servicios participantes.
