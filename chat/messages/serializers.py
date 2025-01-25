from rest_framework.serializers import ModelSerializer, ValidationError
from .models import Message


class ListSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "role",
            "text",
        ]


class CreateSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "conversation",
            "role",
            "text",
        ]
