import csv
from django.contrib import admin
from django.http import HttpResponse

from .models import Answer, Point, Question, Survey


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'is_active')
    list_filter = ('city', 'is_active')
    search_fields = ('name', 'city')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'type', 'is_active', 'is_required', 'order')
    list_filter = ('category', 'type', 'is_active', 'is_required')
    search_fields = ('text',)
    ordering = ('category', 'order')


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'answer_rating', 'answer_yes_no', 'answer_text', 'created_at')
    can_delete = False


def export_answers_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="answers_export.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ['Survey', 'order_number', 'point', 'created_at', 'completed_at', 'question', 'answer']
    )

    answers = Answer.objects.filter(survey__in=queryset).select_related('survey', 'survey__point', 'question')
    for ans in answers:
        writer.writerow(
            [
                str(ans.survey.token),
                ans.survey.order_number,
                ans.survey.point.name,
                ans.survey.created_at,
                ans.survey.completed_at,
                ans.question.text,
                ans.value,
            ]
        )
    return response


export_answers_csv.short_description = 'Export selected surveys answers to CSV'


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'service_type', 'point', 'completed', 'created_at', 'completed_at')
    list_filter = ('point', 'service_type', 'completed', 'created_at', 'completed_at')
    search_fields = ('order_number', 'token')
    readonly_fields = ('token', 'created_at', 'completed_at')
    inlines = [AnswerInline]
    actions = [export_answers_csv]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('survey', 'question', 'answer_rating', 'answer_yes_no', 'created_at')
    list_filter = (
        'question__category',
        'question__type',
        'survey__point',
        'survey__service_type',
        'survey__completed',
        'created_at',
    )
    search_fields = ('survey__order_number', 'survey__token', 'question__text', 'answer_text')
    readonly_fields = ('created_at',)
