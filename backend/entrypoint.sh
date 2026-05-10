#!/bin/bash
set -e

echo "🔄 Waiting for PostgreSQL to be ready..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  echo "⏳ PostgreSQL is not ready yet — sleeping 1s..."
  sleep 1
done

echo "✅ PostgreSQL is ready!"

# تأكد إن DJANGO_SETTINGS_MODULE موجود
echo "📋 DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
echo "📋 DB_HOST=$DB_HOST | DB_PORT=$DB_PORT | DB_NAME=$DB_NAME"

echo "🔄 Running database migrations..."
python manage.py migrate --noinput

echo "🔄 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000