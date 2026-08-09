FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x scripts/entrypoint.sh

ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

EXPOSE 5000

ENTRYPOINT ["scripts/entrypoint.sh"]
