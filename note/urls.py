from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register("subjects", views.SubjectViewSet, basename="subject")
router.register("lessons", views.LessonViewSet, basename="lesson")

urlpatterns = router.urls
