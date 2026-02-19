#!/bin/bash

echo "Esperando a que la base de datos en db:5432 esté lista..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "¡Base de datos lista!"

echo "Aplicando migraciones de base de datos..."
alembic upgrade head

echo "Iniciando servidor FastAPI..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000