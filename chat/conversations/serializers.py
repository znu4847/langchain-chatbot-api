from rest_framework.serializers import ModelSerializer, ValidationError
from .models import Conversation


class ListSerializer(ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            "pk",
            "title",
            "pdf_url",
            "embed_url",
            "last_message",
            "tokens",
            "charges",
        ]


class DetailSerializer(ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"


class CreateSerializer(ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            "pk",
            "user",
            "title",
            "pdf_url",
            "embed_url",
            "tokens",
            "charges",
        ]

    def validate_name(self, value):
        return value

    def validate(self, data):
        return data


class TokenSerializer(ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            "pk",
            "tokens",
            "charges",
        ]

    # def validate_name(self, value):
    #     return value

    # def validate(self, data):
    #     return data
