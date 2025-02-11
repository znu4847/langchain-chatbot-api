import json
from tokenize import TokenError

from channels.generic.websocket import WebsocketConsumer
from urllib.parse import parse_qs
from chat.conversations.models import Conversation
from utils.jwt_utils import decode
from utils.chatbot.prompt import dummy_chat, pdf_chat
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from .messages import serializers as msg_srlz


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.query = self.parse_query_string()
        self.user = self.get_user_from_token()
        print("consumers.connect::query?")
        print(self.query)
        conversation_pk = self.query.get("conversation")

        # load conversation by conversation_pk
        self.conversation = Conversation.objects.get(pk=conversation_pk)
        print("pdf_url:", self.conversation.pdf_url)
        # check pdf_url is not empty
        if self.conversation.pdf_url:
            print("pdf_chat initialized")
            self.chatterbox = pdf_chat.Chatbot(
                self.conversation.pk,
                self.conversation.pdf_url,
                self.conversation.embed_url,
            )
        else:
            self.chatterbox = dummy_chat.Chatbot(self.conversation.pk)

        # jwt = query_string.get("jwt")
        # print("jwt:", jwt)
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        print("-------------------------------")
        print("consumers.receive:: check input")
        print(f"user: {self.user.username}")
        print(f"conversation: {self.conversation.pk}")
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(f"message: {message}")

        # to-do: check user

        # create message model:human
        human_message = {
            "conversation": self.conversation.pk,
            "role": "human",
            "text": message,
        }
        print("human_message:", human_message)

        # check if the message is valid
        serializer = msg_srlz.CreateSerializer(data=human_message)
        if not serializer.is_valid():
            self.send(
                text_data=json.dumps(
                    {
                        "status": "error",
                        "message": "request is invalid",
                        "pending": False,
                    }
                )
            )
            return

        # save the human-message
        serializer.save()

        # chat with the model
        result = self.chatterbox.chat(message)

        print("chat result : ", result)

        # create message model:ai
        bot_message = {
            "conversation": self.conversation.pk,
            "role": "ai",
            "text": result,
        }
        print("bot_message:", bot_message)

        # check if the message is valid
        serializer = msg_srlz.CreateSerializer(data=bot_message)
        if not serializer.is_valid():
            self.send(
                text_data=json.dumps(
                    {
                        "status": "error",
                        "message": "ai-message is invalid",
                        "pending": False,
                    }
                )
            )
            return

        serializer.save()

        self.send(text_data=json.dumps({"message": result, "pending": False}))

    def parse_query_string(self):
        query_string = self.scope["query_string"].decode()
        queries = parse_qs(query_string)
        # convert queries to a dictionary where the key is the parameter name and the value is a list of values
        return {key: value[0] for key, value in queries.items()}

    def get_user_from_token(self):
        try:
            # parsed_query is a dictionary where the key is the parameter name and the value is a list of values
            token = self.query.get("jwt")
            if not token:
                return AnonymousUser()

            user_model = get_user_model()
            return user_model.objects.get(pk=decode(token)["pk"])
        except (IndexError, TokenError, user_model.DoesNotExist):
            return AnonymousUser()
