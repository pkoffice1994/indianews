#!/usr/bin/env bash
python manage.py migrate --run-syncdb
python setup_demo.py
gunicorn indianews.wsgi:application
