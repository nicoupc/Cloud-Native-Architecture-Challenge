# ADR-004: Consumidor SQS con Asyncio en lugar de Lambda para el Notification Service

## Estado

Aceptada

## Contexto

La especificación de `challenge.md` sugiere utilizar AWS Lambda para el polling de SQS en el Notification Service. Sin embargo, Lambda introduce complejidad adicional para el desarrollo local:

- Lambda requiere configuración específica de empaquetado y despliegue (ZIP o imagen de contenedor).
- La emulación local de Lambda con LocalStack es más compleja de configurar y depurar.
- Los cold starts de Lambda pueden introducir latencia en el procesamiento de notificaciones.
- Las pruebas de integración con Lambda requieren herramientas adicionales.

El equipo priorizó la experiencia de desarrollo local y la facilidad de depuración, manteniendo equivalencia funcional con un enfoque basado en Lambda.

## Decisión

Utilizar un consumidor de long-polling con Python asyncio en lugar de AWS Lambda. El consumidor:

- Realiza polling a SQS con `WaitTimeSeconds=20` (long polling) para minimizar respuestas vacías y reducir llamadas a la API.
- Procesa mensajes en lotes de hasta 10 mensajes por ciclo de polling.
- Implementa rate limiting con token bucket para controlar el throughput.
- Soporta apagado graceful mediante manejo de señales (SIGTERM, SIGINT).

## Consecuencias

- **Desarrollo y pruebas locales más simples**: El consumidor se ejecuta como un proceso estándar de Python, fácilmente depurable con herramientas estándar.
- **Equivalencia funcional**: Los mensajes se procesan desde SQS con el mismo resultado final que un enfoque basado en Lambda.
- **Mayor facilidad para agregar aspectos transversales**: Rate limiting, apagado graceful, health checks y métricas se pueden agregar directamente al proceso del consumidor.
- **Compromiso — no es serverless**: El consumidor requiere un proceso en ejecución (contenedor), a diferencia de Lambda que escala a cero. Esto incrementa el costo base de infraestructura.
- **Ruta de migración a producción**: En producción, este consumidor puede migrarse a Lambda con un trigger de SQS. La lógica de procesamiento de mensajes (handler) está desacoplada del mecanismo de polling, lo que hace esta migración sencilla.
