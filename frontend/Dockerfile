# ============================================
# eFootball Arena — Frontend Dockerfile
# Node 18 + Vite + Hot Reload
# ============================================

FROM node:18-alpine AS base

WORKDIR /app

# ── Dependencies Stage ────────────────────────
FROM base AS dependencies

# نسخ package.json فقط — بدون package-lock.json لأنه مش موجود بعد
COPY package.json ./

# npm install بدل npm ci لأن package-lock.json مش موجود بعد
# بعد أول build هيتولد package-lock.json وممكن نرجع npm ci
RUN npm install

# ── Development Stage ─────────────────────────
FROM dependencies AS development

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]