from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Логин',
        max_length=settings.MAX_LEN,
        unique=True,
    )
    email = models.EmailField(
        verbose_name='email address',
        max_length=settings.MAX_LEN,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.MAX_LEN,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.MAX_LEN,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}, {self.email}'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Автор",
    )
    created = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True)

    class Meta:
        ordering = ('-id',)
        constraints = [
            UniqueConstraint(fields=['user', 'author'],
                             name='unique_subscription'),
            CheckConstraint(check=~Q(user=F('author')),
                            name='no_self_subscription'),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (f'Пользователь: {self.user.username},'
                f' автор: {self.author.username}')
