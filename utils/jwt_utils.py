from django.conf import settings
import jwt

from users.models import User


def encode(user: User):
    token = jwt.encode(
        {
            "pk": user.pk,
            "username": user.username,
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return token


def decode(token: str):
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=["HS256"],
    )
