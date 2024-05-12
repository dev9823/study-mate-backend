from django.urls import path
from . import views

urlpatterns = [path("", views.ExamViewSet.as_view())]
