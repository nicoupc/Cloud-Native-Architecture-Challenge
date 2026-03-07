#!/bin/bash

# Script de inicialización de PostgreSQL RDS en LocalStack
# Crea la base de datos para el Event Service

echo "🚀 Inicializando PostgreSQL RDS en LocalStack..."
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

# Crear la instancia de PostgreSQL RDS
echo "📦 Creando instancia PostgreSQL RDS..."
echo ""

# Configurar credenciales dummy para LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

aws --endpoint-url=http://localhost:4566 rds create-db-instance \
    --db-instance-identifier events-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 14.7 \
    --master-username postgres \
    --master-user-password postgres \
    --allocated-storage 20 \
    --db-name events_db \
    --port 4510 \
    --region us-east-1 2>&1 | grep -v "DBInstance"

echo ""
echo "⏳ Esperando a que PostgreSQL esté listo (esto puede tomar 30-60 segundos)..."

# Esperar a que PostgreSQL esté realmente disponible
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if psql -h localhost -p 4510 -U postgres -d events_db -c "SELECT 1" > /dev/null 2>&1; then
        echo "✅ PostgreSQL está listo!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Intento $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "⚠️  PostgreSQL tardó más de lo esperado, pero puede estar listo"
    echo "   Intenta ejecutar el Event Service de todas formas"
else
    echo ""
    echo "✅ Base de datos PostgreSQL lista para usar!"
fi

echo ""
echo "📋 Detalles de conexión:"
echo "   Host: localhost"
echo "   Port: 4510"
echo "   Database: events_db"
echo "   Username: postgres"
echo "   Password: postgres"
echo ""
echo "💡 Para conectarte con psql:"
echo "   psql -h localhost -p 4510 -U postgres -d events_db"
echo ""
echo "💡 Para ver las tablas después de ejecutar el servicio:"
echo "   psql -h localhost -p 4510 -U postgres -d events_db -c '\\dt'"
echo ""
echo "🎉 ¡Listo! Ahora puedes ejecutar el Event Service"
