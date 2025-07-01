#!/bin/bash
set -e
until cd /app
do
    echo "Waiting for server volume..."
done
until python manage.py migrate
do
    echo "Waiting for postgres ready..."
    sleep 2
done

python manage.py collectstatic --noinput

python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME',
                                '$DJANGO_SUPERUSER_EMAIL',
                                '$DJANGO_SUPERUSER_PASSWORD')
"

exec "$@"