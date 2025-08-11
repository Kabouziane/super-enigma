#!/usr/bin/env bash
export PYTHONPATH=.
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
