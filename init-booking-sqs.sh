#!/bin/bash

# Script para inicializar SQS en LocalStack
# Crea la cola principal y la Dead Letter Queue para el Booking Service
# También crea la tabla DynamoDB EventAvailability

echo "🚀 Inicializando SQS para Booking Service..."

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

ENDPOINT_URL="http://localhost:4566"
REGION="us-east-1"

# Verificar que LocalStack está corriendo
echo "⏳ Verificando LocalStack..."
if ! curl -s http://localhost:4566/_localstack/health | grep -q "sqs"; then
    echo "❌ Error: LocalStack no está corriendo"
    echo "   Ejecuta: docker-compose up -d"
    exit 1
fi

echo "✅ LocalStack está listo!"

# Crear Dead Letter Queue primero
echo "📦 Creando Dead Letter Queue (booking-events-dlq)..."
DLQ_URL=$(aws --endpoint-url=$ENDPOINT_URL sqs create-queue \
  --queue-name booking-events-dlq \
  --region $REGION \
  --attributes MessageRetentionPeriod=345600 \
  --query 'QueueUrl' \
  --output text)

echo "✅ DLQ creada: $DLQ_URL"

# Obtener ARN de la DLQ
DLQ_ARN=$(aws --endpoint-url=$ENDPOINT_URL sqs get-queue-attributes \
  --queue-url $DLQ_URL \
  --attribute-names QueueArn \
  --region $REGION \
  --query 'Attributes.QueueArn' \
  --output text)

echo "📋 DLQ ARN: $DLQ_ARN"

# Crear cola principal (sin RedrivePolicy primero)
echo "📦 Creando cola principal (booking-events-queue)..."
QUEUE_URL=$(aws --endpoint-url=$ENDPOINT_URL sqs create-queue \
  --queue-name booking-events-queue \
  --region $REGION \
  --attributes VisibilityTimeout=30,MessageRetentionPeriod=345600,ReceiveMessageWaitTimeSeconds=20 \
  --query 'QueueUrl' \
  --output text)

echo "✅ Cola principal creada: $QUEUE_URL"

# Asignar política de reenvío a DLQ
echo "🔗 Configurando RedrivePolicy hacia DLQ..."
aws --endpoint-url=$ENDPOINT_URL sqs set-queue-attributes \
  --queue-url "$QUEUE_URL" \
  --region $REGION \
  --attributes "{\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"${DLQ_ARN}\\\",\\\"maxReceiveCount\\\":\\\"3\\\"}\"}"

echo "✅ Cola principal creada: $QUEUE_URL"

# Crear tabla DynamoDB EventAvailability
echo ""
echo "📦 Creando tabla DynamoDB EventAvailability..."
aws --endpoint-url=$ENDPOINT_URL dynamodb create-table \
  --table-name EventAvailability \
  --attribute-definitions AttributeName=eventId,AttributeType=S \
  --key-schema AttributeName=eventId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Tabla EventAvailability creada"
else
    echo "⚠️  Tabla EventAvailability ya existe o hubo un error"
fi

echo ""
echo "📋 Colas disponibles:"
aws --endpoint-url=$ENDPOINT_URL sqs list-queues --region $REGION --query 'QueueUrls' --output table

echo ""
echo "✅ SQS inicializado correctamente!"
echo ""
echo "📊 Configuración:"
echo "   - Cola principal: booking-events-queue"
echo "   - Dead Letter Queue: booking-events-dlq"
echo "   - Visibility Timeout: 30 segundos"
echo "   - Retención de mensajes: 4 días (principal), 4 días (DLQ)"
echo "   - Máximo reintentos: 3 (luego pasa a DLQ)"
echo "   - Long Polling: 20 segundos"
echo "   - Tabla DynamoDB: EventAvailability (PK: eventId)"
echo ""
echo "🎉 ¡Listo! Ahora puedes ejecutar el Booking Service"
