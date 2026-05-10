from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class RegisterViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("users:register")
        self.valid_data = {
            "username": "newplayer",
            "email": "new@arena.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "country": "EG",
        }

    def test_register_success(self):
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "newplayer")

    def test_register_duplicate_email(self):
        User.objects.create_user(
            username="existing",
            email="new@arena.com",
            password="Pass123!",
        )
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        data = {**self.valid_data, "password_confirm": "WrongPass123!"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        data = {**self.valid_data, "password": "123", "password_confirm": "123"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        User.objects.create_user(
            username="newplayer",
            email="other@arena.com",
            password="Pass123!",
        )
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("users:login")
        self.user = User.objects.create_user(
            username="loginplayer",
            email="login@arena.com",
            password="StrongPass123!",
        )
        
    def assert_login_success_response(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "loginplayer")
        self.assertIn("rank_level", response.data["user"])
        self.assertIn("rating", response.data["user"])

    def test_login_with_username_success(self):
        response = self.client.post(
            self.url,
            {"username": "loginplayer", "password": "StrongPass123!"},
            format="json",
        )
        self.assert_login_success_response(response)

    def test_login_with_email_success(self):
        response = self.client.post(
            self.url,
            {"username": "login@arena.com", "password": "StrongPass123!"},
            format="json",
        )
        self.assert_login_success_response(response)

    def test_login_with_email_case_insensitive_success(self):
        response = self.client.post(
            self.url,
            {"username": "LOGIN@ARENA.COM", "password": "StrongPass123!"},
            format="json",
        )
        self.assert_login_success_response(response)

    def test_login_with_email_field_success(self):
        response = self.client.post(
            self.url,
            {"email": "login@arena.com", "password": "StrongPass123!"},
            format="json",
        )
        self.assert_login_success_response(response)

    def test_login_wrong_password(self):
        response = self.client.post(
            self.url,
            {"username": "loginplayer", "password": "WrongPass!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        response = self.client.post(
            self.url,
            {"username": "ghost", "password": "Pass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_credentials(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("users:logout")
        self.user = User.objects.create_user(
            username="logoutplayer",
            email="logout@arena.com",
            password="StrongPass123!",
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(self.refresh.access_token)}"
        )

    def test_logout_success(self):
        response = self.client.post(
            self.url, {"refresh": str(self.refresh)}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logged out successfully.")

    def test_logout_without_token(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_unauthenticated(self):
        self.client.credentials()
        response = self.client.post(
            self.url, {"refresh": str(self.refresh)}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_invalid_token(self):
        response = self.client.post(
            self.url, {"refresh": "invalid.token.here"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MeViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("users:me")
        self.user = User.objects.create_user(
            username="meplayer",
            email="me@arena.com",
            password="StrongPass123!",
            country="EG",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

    def test_get_me_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "meplayer")
        self.assertEqual(response.data["user"]["email"], "me@arena.com")
        self.assertIn("rank_level", response.data["user"])
        self.assertIn("rating", response.data["user"])

    def test_get_me_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_me_partial(self):
        response = self.client.patch(
            self.url, {"bio": "Top eFootball player!"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["bio"], "Top eFootball player!")

    def test_update_me_country(self):
        response = self.client.patch(
            self.url, {"country": "SA"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["country"], "SA")


class RefreshTokenViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("users:token-refresh")
        self.user = User.objects.create_user(
            username="refreshplayer",
            email="refresh@arena.com",
            password="StrongPass123!",
        )
        self.refresh = RefreshToken.for_user(self.user)

    def test_refresh_success(self):
        response = self.client.post(
            self.url, {"refresh": str(self.refresh)}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_invalid_token(self):
        response = self.client.post(
            self.url, {"refresh": "bad.token.value"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_missing_token(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)