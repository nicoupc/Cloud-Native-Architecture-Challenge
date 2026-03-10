# ADR-006: EventBridge como Bus Central de Eventos

## Estado

Aceptada

## Contexto

La arquitectura de microservicios requiere comunicación asíncrona entre servicios para flujos de trabajo dirigidos por eventos. El ecosistema de AWS ofrece varias opciones de mensajería:

- **EventBridge**: Enrutamiento basado en contenido con coincidencia de patrones, bus de eventos administrado.
- **SQS**: Cola de mensajes punto a punto.
- **SNS**: Mensajería pub/sub basada en topics.

Se necesitaba una estrategia de enrutamiento que desacople a los productores de eventos de los consumidores, admita filtrado por tipo de evento y minimice la sobrecarga operativa de gestionar suscripciones a topics.

## Decisión

Utilizar Amazon EventBridge como bus central de eventos para toda la comunicación entre servicios:

- Todos los servicios publican eventos de dominio en un bus de eventos personalizado llamado `event-management-bus`.
- Las reglas de EventBridge enrutan eventos a colas SQS basándose en patrones de `source` y `detail-type`.
- Los servicios consumidores consultan sus colas SQS dedicadas para obtener mensajes.
- **No se utiliza SNS** — las reglas de EventBridge reemplazan la necesidad de gestionar topics SNS y filtrado de suscripciones.

Siete reglas de enrutamiento conectan los servicios con sus colas correspondientes:

**Reglas hacia `notification-queue`:**

1. `booking-created` — enruta eventos de creación de reservas.
2. `booking-confirmed` — enruta eventos de confirmación de reservas.
3. `booking-cancelled` — enruta eventos de cancelación de reservas.
4. `payment-completed` — enruta eventos de pagos exitosos.
5. `payment-failed` — enruta eventos de pagos fallidos.

**Reglas hacia `booking-events-queue`:**

6. `event-created` — enruta eventos de creación de eventos (EventCreated).
7. `event-cancelled` — enruta eventos de cancelación de eventos (EventCancelled).

## Consecuencias

- **Enrutamiento centralizado de eventos** con filtrado basado en patrones simplifica la arquitectura del flujo de eventos. Se pueden agregar nuevos consumidores creando nuevas reglas sin modificar los productores.
- **Productores y consumidores desacoplados**: Los servicios publican eventos sin conocimiento de quién los consume. El enrutamiento se gestiona completamente en las reglas de EventBridge.
- **Los eventos son enrutables por `source` y `detail-type`**, lo que permite un filtrado granular sin atributos de mensaje personalizados.
- **Elimina la complejidad de SNS**: Las reglas de EventBridge reemplazan la necesidad de crear y gestionar topics SNS, suscripciones y políticas de filtrado.
- **Compromiso — límites de EventBridge**: EventBridge tiene un límite de tamaño de payload (256 KB) y límites de tasa que pueden requerir consideración en escenarios de muy alto rendimiento. Suficiente para la escala actual.
- **Observabilidad**: EventBridge se integra con CloudWatch para monitorear invocaciones de reglas y entregas fallidas.
