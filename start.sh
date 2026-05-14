#!/usr/bin/env bash
echo "=== Running migrations ==="
python manage.py makemigrations --no-input 2>/dev/null || true
python manage.py migrate --run-syncdb --no-input

echo "=== Setup ==="
# Only add demo news if NO news exists yet (first time only)
NEWS_COUNT=$(python manage.py shell -c "from news.models import News; print(News.objects.count())" 2>/dev/null || echo "0")
if [ "$NEWS_COUNT" = "0" ]; then
  echo "=== First time: adding demo news ==="
  python manage.py add_news
else
  echo "=== News already exists ($NEWS_COUNT articles), skipping demo data ==="
  # Just clean duplicates
  python manage.py clean_duplicates
  # Ensure staff user exists
  python manage.py create_staff --username editor --password "IndiaNews@2026" --email "editor@indianews.in" --name "Editor" 2>/dev/null || true
fi

echo "=== Starting server ==="
gunicorn indianews.wsgi:application --log-level info --access-logfile - --error-logfile -
