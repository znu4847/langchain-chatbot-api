from django.contrib import admin
from .models import Message


# Register your models here.
@admin.register(Message)
class CustomMessagesAdmin(admin.ModelAdmin):
    list_display = ("conversation", "role", "text", "timestamp")
