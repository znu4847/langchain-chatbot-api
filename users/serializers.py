from rest_framework.serializers import ModelSerializer, ValidationError
from .models import User


class TinyUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "email",
            "avatar",
        ]


class PrivateUserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = [
            "password",
            "is_superuser",
            "is_staff",
            "is_active",
            "first_name",
            "last_name",
            "user_permissions",
            "groups",
            "llm_type",
            "openai_key",
            "claude_key",
        ]

    def validate_username(self, value):
        return value

    def validate(self, data):
        return data


class UserPasswordSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "password",
        ]

    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password is too short")
        return value


class LLMKeySerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "openai_key",
            "claude_key",
            "llm_type",
        ]

    def validate_llm_type(self, value):
        if value not in User.LLMChoices.values:
            raise ValidationError("Invalid LLM type")

        if value == User.LLMChoices.OPEN_AI and not self.initial_data.get("openai_key"):
            raise ValidationError("OpenAI key is required")

        elif value == User.LLMChoices.CLAUDE and not self.initial_data.get(
            "claude_key"
        ):
            raise ValidationError("Claude key is required")

        return value


class LoginResposneSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "pk",
            "username",
            "llm_type",
            "openai_key",
            "claude_key",
        ]
