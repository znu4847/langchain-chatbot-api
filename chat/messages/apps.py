from django.apps import AppConfig


class MessagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    # default name `messages` is conflicted with the built-in `messages` module
    name = "chat.messages"
    label = "chat_messages"
