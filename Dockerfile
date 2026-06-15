FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Веб-панель слушает порт из переменной WEB_PORT (по умолчанию 8000)
EXPOSE 8000

CMD ["python", "main.py"]
