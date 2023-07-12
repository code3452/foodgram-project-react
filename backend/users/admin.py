from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'role',
    )
    list_filter = ('email', 'username',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowernAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
    list_filter = ('user',)
    empty_value_display = '-пусто-'
