#!/bin/bash

# Script para inicializar DynamoDB en LocalStack
# Crea la tabla de Payment Sagas para el Payment Service

echo "🚀 Inicializando DynamoDB para Payment Service..."

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

# Verificar que LocalStack está corriendo
echo "⏳ Verificando LocalStack..."
if ! curl -s http://localhost:4566/_localstack/health | grep -q "dynamodb"; then
    echo "❌ Error: LocalStack no está corriendo"
    echo "   Ejecuta: docker-compose up -d"
    exit 1
fi

echo "✅ LocalStack está listo!"

# Verificar si la tabla ya existe
if aws --endpoint-url=http://localhost:4566 dynamodb describe-table \
    --table-name payment-sagas --region us-east-1 > /dev/null 2>&1; then
    echo "✅ La tabla 'payment-sagas' ya existe"
    exit 0
fi

# Crear tabla con GSI
echo "📦 Creando tabla 'payment-sagas'..."

aws --endpoint-url=http://localhost:4566 dynamodb create-table \
  --table-name payment-sagas \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
    AttributeName=bookingId,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --global-secondary-indexes \
    '[{"IndexName":"BookingIdIndex","KeySchema":[{"AttributeName":"bookingId","KeyType":"HASH"}],"Projection":{"ProjectionType":"ALL"},"ProvisionedThroughput":{"ReadCapacityUnits":5,"WriteCapacityUnits":5}}]' \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-east-1

echo "✅ Tabla 'payment-sagas' creada exitosamente!"
echo ""
echo "📊 Estructura de la tabla:"
echo "   - Primary Key: PK (HASH), SK (RANGE)"
echo "   - GSI: BookingIdIndex (bookingId)"
echo ""
echo "🎉 ¡Listo! Ahora puedes ejecutar el Payment Service"
