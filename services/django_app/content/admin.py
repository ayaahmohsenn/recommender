from django.contrib import admin
from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "author", "created_at", "published_at")
    list_filter = ("status", "author")
    search_fields = ("title", "body", "author")
    ordering = ("-created_at",)

