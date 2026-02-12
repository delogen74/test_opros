from rest_framework import serializers

from .models import Answer, Question, Survey


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("id", "text", "category", "type", "is_required", "order")


class PointSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    city = serializers.CharField()


class SurveyPublicSerializer(serializers.ModelSerializer):
    point = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()

    # Чтобы фронт не падал (он ожидает service_type)
    service_type = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = ("token", "order_number", "service_type", "completed", "point", "questions")

    def get_point(self, obj):
        return PointSerializer(obj.point).data

    def get_questions(self, obj):
        return QuestionSerializer(self.context["questions"], many=True).data

    def get_service_type(self, obj):
        # Совместимость со старым фронтом
        if obj.was_pickup and obj.was_tire_service:
            return "both"
        if obj.was_pickup:
            return "pickup"
        if obj.was_tire_service:
            return "tire_service"
        return "both"


class SubmitAnswerItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer = serializers.JSONField()


class SubmitSurveySerializer(serializers.Serializer):
    answers = SubmitAnswerItemSerializer(many=True)

    def validate(self, attrs):
        survey: Survey = self.context["survey"]
        questions = self.context["questions"]

        question_map = {q.id: q for q in questions}
        answers = attrs.get("answers", [])

        provided = {}

        for item in answers:
            qid = item["question_id"]

            if qid not in question_map:
                raise serializers.ValidationError(f"Question {qid} is not valid for this survey.")

            if qid in provided:
                raise serializers.ValidationError(f"Duplicate answer for question {qid}.")

            provided[qid] = item["answer"]

        # обязательные вопросы
        for q in questions:
            if q.is_required and q.id not in provided:
                raise serializers.ValidationError(f"Question {q.id} is required.")

        validated_answers = []
        for qid, raw_answer in provided.items():
            question = question_map[qid]

            rating, yes_no, text = None, None, ""

            if question.type == Question.Type.RATING:
                if not isinstance(raw_answer, int) or not (1 <= raw_answer <= 5):
                    raise serializers.ValidationError(f"Question {qid} expects rating from 1 to 5.")
                rating = raw_answer

            elif question.type == Question.Type.YES_NO:
                if not isinstance(raw_answer, bool):
                    raise serializers.ValidationError(f"Question {qid} expects boolean value.")
                yes_no = raw_answer

            elif question.type == Question.Type.TEXT:
                if not isinstance(raw_answer, str):
                    raise serializers.ValidationError(f"Question {qid} expects text value.")
                text = raw_answer.strip()
                if question.is_required and not text:
                    raise serializers.ValidationError(f"Question {qid} text answer is required.")

            validated_answers.append(
                {"question": question, "rating": rating, "yes_no": yes_no, "text": text}
            )

        attrs["validated_answers"] = validated_answers
        attrs["survey"] = survey
        return attrs

    def save(self, **kwargs):
        survey: Survey = self.validated_data["survey"]
        payload = self.validated_data["validated_answers"]

        # Лучше update_or_create: не сломается при повторной отправке/дублях
        for item in payload:
            Answer.objects.update_or_create(
                survey=survey,
                question=item["question"],
                defaults={
                    "answer_rating": item["rating"],
                    "answer_yes_no": item["yes_no"],
                    "answer_text": item["text"],
                },
            )

        return survey
