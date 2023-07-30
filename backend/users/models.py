from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    ROLES = {
        (USER, 'user'),
        (ADMIN, 'admin'),
    }

    email = models.EmailField(
        max_length=150,
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    username = models.SlugField(
        max_length=100,
        verbose_name='Имя пользователя',
        unique=True,
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя',
        null=True)
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия',
        null=True)
    role = models.CharField(
        max_length=50,
        choices=ROLES,
        default='user',
        verbose_name='Роль пользователя'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_user(self):
        return self.role == self.USER


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
        help_text='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецепта',
        help_text='Автор рецепта',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscriptions',
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
