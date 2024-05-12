from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("oauth/", include("core.urls")),
    path("note/", include("note.urls")),
    path("exam/", include("exams.urls")),
]
