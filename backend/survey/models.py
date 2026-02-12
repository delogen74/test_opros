import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg

from django.contrib.auth.models import User
from django.db import models


class Point(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    review_link_2gis = models.URLField(blank=True)
    review_link_yandex = models.URLField(blank=True)

    def __str__(self) -> str:
        return f'{self.city} - {self.name}'


class Question(models.Model):
    class Category(models.TextChoices):
        PICKUP = 'pickup', 'Получение'
        TIRE_SERVICE = 'tire_service', 'Шиномонтаж'
        COMMON = 'common', 'Общие'

    class Type(models.TextChoices):
        RATING = 'rating', 'Оценка'
        YES_NO = 'yes_no', 'Да / Нет'
        TEXT = 'text', 'Текст'

    text = models.TextField("Текст вопроса")
    category = models.CharField(
        "Группа",
        max_length=32,
        choices=Category.choices
    )
    type = models.CharField(
        "Тип вопроса",
        max_length=32,
        choices=Type.choices
    )
    is_active = models.BooleanField("Активен", default=True)
    is_required = models.BooleanField("Обязательный", default=False)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


    def __str__(self) -> str:
        return f'[{self.category}] {self.text[:60]}'


class Survey(models.Model):
    was_pickup = models.BooleanField("Было получение", default=False)
    was_tire_service = models.BooleanField("Был шиномонтаж", default=False)

    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    order_number = models.CharField("Номер заказа", max_length=64)
    point = models.ForeignKey(
        Point,
        verbose_name="ПВЗ",
        on_delete=models.PROTECT,
        related_name='surveys'
    )
    completed = models.BooleanField("Завершен", default=False)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    completed_at = models.DateTimeField("Завершен в", blank=True, null=True)

    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"


    def __str__(self) -> str:
        return f'{self.order_number} ({self.token})'

    @property
    def average_rating(self):
        result = self.answers.filter(
            answer_rating__isnull=False
        ).aggregate(avg=Avg("answer_rating"))
        return result["avg"]


class Answer(models.Model):
    survey = models.ForeignKey(
        Survey,
        verbose_name="Опрос",
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        verbose_name="Вопрос",
        on_delete=models.PROTECT,
        related_name='answers'
    )
    answer_rating = models.PositiveSmallIntegerField(
        "Оценка",
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    answer_yes_no = models.BooleanField("Ответ Да/Нет", blank=True, null=True)
    answer_text = models.TextField("Текстовый ответ", blank=True)
    created_at = models.DateTimeField("Дата ответа", auto_now_add=True)

    class Meta:
        unique_together = ('survey', 'question')
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"


    def __str__(self) -> str:
        return f'{self.survey_id}-{self.question_id}'

    @property
    def value(self):
        if self.answer_rating is not None:
            return self.answer_rating
        if self.answer_yes_no is not None:
            return self.answer_yes_no
        return self.answer_text

class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.ManyToManyField("Point", verbose_name="Доступные ПВЗ")

    def __str__(self):
        return f"Владелец: {self.user.username}"