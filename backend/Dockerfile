# ============================================
# eFootball Arena — Backend Dockerfile
# Multi-stage optimized build
# ============================================

# ── Stage 1: Base Image ──────────────────────
FROM python:3.11-slim AS base

# منع Python من كتابة .pyc files وتفعيل stdout فوري
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# مجلد العمل داخل الـ container
WORKDIR /app

# ── Stage 2: Dependencies ─────────────────────
FROM base AS dependencies

# تثبيت system dependencies المطلوبة لـ psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# نسخ requirements أولاً — Docker cache layer optimization
COPY requirements.txt .

# تثبيت Python packages
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ── Stage 3: Final Image ──────────────────────
FROM dependencies AS final

# نسخ كل الكود
COPY . .

# إنشاء مجلدات الـ static و media
RUN mkdir -p /app/staticfiles /app/media

# ── Entrypoint Script ─────────────────────────
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Port الذي سيعمل عليه Django
EXPOSE 8000

# تشغيل entrypoint
ENTRYPOINT ["/entrypoint.sh"]