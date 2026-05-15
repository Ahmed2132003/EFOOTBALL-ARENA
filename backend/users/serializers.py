import os

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_AVATAR_SIZE_MB = 5


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField(required=False, allow_blank=True, write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True, write_only=True)
    login = serializers.CharField(required=False, allow_blank=True, write_only=True)
    identifier = serializers.CharField(required=False, allow_blank=True, write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field].required = False

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["rank_level"] = user.rank_level
        token["rating"] = user.rating
        token["is_verified"] = user.is_verified
        return token

    def validate(self, attrs):
        login_identifier = attrs.get(self.username_field) or ""
        if not isinstance(login_identifier, str):
            login_identifier = str(login_identifier)
        login_identifier = login_identifier.strip()

        if not login_identifier:
            for key in ("email", "login", "identifier"):
                val = attrs.get(key)
                if val:
                    login_identifier = str(val).strip()
                    break

        if not login_identifier:
            raise serializers.ValidationError(
                {"non_field_errors": ["Username or email is required."]}
            )

        password = attrs.get("password", "")
        if not password:
            raise serializers.ValidationError({"password": ["Password is required."]})

        if "@" in login_identifier:
            user_obj = (
                User.objects.filter(email__iexact=login_identifier)
                .only("username")
                .first()
            )
            username = user_obj.get_username() if user_obj else login_identifier
        else:
            username = login_identifier

        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=password,
        )

        if user is None:
            raise AuthenticationFailed(
                "No active account found with the given credentials."
            )

        refresh = self.get_token(user)
        self.user = user

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "rank_level": user.rank_level,
                "rating": user.rating,
                "avatar": user.avatar.url if user.avatar else None,
                "is_verified": user.is_verified,
                "country": user.country,
            },
        }


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, min_length=8,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm", "country", "bio"]
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
        }

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters.")
        if not value.replace("_", "").replace("-", "").isalnum():
            raise serializers.ValidationError(
                "Username may only contain letters, numbers, hyphens and underscores."
            )
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserMeSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "bio", "avatar", "avatar_url",
            "rating", "rank_level", "country", "is_verified",
            "date_joined", "updated_at",
        ]
        read_only_fields = ["id", "rating", "rank_level", "is_verified", "date_joined", "updated_at"]

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


def validate_avatar_file(avatar):
    ext = os.path.splitext(avatar.name)[1].lstrip(".").lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise serializers.ValidationError(
            f"Only {', '.join(ALLOWED_IMAGE_EXTENSIONS)} files are allowed."
        )
    if avatar.size > MAX_AVATAR_SIZE_MB * 1024 * 1024:
        raise serializers.ValidationError(
            f"Avatar file size must not exceed {MAX_AVATAR_SIZE_MB}MB."
        )
    return avatar


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    draws = serializers.SerializerMethodField()
    win_rate = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "avatar", "avatar_url",
            "bio", "rating", "rank_level", "country", "favorite_team",
            "matches_played", "wins", "losses", "draws", "win_rate",
            "date_joined",
        ]
        read_only_fields = [
            "id", "username", "email", "rating", "rank_level",
            "matches_played", "wins", "losses", "date_joined",
        ]

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def get_draws(self, obj):
        return obj.draws

    def get_win_rate(self, obj):
        return obj.win_rate

    def validate_avatar(self, value):
        return validate_avatar_file(value)


class PublicProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    draws = serializers.SerializerMethodField()
    win_rate = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "avatar_url", "bio", "rating", "rank_level",
            "country", "favorite_team", "matches_played", "wins", "losses",
            "draws", "win_rate", "date_joined",
        ]

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def get_draws(self, obj):
        return obj.draws

    def get_win_rate(self, obj):
        return obj.win_rate


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "New passwords do not match."}
            )
        if attrs["current_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "New password must differ from current password."}
            )
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password", "updated_at"])
        return user