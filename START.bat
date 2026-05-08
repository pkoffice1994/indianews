@echo off
echo.
echo ========================================
echo   INDIA NEWS — Starting Server
echo ========================================
echo.

IF NOT EXIST "venv\Scripts\activate" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing packages...
pip install -r requirements.txt --quiet

echo Setting up database...
python manage.py migrate --run-syncdb

echo Collecting static files...
python manage.py collectstatic --no-input --quiet

echo.
echo ========================================
echo   Server running at:
echo   http://127.0.0.1:8000
echo   Admin: http://127.0.0.1:8000/admin
echo ========================================
echo.

set DEBUG=True
python manage.py runserver
