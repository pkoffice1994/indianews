#!/bin/bash
echo ""
echo "========================================"
echo "  INDIA NEWS — Starting Server"
echo "========================================"
echo ""

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing packages..."
pip install -r requirements.txt -q

echo "Setting up database..."
python manage.py migrate --run-syncdb

echo "Collecting static files..."
python manage.py collectstatic --no-input -v 0

echo ""
echo "========================================"
echo "  Open in browser:"
echo "  http://127.0.0.1:8000"
echo "  Admin: http://127.0.0.1:8000/admin"
echo "========================================"
echo ""

export DEBUG=True
python manage.py runserver
