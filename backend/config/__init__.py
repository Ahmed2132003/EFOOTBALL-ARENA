# ============================================
# eFootball Arena — Config Package Init
# تحميل Celery عند تشغيل Django
# ============================================

# استيراد celery_app عند بدء تشغيل Django
# هذا يضمن أن Celery يعمل فور تحميل الـ package
# وضروري لـ shared_task decorator في كل مكان
from .celery import app as celery_app

__all__ = ("celery_app",)