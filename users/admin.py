from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (
            "Profile",
            {
                "fields": (
                    "username",
                    "name",
                    "email",
                    "llm_type",
                    "openai_key",
                    "claude_key",
                ),
                "classes": ("wide",),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    list_display = (
        "username",
        "email",
        "name",
        "llm_type",
        "is_openai_key_registed",
        "is_claude_key_registed",
    )

    add_fieldsets = (
        (
            "Add User",
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
