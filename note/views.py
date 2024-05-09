from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from .serializers import LessonSerializer, SubjectSerializer
from .models import Lesson, Subject


class SubjectViewSet(ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["title"]

    def get_queryset(self):
        user_id = self.request.user.id
        return Subject.objects.filter(user_id=user_id)

    def get_serializer_context(self):
        user_id = self.request.user.id
        return {"user_id": user_id}


class LessonViewSet(ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["title"]

    def get_queryset(self):
        user_id = self.request.user.id
        return Lesson.objects.filter(subject__user_id=user_id)
