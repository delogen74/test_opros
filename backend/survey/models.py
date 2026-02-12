import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
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
        PICKUP = 'pickup', 'Pickup'
        TIRE_SERVICE = 'tire_service', 'Tire service'
        COMMON = 'common', 'Common'

    class Type(models.TextChoices):
        RATING = 'rating', 'Rating'
        YES_NO = 'yes_no', 'Yes/No'
        TEXT = 'text', 'Text'

    text = models.TextField()
    category = models.CharField(max_length=32, choices=Category.choices)
    type = models.CharField(max_length=32, choices=Type.choices)
    is_active = models.BooleanField(default=True)
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order', 'id')

    def __str__(self) -> str:
        return f'[{self.category}] {self.text[:60]}'


class Survey(models.Model):
    class ServiceType(models.TextChoices):
        PICKUP = 'pickup', 'Pickup'
        TIRE_SERVICE = 'tire_service', 'Tire service'
        BOTH = 'both', 'Both'

    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    order_number = models.CharField(max_length=64)
    service_type = models.CharField(max_length=32, choices=ServiceType.choices)
    point = models.ForeignKey(Point, on_delete=models.PROTECT, related_name='surveys')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.order_number} ({self.token})'


class Answer(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name='answers')
    answer_rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    answer_yes_no = models.BooleanField(blank=True, null=True)
    answer_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('survey', 'question')

    def __str__(self) -> str:
        return f'{self.survey_id}-{self.question_id}'

    @property
    def value(self):
        if self.answer_rating is not None:
            return self.answer_rating
        if self.answer_yes_no is not None:
            return self.answer_yes_no
        return self.answer_text
