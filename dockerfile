# Use Python 3.13 to match your local 3.13.4
FROM python:3.13-slim

# Faster startup logs, no .pyc
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_PATH=/app/data/app.sqlite

WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Ensure the SQLite data dir exists (image side)
RUN mkdir -p /app/data

EXPOSE 5000

# Make sure app.py binds 0.0.0.0:5000 (you already set this)
CMD ["python", "app.py"]
