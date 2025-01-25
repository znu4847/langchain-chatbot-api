from django.db import models

from common.models import CommonModel


# Create your models here.
class Message(CommonModel):
    class RoleChoices(models.TextChoices):
        SYSTEM = ("system", "System")
        AI = ("ai", "AI")
        HUMAN = "human", "User"

    conversation = models.ForeignKey(
        "chat_conversations.Conversation",
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.HUMAN,
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.text}"
