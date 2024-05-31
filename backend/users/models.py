from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователей."""

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "last_name", "username", "password")
    email = models.EmailField("Email", max_length=254, unique=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписок."""

    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="author",
        verbose_name="Автор",
    )
    subscriber = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="subscriber",
        verbose_name="Подписчик",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=("author", "subscriber"),
                name="author_subscriber_unique",
            )
        ]

    def __str__(self):
        return f"{self.subscriber} подписан на {self.author}"
