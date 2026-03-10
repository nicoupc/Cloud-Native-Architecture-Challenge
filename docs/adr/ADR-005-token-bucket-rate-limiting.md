# ADR-005: Algoritmo Token Bucket para Rate Limiting

## Estado

Aceptada

## Contexto

El Notification Service necesita rate limiting para evitar saturar a los proveedores de correo electrónico downstream y los canales de notificación externos. La estrategia de rate limiting debe:

- Controlar el throughput sostenido para mantenerse dentro de los límites del proveedor.
- Permitir ráfagas cortas para manejar escenarios de picos de demanda (por ejemplo, reservas de eventos populares).
- Ser sencilla de implementar y configurar.
- Funcionar dentro de un consumidor de proceso único (no se requiere rate limiting distribuido para la escala actual).

## Decisión

Implementar el algoritmo Token Bucket con las siguientes características:

- **Tasa configurable**: Por defecto, 5 mensajes por segundo (variable de entorno `RATE_LIMIT_PER_SECOND`).
- **Capacidad de ráfaga configurable**: Por defecto, 10 tokens (variable de entorno `RATE_LIMIT_BURST`).
- **Recarga continua de tokens**: Los tokens se añaden a la tasa configurada, hasta el máximo de capacidad de ráfaga.
- **Consumo bloqueante**: Cuando no hay tokens disponibles, el consumidor espera hasta que se recargue un token antes de procesar el siguiente mensaje.

## Consecuencias

- **Procesamiento fluido de mensajes bajo carga**: El token bucket garantiza una tasa de procesamiento constante que respeta los límites de los proveedores downstream.
- **Manejo de ráfagas**: La capacidad de ráfaga permite al sistema absorber picos cortos (hasta 10 mensajes de forma instantánea) sin descartar ni retrasar mensajes innecesariamente.
- **Implementación sencilla**: El algoritmo token bucket es ampliamente conocido, fácil de implementar en Python asyncio y no requiere dependencias externas (sin Redis ni coordinación distribuida).
- **Configurabilidad en tiempo de ejecución**: Los parámetros de tasa y ráfaga son configurables mediante variables de entorno, lo que permite a los operadores ajustar el throughput sin modificar el código.
- **Compromiso**: Rate limiting de proceso único solamente. Si el Notification Service escala a múltiples instancias de consumidores, se necesitaría una solución de rate limiting distribuido (por ejemplo, basada en Redis).
