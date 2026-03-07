#!/bin/bash

# Script de inicialización de EventBridge en LocalStack
# Crea el bus de eventos para el Event Service

echo "🚀 Inicializando EventBridge en LocalStack..."
echo ""

# Verificar que LocalStack está corriendo
echo "⏳ Verificando LocalStack..."
if ! curl -s http://localhost:4566/_localstack/health > /dev/null; then
    echo "❌ Error: LocalStack no está corriendo"
    echo "   Ejecuta: docker-compose up -d"
    exit 1
fi

echo "✅ LocalStack está corriendo"
echo ""

# Configurar credenciales dummy para LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

# Crear el bus de eventos
echo "📦 Creando bus de eventos 'event-management-bus'..."
echo ""

aws --endpoint-url=http://localhost:4566 events create-event-bus \
    --name event-management-bus \
    --region us-east-1 2>&1 | grep -v "EventBusArn"

echo ""
echo "✅ Bus de eventos creado!"
echo ""

# Listar buses de eventos
echo "📋 Buses de eventos disponibles:"
aws --endpoint-url=http://localhost:4566 events list-event-buses \
    --region us-east-1 \
    --query 'EventBuses[*].Name' \
    --output table

echo ""
echo "💡 Para ver eventos publicados, usa:"
echo "   aws --endpoint-url=http://localhost:4566 events list-rules --event-bus-name event-management-bus"
echo ""
echo "🎉 ¡Listo! EventBridge está configurado"
