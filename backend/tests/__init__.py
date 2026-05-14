# ============================================
# eFootball Arena — Tests Package
# ============================================
#
# هيكل الاختبارات:
# ─────────────────
# tests/
# ├── __init__.py          ← هذا الملف
# ├── conftest.py          ← Fixtures مشتركة
# ├── factories.py         ← Factory Boy للبيانات
# ├── test_auth_flow.py    ← اختبارات المصادقة
# ├── test_profile.py      ← اختبارات البروفايل
# └── test_health_checks.py ← اختبارات الصحة
#
# ─────────────────
# كيفية إضافة اختبارات جديدة:
# ─────────────────
# 1. أنشئ ملف test_<feature>.py في هذا المجلد
# 2. استورد الـ fixtures من conftest.py
# 3. استخدم factories.py لإنشاء البيانات
# 4. شغّل: docker-compose exec backend pytest tests/test_<feature>.py
# ─────────────────