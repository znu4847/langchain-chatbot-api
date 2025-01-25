from rest_framework.test import APITestCase

from users.tests import create_user
from chat.conversations.models import Conversation
from utils import jwt_utils

# Create your tests here.

BASE_URL = "/api/v1/conversations"


def create_conversation(user, title="Hello world"):
    return Conversation.objects.create(
        user=user,
        title=title,
    )


class RootTestCase(APITestCase):
    URL = f"{BASE_URL}/"

    def setUp(self):
        self.user = create_user("test_user1")
        create_conversation(self.user)

    def test_get(self):
        self.client.credentials(HTTP_JWT=jwt_utils.encode(self.user))
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, 200, "ROOT get #1")
        self.assertEqual(len(response.data), 1, "ROOT get #2")
