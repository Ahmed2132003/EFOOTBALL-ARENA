# ============================================
# eFootball Arena — Profile Integration Tests
# Profile CRUD + Avatar + Password Change
# ============================================

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from tests.factories import UserFactory

User = get_user_model()


# ============================================
# 👤 MY PROFILE TESTS
# ============================================


@pytest.mark.django_db
class TestMyProfileAPI:
    """اختبارات My Profile endpoint."""

    def test_get_my_profile_authenticated(
        self, authenticated_client, profile_urls, regular_user
    ):
        """استرجاع البروفايل الخاص ينجح."""
        response = authenticated_client.get(profile_urls["my_profile"])

        assert response.status_code == status.HTTP_200_OK
        assert "profile" in response.data
        profile = response.data["profile"]
        assert profile["username"] == regular_user.username

    def test_get_my_profile_unauthenticated_fails(self, api_client, profile_urls):
        """استرجاع البروفايل بدون مصادقة يُرجع 401."""
        response = api_client.get(profile_urls["my_profile"])
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_contains_required_fields(
        self, authenticated_client, profile_urls
    ):
        """البروفايل يحتوي على الحقول المطلوبة."""
        response = authenticated_client.get(profile_urls["my_profile"])
        profile = response.data["profile"]

        required_fields = [
            "id",
            "username",
            "email",
            "rank_level",
            "rating",
            "matches_played",
            "wins",
            "losses",
            "draws",
            "win_rate",
        ]
        for field in required_fields:
            assert field in profile, f"Field '{field}' missing from profile response"

    def test_profile_doesnt_return_password(
        self, authenticated_client, profile_urls
    ):
        """البروفايل لا يُرجع كلمة المرور."""
        response = authenticated_client.get(profile_urls["my_profile"])
        profile = response.data["profile"]
        assert "password" not in profile

    def test_update_profile_bio(self, authenticated_client, profile_urls):
        """تحديث bio ينجح."""
        response = authenticated_client.patch(
            profile_urls["my_profile"],
            {"bio": "Best eFootball player in Egypt!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["profile"]["bio"] == "Best eFootball player in Egypt!"

    def test_update_profile_country(self, authenticated_client, profile_urls):
        """تحديث country ينجح."""
        response = authenticated_client.patch(
            profile_urls["my_profile"],
            {"country": "Saudi Arabia"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["profile"]["country"] == "Saudi Arabia"

    def test_update_profile_favorite_team(
        self, authenticated_client, profile_urls
    ):
        """تحديث favorite_team ينجح."""
        response = authenticated_client.patch(
            profile_urls["my_profile"],
            {"favorite_team": "Al Ahly"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["profile"]["favorite_team"] == "Al Ahly"

    def test_update_profile_multiple_fields(
        self, authenticated_client, profile_urls
    ):
        """تحديث عدة حقول في نفس الوقت."""
        update_data = {
            "bio": "Champion player",
            "country": "Egypt",
            "favorite_team": "Zamalek",
        }
        response = authenticated_client.patch(
            profile_urls["my_profile"], update_data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        profile = response.data["profile"]
        assert profile["bio"] == "Champion player"
        assert profile["country"] == "Egypt"
        assert profile["favorite_team"] == "Zamalek"

    def test_cannot_change_username_via_profile(
        self, authenticated_client, profile_urls, regular_user
    ):
        """لا يمكن تغيير username عبر Profile API."""
        response = authenticated_client.patch(
            profile_urls["my_profile"],
            {"username": "hacked_username"},
            format="json",
        )
        # يجب أن يبقى الـ username كما هو
        if response.status_code == status.HTTP_200_OK:
            assert response.data["profile"]["username"] == regular_user.username

    def test_win_rate_calculation(self, authenticated_client, profile_urls, regular_user):
        """حساب win_rate صحيح."""
        regular_user.matches_played = 10
        regular_user.wins = 7
        regular_user.losses = 3
        regular_user.save()

        response = authenticated_client.get(profile_urls["my_profile"])
        assert response.status_code == status.HTTP_200_OK
        assert response.data["profile"]["win_rate"] == 70.0

    def test_draws_calculation(self, authenticated_client, profile_urls, regular_user):
        """حساب draws صحيح (draws = matches - wins - losses)."""
        regular_user.matches_played = 10
        regular_user.wins = 6
        regular_user.losses = 3
        regular_user.save()

        response = authenticated_client.get(profile_urls["my_profile"])
        assert response.status_code == status.HTTP_200_OK
        assert response.data["profile"]["draws"] == 1  # 10 - 6 - 3 = 1


# ============================================
# 🌍 PUBLIC PROFILE TESTS
# ============================================


@pytest.mark.django_db
class TestPublicProfileAPI:
    """اختبارات Public Profile endpoint."""

    def test_get_public_profile_success(
        self, api_client, second_user
    ):
        """استرجاع البروفايل العام ينجح بدون مصادقة."""
        response = api_client.get(
            f"/api/v1/users/profile/{second_user.username}/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert "profile" in response.data
        assert response.data["profile"]["username"] == second_user.username

    def test_public_profile_doesnt_expose_email(
        self, api_client, second_user
    ):
        """البروفايل العام لا يُظهر البريد الإلكتروني."""
        response = api_client.get(
            f"/api/v1/users/profile/{second_user.username}/"
        )
        # البريد الإلكتروني حساس — لا يجب أن يظهر في البروفايل العام
        profile = response.data["profile"]
        assert "email" not in profile

    def test_public_profile_nonexistent_user(self, api_client, db):
        """مستخدم غير موجود يُرجع 404."""
        response = api_client.get("/api/v1/users/profile/nonexistentuser/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_public_profile_contains_stats(self, api_client, second_user):
        """البروفايل العام يحتوي على إحصائيات اللاعب."""
        response = api_client.get(
            f"/api/v1/users/profile/{second_user.username}/"
        )
        profile = response.data["profile"]
        assert "matches_played" in profile
        assert "wins" in profile
        assert "losses" in profile
        assert "rank_level" in profile
        assert "rating" in profile


# ============================================
# 🔐 PASSWORD CHANGE TESTS
# ============================================


@pytest.mark.django_db
class TestPasswordChangeAPI:
    """اختبارات تغيير كلمة المرور."""

    def test_change_password_success(
        self, authenticated_client, profile_urls, regular_user
    ):
        """تغيير كلمة المرور الناجح يُرجع 200."""
        response = authenticated_client.post(
            profile_urls["change_password"],
            {
                "current_password": "TestPass123!",
                "new_password": "NewStrongPass456!",
                "confirm_password": "NewStrongPass456!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

    def test_change_password_updates_db(
        self, authenticated_client, profile_urls, regular_user
    ):
        """تغيير كلمة المرور يُحدّث قاعدة البيانات."""
        authenticated_client.post(
            profile_urls["change_password"],
            {
                "current_password": "TestPass123!",
                "new_password": "NewStrongPass456!",
                "confirm_password": "NewStrongPass456!",
            },
            format="json",
        )
        # إعادة تحميل المستخدم من DB
        regular_user.refresh_from_db()
        assert regular_user.check_password("NewStrongPass456!")

    def test_change_password_wrong_current_fails(
        self, authenticated_client, profile_urls
    ):
        """كلمة المرور الحالية الخاطئة تُرجع 400."""
        response = authenticated_client.post(
            profile_urls["change_password"],
            {
                "current_password": "WrongCurrentPass!",
                "new_password": "NewStrongPass456!",
                "confirm_password": "NewStrongPass456!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_mismatch_fails(
        self, authenticated_client, profile_urls
    ):
        """كلمتا المرور الجديدتان غير المتطابقتان تُرجعان 400."""
        response = authenticated_client.post(
            profile_urls["change_password"],
            {
                "current_password": "TestPass123!",
                "new_password": "NewStrongPass456!",
                "confirm_password": "DifferentPass789!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_same_as_current_fails(
        self, authenticated_client, profile_urls
    ):
        """كلمة المرور الجديدة مطابقة للحالية تُرجع 400."""
        response = authenticated_client.post(
            profile_urls["change_password"],
            {
                "current_password": "TestPass123!",
                "new_password": "TestPass123!",
                "confirm_password": "TestPass123!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_unauthenticated_fails(
        self, api_client, profile_urls
    ):
        """تغيير كلمة المرور بدون مصادقة يُرجع 401."""
        response = api_client.post(
            profile_urls["change_password"],
            {
                "current_password": "TestPass123!",
                "new_password": "NewStrongPass456!",
                "confirm_password": "NewStrongPass456!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_weak_new_password_fails(
        self, authenticated_client, profile_urls
    ):
        """كلمة المرور الجديدة الضعيفة تُرجع 400."""
        response = authenticated_client.post(
            profile_urls["change_password"],
            {
                "current_password": "TestPass123!",
                "new_password": "123",
                "confirm_password": "123",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST