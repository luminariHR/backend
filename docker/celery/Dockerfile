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

CMD ["celery", "-A", "config", "worker", "--loglevel=info"]
