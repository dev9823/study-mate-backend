from rest_framework import serializers
from note.models import Lesson


class ExamSerializer(serializers.Serializer):
    question = serializers.StringRelatedField(read_only=True)
    answer = serializers.StringRelatedField(read_only=True)
    choices = serializers.StringRelatedField(read_only=True)


class CreateExamSerializer(serializers.Serializer):
    BLANK_SPACE = "BS"
    MULTIPLE_CHOICE = "MC"
    TRUE_OR_FALSE = "TF"

    QUESTION_TYPE = [
        (BLANK_SPACE, "Blank Space"),
        (MULTIPLE_CHOICE, "Multiple Choice"),
        (TRUE_OR_FALSE, "True or False"),
    ]
    question_type = serializers.ChoiceField(choices=QUESTION_TYPE)
    lesson_id = serializers.IntegerField()

    def validate_lesson_id(self, value):
        if not Lesson.objects.filter(id=value).exists():
            raise serializers.ValidationError("Lesson doesn't exists")
        return value

    def get_question_type_display(self):
        question_type_value = self.validated_data.get("question_type")

        for value, display_name in self.QUESTION_TYPE:
            if value == question_type_value:
                return display_name
        return None
