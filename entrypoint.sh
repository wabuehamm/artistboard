#!/usr/bin/env sh

. /app/.venv/bin/activate

python manage.py migrate

if [ ! -f .superuser_created ]
then
    if [ -z "$DJANGO_SUPERUSER_USERNAME" ]
    then
        echo "Missing DJANGO_SUPERUSER_USERNAME environment variable"
        exit 1
    fi

    if [ -z "$DJANGO_SUPERUSER_PASSWORD" ]
    then
        echo "Missing DJANGO_SUPERUSER_PASSWORD environment variable"
        exit 1
    fi

    if [ -z "$DJANGO_SUPERUSER_EMAIL" ]
    then
        echo "Missing DJANGO_SUPERUSER_EMAIL environment variable"
        exit 1
    fi

    if python manage.py createsuperuser --noinput
    then
        touch .superuser_created
    fi
fi

daphne -b 0.0.0.0 -p 8000 artistboardsite.asgi:application