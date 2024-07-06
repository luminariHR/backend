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

# Collect static files
# RUN python manage.py collectstatic --noinput

# Copy entrypoint script
COPY docker/api/entrypoint.sh /app/entrypoint.sh

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

RUN /app/entrypoint.sh

# Expose the port Daphne will run on
EXPOSE 8000

WORKDIR /app/src

# Start Daphne server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
