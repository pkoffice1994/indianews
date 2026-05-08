#!/usr/bin/env bash
set -x
echo "=== Starting migrate ==="
python manage.py migrate --run-syncdb 2>&1
echo "=== Running setup_demo ==="
python setup_demo.py 2>&1
echo "=== Starting gunicorn ==="
gunicorn indianews.wsgi:application --log-level debug --access-logfile - --error-logfile -
