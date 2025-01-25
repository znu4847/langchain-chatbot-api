from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied
from . import serializers as msg_srlz
from .models import Message
from chat.conversations.models import Conversation

# Create your views here.


class ROOT(APIView):
    def get(self, request):
        """
        로그인한 사용자의 지정한 대화의 메시지 목록을 반환합니다
        """

        user = request.user
        if not user or user.is_anonymous:
            return Response(
                {"message": "로그인이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        conv_pk = request.query_params.get("conversation")

        if not conv_pk:
            return Response(
                {"message": "대화를 지정해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        messages = Message.objects.filter(conversation=conv_pk)

        return Response(
            msg_srlz.ListSerializer(
                messages,
                many=True,
            ).data
        )

    def post(self, request):
        """
        로그인한 사용자의 지정한 대화에 메시지를 추가합니다
        """

        user = request.user
        if not user or user.is_anonymous:
            return Response(
                {"message": "로그인이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not str(user.pk) == str(request.data.get("user")):
            raise PermissionDenied("사용자 정보가 일치하지 않습니다.")

        conversation = Conversation.objects.get(pk=request.data.get("conversation"))
        if not conversation:
            return Response(
                {"message": "대화가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not conversation.user.pk == user.pk:
            raise PermissionDenied("사용자 정보가 일치하지 않습니다.")

        serializer = msg_srlz.CreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message = serializer.save()

        return Response(
            msg_srlz.ListSerializer(message).data,
            status=status.HTTP_201_CREATED,
        )
