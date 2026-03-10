# ADR-002: CQRS con DynamoDB GSI para el Booking Service

## Estado

Aceptada

## Contexto

El Booking Service presenta patrones de lectura y escritura asimétricos. Las operaciones de escritura son de naturaleza transaccional (crear reserva, confirmar reserva, cancelar reserva) y requieren consistencia fuerte. Las operaciones de lectura necesitan consultas optimizadas según diferentes patrones de acceso — principalmente por usuario (para listar las reservas de un usuario) y por evento (para listar todas las reservas de un evento). Un modelo relacional tradicional requeriría joins complejos o múltiples consultas para servir estos diferentes patrones de acceso de manera eficiente.

## Decisión

Implementar CQRS (Command Query Responsibility Segregation) utilizando DynamoDB como almacén de datos:

- **Modelo de escritura**: Utiliza la clave primaria (`bookingId`) para todas las operaciones transaccionales (crear, confirmar, cancelar). Garantiza consistencia fuerte para las mutaciones.
- **Modelo de lectura**: Utiliza Global Secondary Indexes (GSIs) para servir consultas de lectura optimizadas:
  - `UserBookingsIndex`: GSI sobre `userId` para consultar eficientemente todas las reservas de un usuario dado.
  - `EventBookingsIndex`: GSI sobre `eventId` para consultar eficientemente todas las reservas de un evento dado.

Una única tabla de DynamoDB sirve tanto al modelo de escritura como al de lectura, con los GSIs proporcionando las proyecciones del lado de lectura.

## Consecuencias

- **Consistencia eventual** entre el modelo de escritura (tabla base) y los modelos de lectura (GSIs), ya que los GSIs de DynamoDB son eventualmente consistentes por defecto.
- **Rendimiento de lectura optimizado** sin joins complejos — cada patrón de acceso es servido por un índice dedicado.
- **Diseño de tabla única** reduce la complejidad operativa en comparación con mantener almacenes de datos separados para lectura y escritura.
- **Costo-eficiente**: Los GSIs solo proyectan los atributos necesarios para cada patrón de lectura, minimizando los costos de almacenamiento y lectura.
- **Compromiso**: Agregar nuevos patrones de acceso en el futuro requiere crear GSIs adicionales, los cuales tienen un límite por tabla (20 GSIs por tabla).
