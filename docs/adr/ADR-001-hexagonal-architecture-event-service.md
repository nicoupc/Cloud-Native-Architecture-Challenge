# ADR-001: Hexagonal Architecture para Event Service

## Estado

Aceptada

## Contexto

El Event Service necesita aislar la lógica de negocio de las preocupaciones de infraestructura como PostgreSQL, EventBridge y las APIs REST. El equipo requería una alta capacidad de prueba (testability) de la lógica de dominio y la posibilidad de intercambiar adaptadores de infraestructura sin modificar las reglas de negocio principales. Se necesitaba un patrón arquitectónico claro para aplicar la inversión de dependencias y mantener la separación de responsabilidades a medida que el servicio evoluciona.

## Decisión

Utilizar Hexagonal Architecture (Ports & Adapters) con tres capas diferenciadas:

- **Capa de Dominio**: Contiene el agregado `Event`, objetos de valor y la lógica de dominio. No tiene dependencias con la infraestructura.
- **Capa de Aplicación**: Contiene los servicios de aplicación que orquestan los casos de uso. Depende únicamente del dominio y de las interfaces de puertos.
- **Capa de Infraestructura**: Contiene los adaptadores para JPA (PostgreSQL), EventBridge (publicación de eventos) y REST (API HTTP). Implementa las interfaces de puertos definidas en las capas de dominio y aplicación.

El flujo de dependencias es estrictamente hacia adentro: infraestructura → aplicación → dominio.

## Consecuencias

- **Inversión de dependencias limpia** mediante interfaces de puertos (`EventRepository`, `EventPublisher`) que permiten que el dominio permanezca agnóstico a la infraestructura.
- **El dominio es completamente testeable** sin necesidad de levantar bases de datos, brokers de mensajes ni servidores HTTP.
- **Intercambiabilidad de adaptadores**: Los adaptadores de infraestructura (por ejemplo, cambiar de PostgreSQL a otro almacén de datos) pueden reemplazarse sin modificar la lógica de negocio.
- **Compromiso**: Un poco más de código repetitivo (boilerplate) debido a las interfaces de puertos y las implementaciones de adaptadores, pero esto se compensa con una mantenibilidad y capacidad de prueba significativamente mejores.
- **Incorporación**: Los nuevos desarrolladores deben comprender el patrón hexagonal, pero los límites claros entre capas hacen que el código sea más fácil de navegar una vez comprendido.
