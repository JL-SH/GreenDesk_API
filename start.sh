#!/bin/bash
set -e  

echo "Esperando a que la base de datos esté lista..."
until pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER}"; do
  echo "BD no disponible, reintentando en 1s..."
  sleep 1
done
echo "¡Base de datos lista!"

echo "Aplicando migraciones..."
alembic upgrade head

echo "Iniciando FastAPI..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000