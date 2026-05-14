# ⚽ eFootball Arena

> منصة كرة القدم الإلكترونية الأولى — Built with Django + React + Docker

[![CI Pipeline](https://github.com/your-org/efootball-arena/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/efootball-arena/actions)
[![Coverage](https://codecov.io/gh/your-org/efootball-arena/badge.svg)](https://codecov.io/gh/your-org/efootball-arena)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Django 4.2](https://img.shields.io/badge/django-4.2-green.svg)](https://docs.djangoproject.com/en/4.2/)

---

## 📋 Project Overview

eFootball Arena is a full-stack platform for eFootball players featuring:
- **Tournaments** — Competitive bracket-based competitions
- **Tactics** — Community-driven tactical sharing
- **Marketplace** — Buy/sell game accounts
- **Notifications** — Real-time alerts and updates

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 + Django REST Framework |
| Database | PostgreSQL 15 |
| Cache / Queue | Redis 7 |
| Task Queue | Celery 5 + Celery Beat |
| Monitoring | Flower |
| Frontend | React 18 + Vite + Tailwind CSS |
| Auth | JWT (SimpleJWT) |
| CI/CD | GitHub Actions |
| Testing | Pytest + pytest-django |
| Containers | Docker + Docker Compose |

---

## 🚀 Quick Start

### Prerequisites
- Docker 24+
- Docker Compose 2+
- Git

### 1. Clone & Setup

```bash
git clone https://github.com/your-org/efootball-arena.git
cd efootball-arena
```

### 2. Environment Variables

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your values
```

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Verify Everything Works

```bash
# Check all services are running
docker-compose ps

# Check Django health
curl http://localhost:8765/health/

# Check deep readiness
curl http://localhost:8765/api/ready/
```

---

## ⚙️ Docker Services & Ports

| Service | URL | Port |
|---------|-----|------|
| Django Backend | http://localhost:8765 | 8765 |
| React Frontend | http://localhost:5500 | 5500 |
| PostgreSQL | localhost:5434 | 5434 |
| Redis | localhost:6379 | 6379 |
| Flower (Celery Monitor) | http://localhost:5555 | 5555 |

> **⚠️ Important:** Never change these ports — they're used throughout the project.

---

## 🔑 Environment Variables

Create `backend/.env`:

```env
# Django
SECRET_KEY=your-super-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,backend

# Database
DB_NAME=efootball_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432

# Redis / Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

---

## 🔗 API Base URL