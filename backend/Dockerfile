FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Pillow and basic utilities
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user to run the app
# RUN useradd -m appuser
# USER appuser

COPY . .

# Ensure the downloaded_images directory exists and has correct permissions
RUN mkdir -p downloaded_images

EXPOSE 1008

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "1008"]
