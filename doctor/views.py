from functools import reduce

from django.db.models import Value, Q, Exists, OuterRef
from django.db.models.functions import Concat
from rest_framework.generics import ListAPIView, ListCreateAPIView, UpdateAPIView
from django_filters import FilterSet, NumberFilter, CharFilter, DateTimeFilter

from doctor.models import Diagnosis, Doctor, OpenHours, DayTypeChoices
from doctor.serializers import DiagnosisListCreateSerializer, DiagnosisApplySerializer, DoctorSerializer


class DoctorFilter(FilterSet):
    keyword_search = CharFilter(method="keyword_search_filter")
    request_date = DateTimeFilter(method="request_date_filter")

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset).values('id', 'name').distinct()
        return queryset

    def keyword_search_filter(self, queryset, name, value):
        if value:
            keyword_set = value.split(' ')

            queryset = queryset.annotate(
                q=Concat("name", Value("|"), "hospital_name", Value("|"), "department_set__search_name")
            ).filter(
                reduce(lambda q, keyword: q & Q(q__icontains=keyword), keyword_set, Q())
            )
        return queryset

    def request_date_filter(self, queryset, name, value):
        if value:
            queryset = queryset.annotate(
                is_lunch_time=Exists(
                    OpenHours.objects.filter(
                        doctor_id=OuterRef("id"),
                        day_type=DayTypeChoices.LUNCH_TIME.value,
                        opened_time__lte=value.time(),
                        closed_time__gte=value.time(),
                    )
                )
            ).filter(
                openhours__day_type=value.weekday(),
                openhours__opened_time__lte=value.time(),
                openhours__closed_time__gte=value.time(),
                is_lunch_time=False
            )
        return queryset


class DoctorListView(ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    filterset_class = DoctorFilter


class DiagnosisFilter(FilterSet):
    doctor = NumberFilter(field_name="doctor_id")

    class Meta:
        model = Diagnosis
        fields = ['doctor']


class DiagnosisListCreateView(ListCreateAPIView):
    queryset = Diagnosis.objects.filter(is_apply=False)
    serializer_class = DiagnosisListCreateSerializer
    filterset_class = DiagnosisFilter


class DiagnosisApplyView(UpdateAPIView):
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisApplySerializer
