from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import User
from utils.jwt_utils import decode


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("jwt")
        if not token:
            return None
        token_obj = decode(token)
        pk = token_obj.get("pk")
        username = token_obj.get("username")
        if not pk or not username:
            raise AuthenticationFailed("Invalid Token")
        try:
            user = User.objects.get(pk=pk)
            return (user, None)
        except User.DoesNotExist:
            raise AuthenticationFailed("User Not Found")
