#!/bin/bash
# Run migrations
python manage.py migrate

python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'luminari1!')"

# Start Daphne server
exec "$@"
