from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT serializer يضيف بيانات إضافية للـ token payload والـ response."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # بيانات إضافية داخل الـ token payload
        token["username"] = user.username
        token["rank_level"] = user.rank_level
        token["rating"] = user.rating
        token["is_verified"] = user.is_verified
        return token

    def validate(self, attrs):
        login_identifier = attrs.get(self.username_field, "").strip()

        if login_identifier:
            attrs[self.username_field] = login_identifier

        if "@" in login_identifier:
            user = (
                User.objects.filter(email__iexact=login_identifier)
                .only("username")
                .first()
            )
            if user:
                attrs[self.username_field] = user.get_username()

        data = super().validate(attrs)
        user = self.user
        # بيانات إضافية في الـ response body
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rank_level": user.rank_level,
            "rating": user.rating,
            "avatar": user.avatar.url if user.avatar else None,
            "is_verified": user.is_verified,
            "country": user.country,
        }
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer لتسجيل مستخدم جديد مع validation كامل."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "password_confirm",
            "country",
            "bio",
        ]
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
    """Serializer لعرض بيانات المستخدم الحالي."""

    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "bio",
            "avatar",
            "avatar_url",
            "rating",
            "rank_level",
            "country",
            "is_verified",
            "date_joined",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "rating",
            "rank_level",
            "is_verified",
            "date_joined",
            "updated_at",
        ]

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None