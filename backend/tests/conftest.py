# ============================================
# eFootball Arena — Test Fixtures (conftest.py)
# Reusable, Isolated, Production-Ready Fixtures
# ============================================

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from tests.factories import UserFactory, AdminUserFactory

User = get_user_model()


# ============================================
# 🔧 API CLIENT FIXTURES
# ============================================


@pytest.fixture
def api_client():
    """
    APIClient غير مصادَق — للاختبارات العامة.

    الاستخدام:
        def test_public_endpoint(api_client):
            response = api_client.get('/api/v1/health/')
            assert response.status_code == 200
    """
    return APIClient()


@pytest.fixture
def authenticated_client(regular_user):
    """
    APIClient مصادَق بـ JWT token.

    الاستخدام:
        def test_protected_endpoint(authenticated_client):
            response = authenticated_client.get('/api/v1/auth/me/')
            assert response.status_code == 200
    """
    client = APIClient()
    refresh = RefreshToken.for_user(regular_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


@pytest.fixture
def admin_client(admin_user):
    """
    APIClient مصادَق بصلاحيات Admin.

    الاستخدام:
        def test_admin_endpoint(admin_client):
            response = admin_client.get('/admin/')
            assert response.status_code == 200
    """
    client = APIClient()
    refresh = RefreshToken.for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


# ============================================
# 👤 USER FIXTURES
# ============================================


@pytest.fixture
def regular_user(db):
    """
    مستخدم عادي جاهز للاختبار.

    الاستخدام:
        def test_user_profile(regular_user):
            assert regular_user.rank_level == 'Bronze'
    """
    return UserFactory(
        username="testplayer",
        email="testplayer@arena.com",
        password="TestPass123!",
    )


@pytest.fixture
def admin_user(db):
    """
    مستخدم بصلاحيات كاملة (Admin).

    الاستخدام:
        def test_admin_access(admin_user):
            assert admin_user.is_staff == True
    """
    return AdminUserFactory(
        username="adminuser",
        email="admin@arena.com",
        password="AdminPass123!",
    )


@pytest.fixture
def second_user(db):
    """
    مستخدم ثانٍ لاختبار التفاعلات بين المستخدمين.

    الاستخدام:
        def test_view_other_profile(regular_user, second_user, api_client):
            ...
    """
    return UserFactory(
        username="secondplayer",
        email="second@arena.com",
    )


@pytest.fixture
def multiple_users(db):
    """
    قائمة من 5 مستخدمين للاختبارات التي تحتاج بيانات كثيرة.

    الاستخدام:
        def test_user_list(multiple_users):
            assert len(multiple_users) == 5
    """
    return UserFactory.create_batch(5)


# ============================================
# 🔑 TOKEN FIXTURES
# ============================================


@pytest.fixture
def user_tokens(regular_user):
    """
    Access + Refresh tokens لمستخدم عادي.

    الاستخدام:
        def test_refresh(user_tokens):
            access = user_tokens['access']
            refresh = user_tokens['refresh']
    """
    refresh = RefreshToken.for_user(regular_user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": regular_user,
    }


@pytest.fixture
def auth_headers(user_tokens):
    """
    Authorization headers جاهزة للاستخدام في الطلبات.

    الاستخدام:
        def test_endpoint(auth_headers, api_client):
            api_client.credentials(**auth_headers)
    """
    return {"HTTP_AUTHORIZATION": f"Bearer {user_tokens['access']}"}


# ============================================
# 📝 REGISTRATION DATA FIXTURES
# ============================================


@pytest.fixture
def valid_register_data():
    """
    بيانات تسجيل صالحة لاختبار Register API.

    الاستخدام:
        def test_register(api_client, valid_register_data):
            response = api_client.post('/api/v1/auth/register/', valid_register_data)
    """
    return {
        "username": "newplayer",
        "email": "newplayer@arena.com",
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
        "country": "EG",
    }


@pytest.fixture
def valid_login_data(regular_user):
    """
    بيانات تسجيل دخول صالحة.

    الاستخدام:
        def test_login(api_client, valid_login_data):
            response = api_client.post('/api/v1/auth/login/', valid_login_data)
    """
    return {
        "username": regular_user.username,
        "password": "TestPass123!",
    }


# ============================================
# 🌐 URL FIXTURES
# ============================================


@pytest.fixture
def auth_urls():
    """
    URLs لجميع Auth endpoints.

    الاستخدام:
        def test_register(api_client, auth_urls):
            response = api_client.post(auth_urls['register'], {...})
    """
    return {
        "register": "/api/v1/auth/register/",
        "login": "/api/v1/auth/login/",
        "logout": "/api/v1/auth/logout/",
        "refresh": "/api/v1/auth/token/refresh/",
        "me": "/api/v1/auth/me/",
    }


@pytest.fixture
def profile_urls():
    """
    URLs لجميع Profile endpoints.

    الاستخدام:
        def test_profile(authenticated_client, profile_urls):
            response = authenticated_client.get(profile_urls['my_profile'])
    """
    return {
        "my_profile": "/api/v1/users/profile/",
        "change_password": "/api/v1/users/change-password/",
    }


# ============================================
# 🗃️ DATABASE ISOLATION
# ============================================


@pytest.fixture(autouse=False)
def clean_db(db):
    """
    يضمن قاعدة بيانات نظيفة لكل اختبار.
    autouse=False — يجب استدعاؤه صريحاً.
    """
    yield
    # Django pytest plugin يتعامل مع rollback تلقائياً


@pytest.fixture(scope="session")
def django_db_setup():
    """
    Session-scoped DB setup — يُشغَّل مرة واحدة للـ session كاملة.
    """
    pass