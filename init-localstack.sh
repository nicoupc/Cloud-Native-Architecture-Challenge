#!/bin/bash

# Script de inicialización de LocalStack
# Este script crea la base de datos PostgreSQL en LocalStack

echo "🚀 Inicializando LocalStack..."

# Esperar a que LocalStack esté listo
echo "⏳ Esperando a que LocalStack esté disponible..."
until curl -s http://localhost:4566/_localstack/health | grep -q '"rds": "available"'; do
    echo "   Esperando RDS..."
    sleep 2
done

echo "✅ LocalStack está listo!"

# Crear la base de datos PostgreSQL
echo "📦 Creando base de datos PostgreSQL..."

awslocal rds create-db-instance \
    --db-instance-identifier events-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 14.7 \
    --master-username test \
    --master-user-password test \
    --allocated-storage 20 \
    --db-name events_db \
    --port 4510

echo "✅ Base de datos PostgreSQL creada!"
echo ""
echo "📋 Detalles de conexión:"
echo "   Host: localhost"
echo "   Port: 4510"
echo "   Database: events_db"
echo "   Username: test"
echo "   Password: test"
echo ""
echo "🎉 LocalStack inicializado correctamente!"
