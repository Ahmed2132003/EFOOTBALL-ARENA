# ============================================
# eFootball Arena — Authentication Integration Tests
# Full JWT Auth Flow: Register → Login → Profile → Logout
# ============================================

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from tests.factories import UserFactory

User = get_user_model()


# ============================================
# ✅ REGISTER TESTS
# ============================================


@pytest.mark.django_db
class TestRegisterAPI:
    """
    اختبارات تسجيل المستخدمين الجدد.

    كيفية إضافة اختبار جديد:
        def test_new_case(self, api_client, auth_urls):
            response = api_client.post(auth_urls['register'], {...})
            assert response.status_code == ...
    """

    def test_register_success(self, api_client, auth_urls, valid_register_data):
        """تسجيل ناجح — يرجع 201 مع tokens و user data."""
        response = api_client.post(
            auth_urls["register"], valid_register_data, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]
        assert "user" in response.data
        assert response.data["user"]["username"] == "newplayer"
        assert response.data["user"]["email"] == "newplayer@arena.com"
        assert "password" not in response.data["user"]

    def test_register_creates_user_in_db(self, api_client, auth_urls, valid_register_data):
        """التأكد أن المستخدم يُحفظ في قاعدة البيانات."""
        api_client.post(auth_urls["register"], valid_register_data, format="json")
        assert User.objects.filter(username="newplayer").exists()

    def test_register_default_rank_is_bronze(self, api_client, auth_urls, valid_register_data):
        """المستخدم الجديد يبدأ بمستوى Bronze."""
        response = api_client.post(
            auth_urls["register"], valid_register_data, format="json"
        )
        assert response.data["user"]["rank_level"] == "Bronze"

    def test_register_default_rating_is_1000(self, api_client, auth_urls, valid_register_data):
        """المستخدم الجديد يبدأ بتقييم 1000."""
        response = api_client.post(
            auth_urls["register"], valid_register_data, format="json"
        )
        assert response.data["user"]["rating"] == 1000.0

    def test_register_duplicate_email_fails(self, api_client, auth_urls, valid_register_data, db):
        """البريد الإلكتروني المكرر يُرجع 400."""
        # إنشاء مستخدم بنفس البريد
        UserFactory(email="newplayer@arena.com", username="existinguser")

        response = api_client.post(
            auth_urls["register"], valid_register_data, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_username_fails(self, api_client, auth_urls, valid_register_data, db):
        """اسم المستخدم المكرر يُرجع 400."""
        UserFactory(username="newplayer", email="other@arena.com")

        response = api_client.post(
            auth_urls["register"], valid_register_data, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_password_mismatch_fails(self, api_client, auth_urls, valid_register_data):
        """كلمتا المرور غير المتطابقتان يُرجعان 400."""
        data = {**valid_register_data, "password_confirm": "WrongPass999!"}
        response = api_client.post(auth_urls["register"], data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password_fails(self, api_client, auth_urls, valid_register_data):
        """كلمة المرور الضعيفة يُرجع 400."""
        data = {**valid_register_data, "password": "123", "password_confirm": "123"}
        response = api_client.post(auth_urls["register"], data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_email_fails(self, api_client, auth_urls, valid_register_data):
        """غياب البريد الإلكتروني يُرجع 400."""
        data = {k: v for k, v in valid_register_data.items() if k != "email"}
        response = api_client.post(auth_urls["register"], data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_username_fails(self, api_client, auth_urls, valid_register_data):
        """غياب اسم المستخدم يُرجع 400."""
        data = {k: v for k, v in valid_register_data.items() if k != "username"}
        response = api_client.post(auth_urls["register"], data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_empty_body_fails(self, api_client, auth_urls):
        """Body فارغ يُرجع 400."""
        response = api_client.post(auth_urls["register"], {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_username_fails(self, api_client, auth_urls, valid_register_data):
        """اسم المستخدم أقل من 3 أحرف يُرجع 400."""
        data = {**valid_register_data, "username": "ab"}
        response = api_client.post(auth_urls["register"], data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================
# 🔐 LOGIN TESTS
# ============================================


@pytest.mark.django_db
class TestLoginAPI:
    """اختبارات تسجيل الدخول."""

    def test_login_with_username_success(self, api_client, auth_urls, regular_user):
        """تسجيل الدخول باسم المستخدم."""
        response = api_client.post(
            auth_urls["login"],
            {"username": regular_user.username, "password": "TestPass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]
        assert "user" in response.data

    def test_login_with_email_success(self, api_client, auth_urls, regular_user):
        """تسجيل الدخول بالبريد الإلكتروني."""
        response = api_client.post(
            auth_urls["login"],
            {"username": regular_user.email, "password": "TestPass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"]["username"] == regular_user.username

    def test_login_with_email_field_success(self, api_client, auth_urls, regular_user):
        """تسجيل الدخول باستخدام حقل email بدل username."""
        response = api_client.post(
            auth_urls["login"],
            {"email": regular_user.email, "password": "TestPass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_login_wrong_password_fails(self, api_client, auth_urls, regular_user):
        """كلمة مرور خاطئة تُرجع 401."""
        response = api_client.post(
            auth_urls["login"],
            {"username": regular_user.username, "password": "WrongPass!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user_fails(self, api_client, auth_urls, db):
        """مستخدم غير موجود يُرجع 401."""
        response = api_client.post(
            auth_urls["login"],
            {"username": "ghostplayer", "password": "Pass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_empty_credentials_fails(self, api_client, auth_urls, db):
        """بيانات فارغة تُرجع 400."""
        response = api_client.post(auth_urls["login"], {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_returns_user_rank_level(self, api_client, auth_urls, regular_user):
        """بيانات المستخدم تشمل rank_level."""
        response = api_client.post(
            auth_urls["login"],
            {"username": regular_user.username, "password": "TestPass123!"},
            format="json",
        )
        assert "rank_level" in response.data["user"]

    def test_login_returns_user_rating(self, api_client, auth_urls, regular_user):
        """بيانات المستخدم تشمل rating."""
        response = api_client.post(
            auth_urls["login"],
            {"username": regular_user.username, "password": "TestPass123!"},
            format="json",
        )
        assert "rating" in response.data["user"]


# ============================================
# 🔄 TOKEN REFRESH TESTS
# ============================================


@pytest.mark.django_db
class TestTokenRefreshAPI:
    """اختبارات تجديد الـ Access Token."""

    def test_refresh_token_success(self, api_client, auth_urls, user_tokens):
        """تجديد الـ token الناجح يُرجع access token جديد."""
        response = api_client.post(
            auth_urls["refresh"],
            {"refresh": user_tokens["refresh"]},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_refresh_with_invalid_token_fails(self, api_client, auth_urls, db):
        """Token غير صالح يُرجع 401."""
        response = api_client.post(
            auth_urls["refresh"],
            {"refresh": "this.is.not.a.valid.token"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_without_token_fails(self, api_client, auth_urls, db):
        """غياب الـ token يُرجع 400."""
        response = api_client.post(auth_urls["refresh"], {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================
# 👤 ME ENDPOINT TESTS
# ============================================


@pytest.mark.django_db
class TestMeAPI:
    """اختبارات /me endpoint."""

    def test_get_me_authenticated(self, authenticated_client, auth_urls, regular_user):
        """GET /me/ يُرجع بيانات المستخدم المصادَق."""
        response = authenticated_client.get(auth_urls["me"])

        assert response.status_code == status.HTTP_200_OK
        assert "user" in response.data
        assert response.data["user"]["username"] == regular_user.username
        assert response.data["user"]["email"] == regular_user.email

    def test_get_me_unauthenticated_fails(self, api_client, auth_urls):
        """GET /me/ بدون مصادقة يُرجع 401."""
        response = api_client.get(auth_urls["me"])
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_me_bio(self, authenticated_client, auth_urls):
        """تحديث bio ينجح."""
        response = authenticated_client.patch(
            auth_urls["me"], {"bio": "Top eFootball player!"}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"]["bio"] == "Top eFootball player!"

    def test_update_me_country(self, authenticated_client, auth_urls):
        """تحديث country ينجح."""
        response = authenticated_client.patch(
            auth_urls["me"], {"country": "SA"}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"]["country"] == "SA"

    def test_me_doesnt_return_password(self, authenticated_client, auth_urls):
        """بيانات /me/ لا تحتوي على password."""
        response = authenticated_client.get(auth_urls["me"])
        assert "password" not in response.data.get("user", {})


# ============================================
# 🚪 LOGOUT TESTS
# ============================================


@pytest.mark.django_db
class TestLogoutAPI:
    """اختبارات تسجيل الخروج."""

    def test_logout_success(self, authenticated_client, auth_urls, user_tokens):
        """تسجيل الخروج الناجح يُرجع 200."""
        response = authenticated_client.post(
            auth_urls["logout"],
            {"refresh": user_tokens["refresh"]},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Logged out successfully."

    def test_logout_blacklists_refresh_token(
        self, authenticated_client, auth_urls, user_tokens, api_client
    ):
        """بعد تسجيل الخروج، الـ refresh token لا يعمل."""
        # Logout أولاً
        authenticated_client.post(
            auth_urls["logout"],
            {"refresh": user_tokens["refresh"]},
            format="json",
        )

        # محاولة استخدام الـ refresh token المُبطل
        response = api_client.post(
            auth_urls["refresh"],
            {"refresh": user_tokens["refresh"]},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_unauthenticated_fails(self, api_client, auth_urls, user_tokens):
        """تسجيل الخروج بدون JWT يُرجع 401."""
        response = api_client.post(
            auth_urls["logout"],
            {"refresh": user_tokens["refresh"]},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_without_refresh_token_fails(self, authenticated_client, auth_urls):
        """تسجيل الخروج بدون refresh token يُرجع 400."""
        response = authenticated_client.post(auth_urls["logout"], {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_with_invalid_token_fails(self, authenticated_client, auth_urls):
        """Refresh token غير صالح يُرجع 400."""
        response = authenticated_client.post(
            auth_urls["logout"],
            {"refresh": "invalid.token.here"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================
# 🔄 FULL AUTH FLOW INTEGRATION TEST
# ============================================


@pytest.mark.django_db
@pytest.mark.integration
class TestFullAuthFlow:
    """
    اختبار التدفق الكامل للمصادقة:
    Register → Login → Get Profile → Update → Refresh → Logout
    """

    def test_complete_auth_flow(self, api_client, auth_urls, valid_register_data):
        """
        سيناريو كامل:
        1. تسجيل مستخدم جديد
        2. تسجيل دخول
        3. استرجاع بيانات المستخدم
        4. تحديث البيانات
        5. تجديد الـ token
        6. تسجيل الخروج
        """
        # Step 1: Register
        register_response = api_client.post(
            auth_urls["register"], valid_register_data, format="json"
        )
        assert register_response.status_code == status.HTTP_201_CREATED

        access_token = register_response.data["tokens"]["access"]
        refresh_token = register_response.data["tokens"]["refresh"]

        # Step 2: Authenticate
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Step 3: Get Profile
        me_response = api_client.get(auth_urls["me"])
        assert me_response.status_code == status.HTTP_200_OK
        assert me_response.data["user"]["username"] == "newplayer"

        # Step 4: Update Profile
        update_response = api_client.patch(
            auth_urls["me"], {"bio": "eFootball Champion 2024"}, format="json"
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data["user"]["bio"] == "eFootball Champion 2024"

        # Step 5: Refresh Token
        refresh_response = api_client.post(
            auth_urls["refresh"], {"refresh": refresh_token}, format="json"
        )
        assert refresh_response.status_code == status.HTTP_200_OK
        new_access_token = refresh_response.data["access"]
        assert new_access_token != access_token  # Token جديد مختلف

        # Step 6: Logout
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access_token}")
        logout_response = api_client.post(
            auth_urls["logout"], {"refresh": refresh_token}, format="json"
        )
        assert logout_response.status_code == status.HTTP_200_OK

        # Step 7: Verify Logout — Token no longer works
        api_client.credentials()
        verify_response = api_client.get(auth_urls["me"])
        assert verify_response.status_code == status.HTTP_401_UNAUTHORIZED