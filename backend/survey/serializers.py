from rest_framework import serializers

from .models import Answer, Question, Survey


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'text', 'category', 'type', 'is_required', 'order')


class PointSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    city = serializers.CharField()


class SurveyPublicSerializer(serializers.ModelSerializer):
    point = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = ('token', 'order_number', 'service_type', 'completed', 'point', 'questions')

    def get_point(self, obj):
        return PointSerializer(obj.point).data

    def get_questions(self, obj):
        return QuestionSerializer(self.context['questions'], many=True).data


class SubmitAnswerItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer = serializers.JSONField()


class SubmitSurveySerializer(serializers.Serializer):
    answers = SubmitAnswerItemSerializer(many=True)

    def validate(self, attrs):
        survey: Survey = self.context['survey']
        questions = self.context['questions']
        question_map = {q.id: q for q in questions}
        answers = attrs.get('answers', [])

        provided_map = {}
        for item in answers:
            qid = item['question_id']
            if qid not in question_map:
                raise serializers.ValidationError(f'Question {qid} is not valid for this survey.')
            if qid in provided_map:
                raise serializers.ValidationError(f'Duplicate answer for question {qid}.')
            provided_map[qid] = item['answer']

        for q in questions:
            if q.is_required and q.id not in provided_map:
                raise serializers.ValidationError(f'Question {q.id} is required.')

        validated_answers = []
        for qid, raw_answer in provided_map.items():
            question = question_map[qid]
            rating, yes_no, text = None, None, ''
            if question.type == Question.Type.RATING:
                if not isinstance(raw_answer, int) or raw_answer < 1 or raw_answer > 5:
                    raise serializers.ValidationError(f'Question {qid} expects rating from 1 to 5.')
                rating = raw_answer
            elif question.type == Question.Type.YES_NO:
                if not isinstance(raw_answer, bool):
                    raise serializers.ValidationError(f'Question {qid} expects boolean value.')
                yes_no = raw_answer
            elif question.type == Question.Type.TEXT:
                if not isinstance(raw_answer, str):
                    raise serializers.ValidationError(f'Question {qid} expects text value.')
                if question.is_required and not raw_answer.strip():
                    raise serializers.ValidationError(f'Question {qid} text answer is required.')
                text = raw_answer.strip()

            validated_answers.append({'question': question, 'rating': rating, 'yes_no': yes_no, 'text': text})

        attrs['validated_answers'] = validated_answers
        attrs['survey'] = survey
        return attrs

    def save(self, **kwargs):
        survey: Survey = self.validated_data['survey']
        payload = self.validated_data['validated_answers']
        Answer.objects.bulk_create(
            [
                Answer(
                    survey=survey,
                    question=item['question'],
                    answer_rating=item['rating'],
                    answer_yes_no=item['yes_no'],
                    answer_text=item['text'],
                )
                for item in payload
            ]
        )
        return survey
