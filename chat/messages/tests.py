from rest_framework.test import APITestCase

from users.tests import create_user
from chat.messages.models import Message
from chat.conversations.models import Conversation
from chat.conversations.tests import create_conversation
from utils import jwt_utils

# Create your tests here.

BASE_URL = "/api/v1/messages"


def create_message(user, conversation, text):
    return Message.objects.create(
        conversation=conversation,
        text=text,
    )


class RootTestCase(APITestCase):
    URL = f"{BASE_URL}/"

    def setUp(self):
        self.user = create_user("test_user1")
        self.conversation = create_conversation(self.user)
        create_message(self.user, self.conversation, "Hello world")

    def test_post(self):
        self.client.credentials(HTTP_JWT=jwt_utils.encode(self.user))
        response = self.client.post(
            self.URL,
            {
                "user": self.user.pk,
                "conversation": self.conversation.pk,
                "text": "Hello world 2",
            },
        )

        self.assertEqual(response.status_code, 201, "ROOT post #1")
        self.assertEqual(response.data["text"], "Hello world 2", "ROOT post #2")
        self.assertEqual(
            response.data["conversation"], self.conversation.pk, "ROOT post #3"
        )
