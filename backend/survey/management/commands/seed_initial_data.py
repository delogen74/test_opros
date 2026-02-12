from django.core.management.base import BaseCommand

from survey.models import Point, Question


class Command(BaseCommand):
    help = 'Seed initial points and default questions'

    def handle(self, *args, **options):
        points = [
            {
                'name': 'ПВЗ Центральный',
                'city': 'Москва',
                'review_link_2gis': 'https://go.2gis.com/example1',
                'review_link_yandex': 'https://yandex.ru/maps/org/example1/reviews/',
            },
            {
                'name': 'ПВЗ Север',
                'city': 'Санкт-Петербург',
                'review_link_2gis': 'https://go.2gis.com/example2',
                'review_link_yandex': 'https://yandex.ru/maps/org/example2/reviews/',
            },
        ]
        for item in points:
            Point.objects.get_or_create(name=item['name'], city=item['city'], defaults=item)

        questions = [
            ('Оцените скорость обслуживания', Question.Category.COMMON, Question.Type.RATING, True, 10),
            ('Оцените вежливость персонала', Question.Category.COMMON, Question.Type.RATING, True, 20),
            ('Понравилось ли состояние зоны выдачи?', Question.Category.PICKUP, Question.Type.YES_NO, False, 30),
            ('Оцените качество шиномонтажа', Question.Category.TIRE_SERVICE, Question.Type.RATING, True, 40),
            ('Ваш комментарий', Question.Category.COMMON, Question.Type.TEXT, False, 50),
        ]

        for text, category, qtype, is_required, order in questions:
            Question.objects.get_or_create(
                text=text,
                category=category,
                type=qtype,
                defaults={'is_required': is_required, 'order': order, 'is_active': True},
            )

        self.stdout.write(self.style.SUCCESS('Seed completed'))
