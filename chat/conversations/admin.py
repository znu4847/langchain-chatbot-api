from django.contrib import admin
from .models import Conversation


# Register your models here.
@admin.register(Conversation)
class CustomMessagesAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "title", "pdf_url", "embed_url", "last_message")
