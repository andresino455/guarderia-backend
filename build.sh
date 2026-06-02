#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createcachetable
python manage.py crear_datos_iniciales
python manage.py reset_admin
python manage.py crear_superusuario  