# ============================================
# eFootball Arena — Health Check Tests
# /api/health/ and /api/ready/ Endpoints
# ============================================

import pytest
from rest_framework import status


# ============================================
# 🏥 HEALTH CHECK TESTS
# ============================================


@pytest.mark.django_db
class TestHealthEndpoint:
    """اختبارات الـ health check الأساسي."""

    def test_health_check_returns_200(self, api_client):
        """GET /health/ يُرجع 200."""
        response = api_client.get("/health/")
        assert response.status_code == status.HTTP_200_OK

    def test_health_check_returns_ok_status(self, api_client):
        """GET /health/ يُرجع status: ok."""
        response = api_client.get("/health/")
        assert response.data["status"] == "ok"

    def test_health_check_no_auth_required(self, api_client):
        """Health check لا يحتاج مصادقة."""
        # لا نضيف credentials
        response = api_client.get("/health/")
        assert response.status_code == status.HTTP_200_OK

    def test_health_check_returns_version(self, api_client):
        """Health check يُرجع version."""
        response = api_client.get("/health/")
        assert "version" in response.data


# ============================================
# 🗄️ DATABASE HEALTH TESTS
# ============================================


@pytest.mark.django_db
class TestDatabaseHealth:
    """اختبارات صحة قاعدة البيانات."""

    def test_database_is_accessible(self, db):
        """قاعدة البيانات قابلة للوصول."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        # إذا نجح هذا الاستعلام، فالـ DB يعمل
        count = User.objects.count()
        assert isinstance(count, int)

    def test_can_create_and_retrieve_user(self, db):
        """يمكن إنشاء واسترجاع مستخدم من DB."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(
            username="healthtestuser",
            email="health@test.com",
            password="TestPass123!",
        )
        retrieved = User.objects.get(username="healthtestuser")
        assert retrieved.id == user.id
        assert retrieved.email == "health@test.com"

    def test_database_transactions_work(self, db):
        """Database transactions تعمل بشكل صحيح."""
        from django.contrib.auth import get_user_model
        from django.db import transaction

        User = get_user_model()

        with transaction.atomic():
            user = User.objects.create_user(
                username="transactiontest",
                email="transaction@test.com",
                password="TestPass123!",
            )
            user_id = user.id

        # بعد الـ transaction، المستخدم موجود
        assert User.objects.filter(id=user_id).exists()


# ============================================
# 🔗 API STRUCTURE TESTS
# ============================================


@pytest.mark.django_db
class TestAPIStructure:
    """اختبارات هيكل الـ API."""

    def test_register_endpoint_exists(self, api_client):
        """Register endpoint موجود."""
        response = api_client.post("/api/v1/auth/register/", {}, format="json")
        # 400 لأن البيانات فارغة — لكن الـ endpoint موجود
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_login_endpoint_exists(self, api_client):
        """Login endpoint موجود."""
        response = api_client.post("/api/v1/auth/login/", {}, format="json")
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_me_endpoint_exists(self, api_client):
        """Me endpoint موجود."""
        response = api_client.get("/api/v1/auth/me/")
        # 401 لأنه غير مصادق — لكن الـ endpoint موجود
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_endpoint_exists(self, api_client):
        """Profile endpoint موجود."""
        response = api_client.get("/api/v1/users/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh_endpoint_exists(self, api_client):
        """Token refresh endpoint موجود."""
        response = api_client.post(
            "/api/v1/auth/token/refresh/", {}, format="json"
        )
        assert response.status_code != status.HTTP_404_NOT_FOUND


# ============================================
# 🔒 SECURITY TESTS
# ============================================


@pytest.mark.django_db
class TestSecurityBasics:
    """اختبارات أمان أساسية."""

    def test_protected_endpoints_require_auth(self, api_client):
        """Endpoints المحمية تتطلب مصادقة."""
        protected_urls = [
            "/api/v1/auth/me/",
            "/api/v1/users/profile/",
            "/api/v1/auth/logout/",
            "/api/v1/users/change-password/",
        ]
        for url in protected_urls:
            response = api_client.get(url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
                f"URL {url} should require authentication"
            )

    def test_public_endpoints_dont_require_auth(self, api_client, db):
        """Endpoints العامة لا تتطلب مصادقة."""
        public_urls = [
            "/health/",
        ]
        for url in public_urls:
            response = api_client.get(url)
            assert response.status_code == status.HTTP_200_OK, (
                f"URL {url} should be public"
            )

    def test_passwords_not_exposed_in_responses(
        self, api_client, auth_urls, valid_register_data
    ):
        """كلمات المرور لا تظهر في الاستجابات."""
        response = api_client.post(
            auth_urls["register"], valid_register_data, format="json"
        )
        response_str = str(response.data)
        assert "StrongPass123!" not in response_str
        assert "password" not in response.data.get("user", {})