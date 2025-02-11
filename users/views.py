from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from utils.jwt_utils import encode
from utils import page_utils
from .models import User
from . import serializers


# /users/
class ROOT(APIView):
    def get(self, request):
        """
        등록된 사용자 목록을 반환합니다
        """

        page = page_utils.get_page(request)

        # get users per page
        users = page_utils.get_page_items(page, User.objects.all())
        serializer = serializers.TinyUserSerializer(
            users,
            many=True,
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """
        신규 사용자를 등록합니다
        """

        password1 = request.data.get("password1")
        password2 = request.data.get("password2")

        try:
            # check if passwords match
            if password1 != password2:
                raise ValidationError(["암호가 일치하지 않습니다."])

            # validate user data
            serializer = serializers.PrivateUserSerializer(data=request.data)
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)

            # validate password
            # validate_password(password1)

        except ValidationError as e:
            return Response(
                {"errors": e.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        password = password1
        user = serializer.save()
        # set password by calling set_password method for hashing it
        user.set_password(password)
        user.save()
        token = encode(user)

        print("------------- POST: /users/")

        serializer = serializers.PrivateUserSerializer(user)
        print(serializer.data)
        # print(serializer.data["id"])
        # print(serializer.data["pk"])
        # print(serializer.data["username"])
        # print(serializer.data["name"])
        return Response(
            serializer.data | {"jwt": token},
            status=status.HTTP_201_CREATED,
        )


# /users/<int:pk>
class PK(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("User does not exist")

    def get(self, request, pk):
        """
        pk에 해당하는 사용자 정보를 반환합니다
        """
        user = self.get_object(pk)
        serializer = serializers.PrivateUserSerializer(user)
        return Response(serializer.data)


# /users/password
class Password(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """
        로그인한 사용자의 비밀번호를 변경합니다
        """

        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            raise ParseError("Old password and new password are required")

        if not user.check_password(old_password):
            raise ParseError("Old password is incorrect")

        user.set_password(new_password)
        user.save()
        return Response(status=204)


# /users/login
class Login(APIView):
    def post(self, request):
        """
        지정한 사용자로 로그인합니다
        """
        print("---------------- hey")
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response(
                {"error": "username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if not user:
            return Response(
                {"error": "username or password is incorrect"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token = encode(user)
        login(request, user)
        return Response(
            {
                "pk": user.pk,
                "username": user.username,
                "jwt": token,
            },
            status=status.HTTP_200_OK,
        )


# /users/logout
class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        로그아웃합니다
        """
        logout(request)
        return Response(
            {"ok": "bye!"},
            status=status.HTTP_200_OK,
        )


# /users/verify
class Verify(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        록인한 사용자의 정보를 반환합니다
        """

        serializer = serializers.PrivateUserSerializer(request.user)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# /users/auth
class Auth(APIView):
    def get(self, request):
        """
        요청한 사용자가 인증되었는지 확인합니다
        """

        user = request.user

        if not user or user.is_anonymous:
            return Response(
                {"errors": ["user is not authenticated"]},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {"ok": "Welcome!"},
            status=status.HTTP_200_OK,
        )


class LLMKey(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("User does not exist")

    def get(self, request, pk):
        """
        사용자의 API 키를 반환합니다
        """
        user = self.get_object(pk)
        return Response(
            serializers.LLMKeySerializer(user).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        """
        사용자의 API 키를 갱신합니다
        """
        user = request.user

        if not user or user.is_anonymous:
            return Response(
                {"errors": ["user is not authenticated"]},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = self.get_object(pk)

        serializer = serializers.LLMKeySerializer(
            user,
            data=request.data,
            partial=True,
        )
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = serializer.save()

        return Response(
            serializers.LLMKeySerializer(user).data,
            status=status.HTTP_200_OK,
        )


class Stats(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("User does not exist")

    def get(self, request, pk):
        """
        사용자의 API 키를 반환합니다
        """
        print("users/stats")
        print(pk)
        user = self.get_object(pk)
        return Response(
            serializers.LLMKeySerializer(user).data,
            status=status.HTTP_200_OK,
        )
