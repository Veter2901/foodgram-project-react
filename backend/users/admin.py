from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscribe, User

# Register your models here.


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username', 'id', 'email', 'first_name', 'last_name',
    )
    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('first_name', 'email')
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'author', 'user', 'created'
    )
    search_fields = ('author', 'created')
    list_filter = ('author', 'user', 'created')
    empy_value_display = '-пусто-'
