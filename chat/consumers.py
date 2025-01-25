import json
import random
import time
from tokenize import TokenError

from channels.generic.websocket import WebsocketConsumer
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from urllib.parse import parse_qs
from utils.jwt_utils import decode
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from .messages import serializers as msg_srlz
from . import prompts


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.query = self.parse_query_string()
        self.user = self.get_user_from_token()
        print("consumers.connect::query?")
        print(self.query)
        self.conversation = self.query.get("conversation")
        print("consumers.connect:: socket connected")

        # jwt = query_string.get("jwt")
        # print("jwt:", jwt)
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        print("-------------------------------")
        print("consumers.receive:: check input")
        print(f"user: {self.user}")
        print(f"conversation: {self.conversation}")

        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print("receive:", message)
        {
            "conversation": self.conversation,
            "role": "human",
            "text": message,
        }
        human_serializer = msg_srlz.CreateSerializer(
            data={
                "conversation": self.conversation,
                "role": "human",
                "text": message,
            }
        )
        if human_serializer.is_valid():
            human_serializer.save()
        else:
            print(human_serializer.errors)

        dev = True
        if dev:
            ai_message = message + "_re"
            self.send(text_data=json.dumps({"message": ai_message, "pending": False}))
            ai_serializer = msg_srlz.CreateSerializer(
                data={
                    "conversation": self.conversation,
                    "role": "ai",
                    "text": ai_message,
                }
            )
            if ai_serializer.is_valid():
                ai_serializer.save()
            else:
                print(ai_serializer.errors)
            return
        messages = [
            SystemMessage("Translate the following from English into Italian"),
            HumanMessage(message),
        ]
        model = ChatOpenAI(model="gpt-4o-mini")

        prompt = prompts.SimpleChat(model)
        result = prompt.chat(messages)
        print("result:", result.content)

        self.send(text_data=json.dumps({"message": result.content, "pending": False}))

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


dummy_messages = [
    """
맨발로 기억을 거닐다
떨어지는 낙엽에
그간 잊지 못한 사람들을 보낸다
""",
    """
맨발로 기억을 거닐다
붉게 물든 하늘에
그간 함께 못한 사람들을 올린다
""",
    """
시간은 물 흐르듯이 흘러가고
난 추억이란 댐을 놓아
미처 잡지 못한 기억이 있어
오늘도 수평선 너머를 보는 이유
""",
    """
맨발로 기억을 거닐다
날 애싸는 단풍에
모든 걸 내어주고 살포시 기대본다
""",
    """
맨발로 기억을 거닐다
다 익은 가을내에
허기진 맘을 붙잡고 곤히 잠이 든다
""",
    """
가슴의 꽃과 나무 시들어지고
깊게 묻혀 꺼내지 못할 기억
그 곳에 잠들어 버린
그대로가 아름다운 것이

슬프다 슬프다
""",
    """
맨발로 기억을 거닐다
노란 은행나무에
숨은 나의 옛날 추억을 불러본다
""",
    """
맨발로 기억을 거닐다
불어오는 바람에
가슴으로 감은 눈을 꼭 안아본다
""",
]


class DummyConsumer(WebsocketConsumer):
    def connect(self):
        print("connect")
        self.accept()
        self.send(text_data=json.dumps({"data": "connected..?"}))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print("receive:", message)

        # get random index of dummy_messages
        random_index = random.randint(0, len(dummy_messages) - 1)
        random_message = dummy_messages[random_index]

        print("random_message:", random_message)

        response_message = ""

        for char in random_message:
            response_message += char
            # response message asynchronusly
            self.send(
                text_data=json.dumps({"message": response_message, "pending": True})
            )
            time.sleep(0.1)

        self.send(text_data=json.dumps({"message": response_message, "pending": False}))
