#!/bin/bash

# Script de inicialización de CloudWatch Logs en LocalStack
# Crea los log groups para todos los microservicios

echo "🚀 Inicializando CloudWatch Logs en LocalStack..."
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

# Crear log groups para cada microservicio
echo "📋 Creando CloudWatch Log Groups..."
echo ""

for service in event-service booking-service payment-service notification-service; do
    log_group="/aws/${service}"
    echo "  📦 Creando log group: ${log_group}"
    aws --endpoint-url=http://localhost:4566 logs create-log-group \
        --log-group-name "${log_group}" \
        --region us-east-1 2>&1 | grep -v "already exists" || true
done

echo ""
echo "✅ CloudWatch Log Groups creados!"
echo ""

echo "📋 Log groups disponibles:"
aws --endpoint-url=http://localhost:4566 logs describe-log-groups \
    --region us-east-1 \
    --query 'logGroups[].logGroupName' \
    --output table 2>/dev/null || echo "   (ejecuta el comando manualmente para verificar)"

echo ""
echo "💡 Para ver los logs de un servicio:"
echo "   aws --endpoint-url=http://localhost:4566 logs filter-log-events --log-group-name /aws/event-service"
echo ""
echo "🎉 ¡CloudWatch Logs listo!"
