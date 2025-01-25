from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.core.exceptions import PermissionDenied
from . import serializers as conv_srlz
from .models import Conversation

# Create your views here.


class ROOT(APIView):
    def get(self, request):
        """
        로그인한 사용자의 대화 목록을 반환합니다
        """

        user = request.user
        if not user or user.is_anonymous:
            return Response(
                {"message": "로그인이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        conversations = conv_srlz.ListSerializer(user.conversations, many=True)

        return Response(
            data=conversations.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """
        새 대화를 생성합니다
        """

        user = request.user
        if not user or user.is_anonymous:
            return Response(
                {"message": "로그인이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not str(user.pk) == str(request.data.get("user")):
            raise PermissionDenied("사용자 정보가 일치하지 않습니다.")

        serializer = conv_srlz.CreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ROOTToken(APIView):
    def get_object(self, pk):
        try:
            return Conversation.objects.get(pk=pk)
        except Conversation.DoesNotExist:
            raise NotFound

    def put(self, request, pk):
        """
        새 대화를 생성합니다
        """
        print("PUT:conversations/:pk")
        print(pk)

        user = request.user
        if not user or user.is_anonymous:
            return Response(
                {"message": "로그인이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        conversation = self.get_object(pk)
        if "tokens" in request.data:
            request.data["tokens"] += conversation.tokens
        if "charges" in request.data:
            request.data["charges"] += conversation.charges
        if not user.pk == conversation.user.pk:
            raise PermissionDenied("사용자 정보가 일치하지 않습니다.")

        serializer = conv_srlz.TokenSerializer(
            conversation, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ROOTDetail(APIView):
    def get_object(self, pk):
        try:
            return Conversation.objects.get(pk=pk)
        except Conversation.DoesNotExist:
            raise NotFound

    def put(self, request, pk):
        """
        대화를 수정합니다
        """

        user = request.user
        if not user or user.is_anonymous:
            return Response(
                {"message": "로그인이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        conversation = self.get_object(pk)
        if not user.pk == conversation.user.pk:
            raise PermissionDenied("사용자 정보가 일치하지 않습니다.")

        serializer = conv_srlz.CreateSerializer(
            conversation, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, pk):
        """
        대화를 삭제합니다
        """

        user = request.user
        if not user or user.is_anonymous:
            return Response(
                {"message": "로그인이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        conversation = self.get_object(pk)
        if not user.pk == conversation.user.pk:
            raise PermissionDenied("사용자 정보가 일치하지 않습니다.")

        conversation.delete()

        return Response(
            {"message": "대화가 삭제되었습니다."},
            status=status.HTTP_200_OK,
        )
