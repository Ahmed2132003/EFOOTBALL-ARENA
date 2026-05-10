from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserMeSerializer,
)
from .throttles import LoginRateThrottle, RegisterRateThrottle

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    تسجيل مستخدم جديد — يرجع tokens + بيانات المستخدم.
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # توليد JWT tokens مباشرة بعد التسجيل
        refresh = RefreshToken.for_user(user)
        refresh["username"] = user.username
        refresh["rank_level"] = user.rank_level
        refresh["rating"] = user.rating
        refresh["is_verified"] = user.is_verified

        return Response(
            {
                "message": "Registration successful.",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "rank_level": user.rank_level,
                    "rating": user.rating,
                    "avatar": None,
                    "is_verified": user.is_verified,
                    "country": user.country,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """
    POST /api/v1/auth/login/
    تسجيل دخول — يرجع access + refresh tokens مع بيانات المستخدم.
    """

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(
            {
                "message": "Login successful.",
                "tokens": {
                    "refresh": serializer.validated_data["refresh"],
                    "access": serializer.validated_data["access"],
                },
                "user": serializer.validated_data["user"],
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    تسجيل خروج — يعمل blacklist للـ refresh token.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"error": "Token is invalid or already blacklisted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )


class RefreshTokenView(TokenRefreshView):
    """
    POST /api/v1/auth/token/refresh/
    تجديد الـ access token باستخدام الـ refresh token.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response.data["message"] = "Token refreshed successfully."
        return response


class MeView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/v1/auth/me/  ← بيانات المستخدم الحالي
    PUT  /api/v1/auth/me/  ← تحديث البيانات
    PATCH /api/v1/auth/me/ ← تحديث جزئي
    """

    serializer_class = UserMeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "message": "User data retrieved successfully.",
                "user": serializer.data,
            }
        )

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs["partial"])
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Profile updated successfully.",
                "user": serializer.data,
            }
        )