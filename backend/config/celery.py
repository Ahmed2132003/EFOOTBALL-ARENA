# ============================================
# eFootball Arena — Celery Configuration
# Production-Ready Async Task Processing
# ============================================

import os
from celery import Celery
from django.conf import settings

# تحديد Django settings module لـ Celery
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings.development"
)

# إنشاء Celery application باسم "config"
# هذا الاسم يطابق اسم Django project package
app = Celery("config")

# ─── Load Configuration ──────────────────────────────────────────────────────
# قراءة جميع إعدادات Celery من Django settings
# namespace="CELERY" يعني أن كل إعداد Celery في settings يبدأ بـ CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# ─── Auto Discover Tasks ─────────────────────────────────────────────────────
# Celery يكتشف تلقائياً tasks.py في كل app مُثبتة
# هذا يعني إضافة task جديد في أي app يتم اكتشافه تلقائياً
app.autodiscover_tasks()


# ─── Debug Task ──────────────────────────────────────────────────────────────
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Task للتشخيص — تطبع معلومات الـ request الحالي.
    الاستخدام: debug_task.delay()
    """
    print(f"[DEBUG TASK] Request: {self.request!r}")