from django.contrib import admin
from .models import FavoriteQuote

@admin.register(FavoriteQuote)
class FavoriteQuoteAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'author', 'text')
    search_fields = ('user_id', 'author')