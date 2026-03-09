#!/bin/bash

# Script para crear reglas de EventBridge que conectan los microservicios
# Estas reglas implementan el patrón Event-Driven Architecture (EDA)
# enrutando eventos del bus central hacia las colas SQS correspondientes

echo "🚀 Configurando reglas de EventBridge..."
echo ""

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

ENDPOINT_URL="http://localhost:4566"
REGION="us-east-1"
BUS_NAME="event-management-bus"
ACCOUNT_ID="000000000000"

# Verificar que LocalStack está corriendo
echo "⏳ Verificando LocalStack..."
if ! curl -s http://localhost:4566/_localstack/health > /dev/null; then
    echo "❌ Error: LocalStack no está corriendo"
    echo "   Ejecuta: docker-compose up -d"
    exit 1
fi
echo "✅ LocalStack está corriendo"
echo ""

# Verificar que el bus existe
echo "📋 Verificando bus de eventos..."
aws --endpoint-url=$ENDPOINT_URL events describe-event-bus \
    --name $BUS_NAME --region $REGION > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Error: El bus '$BUS_NAME' no existe."
    echo "   Ejecuta primero: bash init-eventbridge.sh"
    exit 1
fi
echo "✅ Bus '$BUS_NAME' encontrado"
echo ""

# Obtener ARN de la cola de notificaciones
NOTIFICATION_QUEUE_ARN="arn:aws:sqs:${REGION}:${ACCOUNT_ID}:notification-queue"

# Obtener ARN de la cola de booking
BOOKING_QUEUE_ARN="arn:aws:sqs:${REGION}:${ACCOUNT_ID}:booking-events-queue"

# ─────────────────────────────────────────────
# Regla 1: PaymentProcessed → notification-queue
# Cuando un pago se procesa exitosamente, notificar al usuario
# ─────────────────────────────────────────────
echo "📌 Regla 1: PaymentProcessed → notification-queue"
aws --endpoint-url=$ENDPOINT_URL events put-rule \
    --name "payment-confirmed-to-notifications" \
    --event-bus-name $BUS_NAME \
    --event-pattern '{
        "source": ["payment-service"],
        "detail-type": ["PaymentProcessed"]
    }' \
    --state ENABLED \
    --region $REGION > /dev/null

aws --endpoint-url=$ENDPOINT_URL events put-targets \
    --rule "payment-confirmed-to-notifications" \
    --event-bus-name $BUS_NAME \
    --targets "[{\"Id\":\"notification-queue-target\",\"Arn\":\"${NOTIFICATION_QUEUE_ARN}\"}]" \
    --region $REGION > /dev/null

echo "✅ PaymentProcessed → notification-queue"

# ─────────────────────────────────────────────
# Regla 2: PaymentFailed → notification-queue
# Cuando un pago falla, notificar al usuario
# ─────────────────────────────────────────────
echo "📌 Regla 2: PaymentFailed → notification-queue"
aws --endpoint-url=$ENDPOINT_URL events put-rule \
    --name "payment-failed-to-notifications" \
    --event-bus-name $BUS_NAME \
    --event-pattern '{
        "source": ["payment-service"],
        "detail-type": ["PaymentFailed"]
    }' \
    --state ENABLED \
    --region $REGION > /dev/null

aws --endpoint-url=$ENDPOINT_URL events put-targets \
    --rule "payment-failed-to-notifications" \
    --event-bus-name $BUS_NAME \
    --targets "[{\"Id\":\"notification-queue-target\",\"Arn\":\"${NOTIFICATION_QUEUE_ARN}\"}]" \
    --region $REGION > /dev/null

echo "✅ PaymentFailed → notification-queue"

# ─────────────────────────────────────────────
# Regla 3: EventPublished → notification-queue
# Cuando un evento se publica, notificar a interesados
# ─────────────────────────────────────────────
echo "📌 Regla 3: EventPublished → notification-queue"
aws --endpoint-url=$ENDPOINT_URL events put-rule \
    --name "event-published-to-notifications" \
    --event-bus-name $BUS_NAME \
    --event-pattern '{
        "source": ["event-service"],
        "detail-type": ["EventPublished"]
    }' \
    --state ENABLED \
    --region $REGION > /dev/null

aws --endpoint-url=$ENDPOINT_URL events put-targets \
    --rule "event-published-to-notifications" \
    --event-bus-name $BUS_NAME \
    --targets "[{\"Id\":\"notification-queue-target\",\"Arn\":\"${NOTIFICATION_QUEUE_ARN}\"}]" \
    --region $REGION > /dev/null

echo "✅ EventPublished → notification-queue"

# ─────────────────────────────────────────────
# Regla 4: EventCancelled → notification-queue
# Cuando un evento se cancela, notificar a afectados
# ─────────────────────────────────────────────
echo "📌 Regla 4: EventCancelled → notification-queue"
aws --endpoint-url=$ENDPOINT_URL events put-rule \
    --name "event-cancelled-to-notifications" \
    --event-bus-name $BUS_NAME \
    --event-pattern '{
        "source": ["event-service"],
        "detail-type": ["EventCancelled"]
    }' \
    --state ENABLED \
    --region $REGION > /dev/null

aws --endpoint-url=$ENDPOINT_URL events put-targets \
    --rule "event-cancelled-to-notifications" \
    --event-bus-name $BUS_NAME \
    --targets "[{\"Id\":\"notification-queue-target\",\"Arn\":\"${NOTIFICATION_QUEUE_ARN}\"}]" \
    --region $REGION > /dev/null

echo "✅ EventCancelled → notification-queue"

# ─────────────────────────────────────────────
# Regla 5: BookingCreated → notification-queue
# Cuando se crea una reserva, confirmar al usuario
# ─────────────────────────────────────────────
echo "📌 Regla 5: BookingCreated → notification-queue"
aws --endpoint-url=$ENDPOINT_URL events put-rule \
    --name "booking-created-to-notifications" \
    --event-bus-name $BUS_NAME \
    --event-pattern '{
        "source": ["booking-service"],
        "detail-type": ["BookingCreated"]
    }' \
    --state ENABLED \
    --region $REGION > /dev/null

aws --endpoint-url=$ENDPOINT_URL events put-targets \
    --rule "booking-created-to-notifications" \
    --event-bus-name $BUS_NAME \
    --targets "[{\"Id\":\"notification-queue-target\",\"Arn\":\"${NOTIFICATION_QUEUE_ARN}\"}]" \
    --region $REGION > /dev/null

echo "✅ BookingCreated → notification-queue"
echo ""

# ─────────────────────────────────────────────
# Regla 6: EventCreated → booking-events-queue
# Cuando se crea un evento, registrar disponibilidad en Booking Service
# ─────────────────────────────────────────────
echo "📌 Regla 6: EventCreated → booking-events-queue"
aws --endpoint-url=$ENDPOINT_URL events put-rule \
    --name "event-created-to-booking" \
    --event-bus-name $BUS_NAME \
    --event-pattern '{
        "source": ["event-service"],
        "detail-type": ["EventCreated"]
    }' \
    --state ENABLED \
    --region $REGION > /dev/null

aws --endpoint-url=$ENDPOINT_URL events put-targets \
    --rule "event-created-to-booking" \
    --event-bus-name $BUS_NAME \
    --targets "[{\"Id\":\"booking-queue-target\",\"Arn\":\"${BOOKING_QUEUE_ARN}\"}]" \
    --region $REGION > /dev/null

echo "✅ EventCreated → booking-events-queue"

# ─────────────────────────────────────────────
# Regla 7: EventCancelled → booking-events-queue
# Cuando se cancela un evento, cancelar reservas en Booking Service
# ─────────────────────────────────────────────
echo "📌 Regla 7: EventCancelled → booking-events-queue"
aws --endpoint-url=$ENDPOINT_URL events put-rule \
    --name "event-cancelled-to-booking" \
    --event-bus-name $BUS_NAME \
    --event-pattern '{
        "source": ["event-service"],
        "detail-type": ["EventCancelled"]
    }' \
    --state ENABLED \
    --region $REGION > /dev/null

aws --endpoint-url=$ENDPOINT_URL events put-targets \
    --rule "event-cancelled-to-booking" \
    --event-bus-name $BUS_NAME \
    --targets "[{\"Id\":\"booking-queue-target\",\"Arn\":\"${BOOKING_QUEUE_ARN}\"}]" \
    --region $REGION > /dev/null

echo "✅ EventCancelled → booking-events-queue"
echo ""

# ─────────────────────────────────────────────
# Mostrar resumen
# ─────────────────────────────────────────────
echo "📋 Reglas de EventBridge configuradas:"
aws --endpoint-url=$ENDPOINT_URL events list-rules \
    --event-bus-name $BUS_NAME \
    --region $REGION \
    --query 'Rules[*].{Name:Name,State:State}' \
    --output table

echo ""
echo "🔗 Arquitectura EDA configurada:"
echo "   Event Service   → EventBridge → notification-queue"
echo "   Booking Service → EventBridge → notification-queue"
echo "   Payment Service → EventBridge → notification-queue"
echo "   Booking Service → EventBridge ← Event Service"
echo ""
echo "🎉 ¡Reglas de EventBridge listas!"
