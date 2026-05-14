# ============================================
# eFootball Arena — Test Factories
# Factory Boy + Faker for Realistic Test Data
# ============================================

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker()

User = get_user_model()


# ============================================
# 👤 USER FACTORIES
# ============================================


class UserFactory(DjangoModelFactory):
    """
    Factory لإنشاء مستخدمين عاديين للاختبار.

    الاستخدام:
        # مستخدم واحد
        user = UserFactory()

        # مستخدم بـ username محدد
        user = UserFactory(username='myplayer')

        # 10 مستخدمين
        users = UserFactory.create_batch(10)

        # مستخدم بكلمة مرور معينة
        user = UserFactory(password='CustomPass123!')
    """

    class Meta:
        model = User
        # تجنب تكرار username
        django_get_or_create = ("username",)

    # ── Basic Fields ───────────────────────────────────────────────────────
    username = factory.LazyFunction(
        lambda: f"player_{fake.unique.user_name()[:15]}"
    )
    email = factory.LazyAttribute(
        lambda obj: f"{obj.username}@arena.com"
    )
    first_name = factory.LazyFunction(fake.first_name)
    last_name = factory.LazyFunction(fake.last_name)

    # ── Profile Fields ─────────────────────────────────────────────────────
    bio = factory.LazyFunction(lambda: fake.sentence(nb_words=10))
    country = factory.LazyFunction(
        lambda: fake.random_element(["EG", "SA", "AE", "KW", "QA", "MA"])
    )
    favorite_team = factory.LazyFunction(
        lambda: fake.random_element(
            ["Al Ahly", "Zamalek", "Barcelona", "Real Madrid", "Manchester City"]
        )
    )
    rank_level = factory.LazyFunction(
        lambda: fake.random_element(
            ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Legend"]
        )
    )
    rating = factory.LazyFunction(lambda: fake.pyfloat(min_value=800, max_value=3000))
    is_active = True
    is_verified = False

    # ── Password ───────────────────────────────────────────────────────────
    # لا نخزن الباسورد مباشرة — نستخدم set_password
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override لاستخدام set_password."""
        password = kwargs.pop("password", "TestPass123!")
        manager = cls._get_manager(model_class)
        user = manager.create_user(password=password, **kwargs)
        return user

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        """Override للـ build strategy."""
        kwargs.pop("password", None)
        return super()._build(model_class, *args, **kwargs)


class AdminUserFactory(UserFactory):
    """
    Factory لإنشاء مستخدمين بصلاحيات Admin.

    الاستخدام:
        admin = AdminUserFactory()
        assert admin.is_staff == True
        assert admin.is_superuser == True
    """

    username = factory.LazyFunction(
        lambda: f"admin_{fake.unique.user_name()[:10]}"
    )
    email = factory.LazyAttribute(
        lambda obj: f"{obj.username}@admin.arena.com"
    )
    is_staff = True
    is_superuser = True
    is_verified = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """إنشاء superuser."""
        password = kwargs.pop("password", "AdminPass123!")
        manager = cls._get_manager(model_class)
        user = manager.create_superuser(password=password, **kwargs)
        return user


class VerifiedUserFactory(UserFactory):
    """
    Factory لإنشاء مستخدمين موثقين.

    الاستخدام:
        verified_user = VerifiedUserFactory()
        assert verified_user.is_verified == True
    """

    is_verified = True
    rank_level = "Gold"
    rating = factory.LazyFunction(lambda: fake.pyfloat(min_value=1500, max_value=3000))


class BronzeUserFactory(UserFactory):
    """
    Factory لإنشاء مستخدمين بمستوى Bronze (الافتراضي).

    الاستخدام:
        new_player = BronzeUserFactory()
        assert new_player.rank_level == 'Bronze'
    """

    rank_level = "Bronze"
    rating = 1000.0
    matches_played = 0
    wins = 0
    losses = 0


class LegendUserFactory(UserFactory):
    """
    Factory لإنشاء مستخدمين بمستوى Legend.

    الاستخدام:
        legend = LegendUserFactory()
        assert legend.rank_level == 'Legend'
    """

    rank_level = "Legend"
    rating = factory.LazyFunction(lambda: fake.pyfloat(min_value=2500, max_value=3000))
    matches_played = factory.LazyFunction(lambda: fake.random_int(min=500, max=2000))
    wins = factory.LazyAttribute(
        lambda obj: int(obj.matches_played * 0.75)
    )
    losses = factory.LazyAttribute(
        lambda obj: obj.matches_played - obj.wins
    )
    is_verified = True