from django.contrib import admin
from bot_app.models import Quote, FavoriteQuote

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'category', 'text')
    list_filter = ('category',)


@admin.register(FavoriteQuote)
class FavoriteQuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'author', 'category')