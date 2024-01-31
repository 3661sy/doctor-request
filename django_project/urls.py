from django.contrib import admin
from django.urls import path

from doctor.views import DiagnosisListCreateView, DiagnosisApplyView, DoctorListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("doctors/", DoctorListView.as_view()),
    path("diagnosis/", DiagnosisListCreateView.as_view()),
    path("diagnosis/<int:pk>/", DiagnosisApplyView.as_view())
]
