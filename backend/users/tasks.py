# ============================================
# eFootball Arena — Users Celery Tasks
# Async Background Jobs for User Operations
# ============================================

import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

# Logger خاص بـ tasks — يظهر في Celery Worker logs
logger = logging.getLogger("users.tasks")


# ============================================
# 📧 TASK 1: Send Welcome Email
# ============================================

@shared_task(
    # اسم واضح يظهر في Flower Dashboard
    name="users.tasks.send_welcome_email",

    # إعادة المحاولة تلقائياً عند هذه الأخطاء
    autoretry_for=(Exception,),

    # Exponential backoff: 60s → 120s → 240s
    retry_backoff=True,
    retry_backoff_max=600,   # أقصى انتظار 10 دقائق

    # عدد المحاولات القصوى
    max_retries=3,

    # لا نحتاج نتيجة هذه المهمة
    ignore_result=False,

    # لا نرسل بريد لمستخدم محذوف
    acks_late=True,
)
def send_welcome_email(user_id: int) -> dict:
    """
    إرسال بريد ترحيبي بعد تسجيل مستخدم جديد.

    Args:
        user_id: معرف المستخدم في قاعدة البيانات

    Returns:
        dict: حالة الإرسال ومعلومات المستخدم

    الاستخدام:
        send_welcome_email.delay(user.id)  # من RegisterView
        send_welcome_email.apply_async(args=[user.id], countdown=5)  # بعد 5 ثوانٍ
    """
    # استيراد داخل الـ task لتجنب circular imports
    from django.contrib.auth import get_user_model
    User = get_user_model()

    logger.info(f"📧 Sending welcome email | user_id={user_id}")

    try:
        # جلب المستخدم من قاعدة البيانات
        user = User.objects.get(id=user_id)

    except User.DoesNotExist:
        # المستخدم غير موجود — لا نعيد المحاولة
        logger.warning(f"⚠️ User not found | user_id={user_id} | Skipping.")
        return {"status": "skipped", "reason": "user_not_found", "user_id": user_id}

    # ─── Build Email Content ────────────────────────────────────────────────
    subject = f"🎮 Welcome to eFootball Arena, {user.username}!"

    message = f"""
مرحباً {user.username}! 👋

أهلاً بك في eFootball Arena — منصة كرة القدم الإلكترونية الأولى!

حسابك الآن جاهز:
━━━━━━━━━━━━━━━━━━━━
👤 اسم المستخدم: {user.username}
📧 البريد الإلكتروني: {user.email}
🥉 المستوى الحالي: {user.rank_level}
⭐ التقييم: {user.rating} نقطة

ماذا يمكنك فعله الآن؟
━━━━━━━━━━━━━━━━━━━━
🏆 انضم للبطولات الأسبوعية
📋 شارك تكتيكاتك مع المجتمع
💰 تصفح السوق وتداول الحسابات
📊 ارتقِ بالرانك وأثبت نفسك

نتمنى لك تجربة رائعة!
فريق eFootball Arena ⚽
    """.strip()

    # ─── Send Email ─────────────────────────────────────────────────────────
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,  # نريد معرفة الأخطاء
        )

        logger.info(
            f"✅ Welcome email sent successfully | "
            f"user_id={user_id} | username={user.username} | "
            f"email={user.email}"
        )

        return {
            "status": "success",
            "user_id": user_id,
            "username": user.username,
            "email": user.email,
        }

    except Exception as exc:
        logger.error(
            f"❌ Failed to send welcome email | "
            f"user_id={user_id} | error={str(exc)}"
        )
        # إعادة raise لتفعيل autoretry
        raise exc


# ============================================
# 📊 TASK 2: Daily Rank Update
# ============================================

@shared_task(
    name="users.tasks.daily_rank_update",
    # لا نريد retry تلقائي — مهمة مجدولة ستعاد غداً
    autoretry_for=(),
    max_retries=0,
    ignore_result=False,
    acks_late=True,
)
def daily_rank_update() -> dict:
    """
    تحديث الرانك اليومي لجميع المستخدمين.

    يتم تشغيلها تلقائياً كل يوم الساعة 2 صباحاً
    عبر Celery Beat Scheduler.

    حالياً: تسجيل Log فقط
    مستقبلاً: حساب وتحديث رانك كل لاعب بناءً على:
        - نسبة الفوز
        - عدد المباريات
        - التقييم الحالي
        - النشاط الأسبوعي

    الاستخدام اليدوي:
        daily_rank_update.delay()
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    logger.info("🏆 Starting daily rank update task...")

    try:
        # جلب عدد المستخدمين النشطين
        active_users_count = User.objects.filter(is_active=True).count()

        logger.info(
            f"📊 Daily rank update | "
            f"active_users={active_users_count} | "
            f"status=completed (placeholder)"
        )

        # ─── TODO: Rank Calculation Logic ──────────────────────────────────
        # في الإصدار القادم سيتم تطبيق:
        #
        # for user in User.objects.filter(is_active=True):
        #     new_rank = calculate_rank(user.rating, user.win_rate)
        #     if new_rank != user.rank_level:
        #         old_rank = user.rank_level
        #         user.rank_level = new_rank
        #         user.save(update_fields=["rank_level", "updated_at"])
        #         # إرسال إشعار ترقية الرانك
        #         notify_rank_change.delay(user.id, old_rank, new_rank)
        # ───────────────────────────────────────────────────────────────────

        return {
            "status": "success",
            "users_processed": active_users_count,
            "message": "Daily rank update completed (placeholder)",
        }

    except Exception as exc:
        logger.error(f"❌ Daily rank update failed | error={str(exc)}")
        raise exc


# ============================================
# 📱 TASK 3: Send Notification Email (Future)
# ============================================

@shared_task(
    name="users.tasks.send_notification_email",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
    ignore_result=False,
)
def send_notification_email(user_id: int, subject: str, message: str) -> dict:
    """
    إرسال بريد إلكتروني للإشعارات العامة.

    Args:
        user_id: معرف المستخدم
        subject: عنوان البريد
        message: محتوى البريد

    الاستخدام:
        send_notification_email.delay(
            user_id=1,
            subject="You won the tournament!",
            message="Congratulations..."
        )
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    logger.info(f"📱 Sending notification email | user_id={user_id}")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.warning(f"⚠️ User not found | user_id={user_id}")
        return {"status": "skipped", "reason": "user_not_found"}

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f"✅ Notification email sent | user_id={user_id}")
        return {"status": "success", "user_id": user_id}

    except Exception as exc:
        logger.error(f"❌ Notification email failed | user_id={user_id} | error={str(exc)}")
        raise exc