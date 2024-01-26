#!/bin/bash
set -e

# Migrate the database
python3 /backend/manage.py makemigrations
python3 /backend/manage.py migrate

# Check if the superuser already exists
USER_EXISTS=$(python3 /backend/manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='$DJANGO_NAME').exists())")

if [ "$USER_EXISTS" = "False" ]; then
    echo "Creating superuser $DJANGO_NAME"
    export DJANGO_SUPERUSER_PASSWORD=$DJANGO_PASSWORD
    python3 /backend/manage.py createsuperuser \
        --no-input \
        --username=$DJANGO_NAME \
        --email=$DJANGO_NAME@example.com
else
    echo "Superuser $DJANGO_NAME already exists. Skipping creation."
fi
