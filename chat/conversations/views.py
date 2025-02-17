from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.core.exceptions import PermissionDenied
from copy import copy

from . import serializers as conv_srlz
from .models import Conversation
from chat.messages import serializers as msg_srlz
from utils.chatbot.prompt import pdf_chat
from utils.chatbot.embedding.pdf_embedding import Embedder

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
        print("POST:conversations/")
        print(request.data)

        user = request.user
        if not user or user.is_anonymous:
            return Response(
                {"message": "로그인이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # save the conversation
        data = copy(request.data)
        # add 'user' field to the data
        data["user"] = user.pk

        # store file to `./.cache/{username}/file/{filename}`
        # pdf_mode = "file" in request.data and request.data["file"] is not None

        # pdf_mode is True if the request has a file field and is not null
        pdf_mode = "file" in request.data and "null" != request.data["file"]

        if pdf_mode:
            embedder = Embedder()
            file = request.data["file"]
            embed_cache_info = embedder.embed(user.username, file)

            data["pdf_url"] = embed_cache_info["file_path"]
            data["embed_url"] = embed_cache_info["embed_path"]

        print("before validation")

        conv_serializer = conv_srlz.CreateSerializer(data=data)
        if not conv_serializer.is_valid():
            print("POST:conversations/")
            print("conv_serializer is not valid")
            print(conv_serializer.errors)
            print(data)
            return Response(
                {"errors": conv_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation = conv_serializer.save(user=user)

        # chat with the model
        if pdf_mode:
            chatterbox = pdf_chat.Chatbot(
                conversation.pk, conversation.pdf_url, conversation.embed_url
            )
            first_question = "Say welcome and tell me what your job is. Then, summarize the document."
            result = chatterbox.chat(first_question)

            # save the ai-message
            message = {
                "conversation": conversation.pk,
                "role": "ai",
                "text": result,
            }
            msg_serializer = msg_srlz.CreateSerializer(data=message)
            if not msg_serializer.is_valid():
                print("POST:conversations/")
                print("msg_serializer is not valid")
                return Response(
                    {"errors": msg_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            msg_serializer.save()

        return Response(
            conv_serializer.data,
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
