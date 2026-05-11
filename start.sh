#!/usr/bin/env bash
echo "=== Running migrations ==="
python manage.py makemigrations --no-input 2>/dev/null || true
python manage.py migrate --run-syncdb --no-input
echo "=== Adding news & epaper data ==="
python manage.py add_news
echo "=== Starting server ==="
gunicorn indianews.wsgi:application --log-level info --access-logfile - --error-logfile -
