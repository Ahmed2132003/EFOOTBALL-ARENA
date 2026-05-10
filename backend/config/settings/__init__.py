# ============================================
# eFootball Arena — Settings Router
# يختار settings المناسب حسب البيئة
# ============================================

from decouple import config

# قراءة نوع البيئة من .env — default: development
environment = config("DJANGO_SETTINGS_MODULE", default="config.settings.development")