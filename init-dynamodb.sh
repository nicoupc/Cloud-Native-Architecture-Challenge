#!/bin/bash

# Script para inicializar DynamoDB en LocalStack
# Crea la tabla de Bookings con GSI para queries eficientes

echo "🚀 Inicializando DynamoDB para Booking Service..."

# Esperar a que LocalStack esté listo
echo "⏳ Esperando a que LocalStack esté disponible..."
until curl -s http://localhost:4566/_localstack/health | grep -q "\"dynamodb\": \"available\""; do
  echo "   Esperando DynamoDB..."
  sleep 2
done

echo "✅ LocalStack está listo!"

# Crear tabla de Bookings con GSI
echo "📦 Creando tabla 'Bookings' con índices GSI..."

awslocal dynamodb create-table \
  --table-name Bookings \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
    AttributeName=userId,AttributeType=S \
    AttributeName=eventId,AttributeType=S \
    AttributeName=createdAt,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --global-secondary-indexes \
    "[
      {
        \"IndexName\": \"UserBookingsIndex\",
        \"KeySchema\": [
          {\"AttributeName\": \"userId\", \"KeyType\": \"HASH\"},
          {\"AttributeName\": \"createdAt\", \"KeyType\": \"RANGE\"}
        ],
        \"Projection\": {\"ProjectionType\": \"ALL\"},
        \"ProvisionedThroughput\": {
          \"ReadCapacityUnits\": 5,
          \"WriteCapacityUnits\": 5
        }
      },
      {
        \"IndexName\": \"EventBookingsIndex\",
        \"KeySchema\": [
          {\"AttributeName\": \"eventId\", \"KeyType\": \"HASH\"},
          {\"AttributeName\": \"createdAt\", \"KeyType\": \"RANGE\"}
        ],
        \"Projection\": {\"ProjectionType\": \"ALL\"},
        \"ProvisionedThroughput\": {
          \"ReadCapacityUnits\": 5,
          \"WriteCapacityUnits\": 5
        }
      }
    ]" \
  --provisioned-throughput \
    ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-east-1

echo "✅ Tabla 'Bookings' creada exitosamente!"

# Verificar que la tabla existe
echo "🔍 Verificando tabla..."
awslocal dynamodb describe-table --table-name Bookings --region us-east-1 | grep TableName

echo ""
echo "✨ DynamoDB inicializado correctamente!"
echo ""
echo "📊 Estructura de la tabla:"
echo "   - Primary Key: PK (HASH), SK (RANGE)"
echo "   - GSI 1: UserBookingsIndex (userId + createdAt)"
echo "   - GSI 2: EventBookingsIndex (eventId + createdAt)"
echo ""
echo "🧪 Para probar:"
echo "   awslocal dynamodb scan --table-name Bookings"
