from django.contrib import admin

from .models import Content


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ["title", "kind", "price", "sale_price", "is_published", "created_at"]
    list_filter = ["kind", "is_published"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ["title"]}
    list_editable = ["is_published"]
