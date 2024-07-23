FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt /app/
COPY .env.dev /app/

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src/ /app/src

WORKDIR /app/src

ENV DJANGO_ENV=development
ENV DJANGO_SETTINGS_MODULE=config.settings

RUN python manage.py migrate

RUN python manage.py collectstatic --noinput

RUN python manage.py createcustomgroup

RUN python manage.py createptotype

RUN python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@luminari.com').exists() or User.objects.create_superuser(email='admin@luminari.com', password='luminari1!')"

# Expose the port Daphne will run on
EXPOSE 8000

# Start Daphne server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
