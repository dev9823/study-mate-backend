from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Lesson, Subject


class SubjectSerializer(ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "title"]

    def create(self, validated_data):
        user_id = self.context.get("user_id")
        return Subject.objects.create(user_id=user_id, **validated_data)


class LessonSerializer(ModelSerializer):
    subject_id = serializers.IntegerField(write_only=True)
    subject = serializers.CharField(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "subject_id",
            "subject",
            "title",
            "content",
            "created_at",
            "updated_at",
        ]

    def validate_subject_id(self, value):
        if not Subject.objects.filter(id=value).exists():
            raise serializers.ValidationError("Subject doesn't exist.")
        return value
