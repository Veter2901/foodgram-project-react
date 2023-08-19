from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'id',
        'email',
        'first_name',
        'last_name',
        'get_recipe_count',
        'get_follower_count',
    )
    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('first_name', 'email')
    empty_value_display = '-пусто-'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(recipe_count=Count('recipes'))
        queryset = queryset.annotate(follower_count=Count('follower'))
        return queryset

    def get_recipe_count(self, obj):
        return obj.recipe_count
    get_recipe_count.short_description = 'Кол-во рецептов'

    def get_follower_count(self, obj):
        return obj.follower_count
    get_follower_count.short_description = 'Кол-во подписчиков'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'author', 'user', 'created'
    )
    search_fields = ('author', 'created')
    list_filter = ('author', 'user', 'created')
    empy_value_display = '-пусто-'
