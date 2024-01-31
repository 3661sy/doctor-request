from django.db import models


class DayTypeChoices(models.IntegerChoices):
    MONDAY = 0, "월요일"
    TUESDAY = 1, "화요일"
    WEDNESDAY = 2, "수요일"
    THURSDAY = 3, "목요일"
    FRIDAY = 4, "금요일"
    SATURDAY = 5, "토요일"
    SUNDAY = 6, "일요일"
    LUNCH_TIME = 7, "점심시간"
    HOLIDAY = 8, "공휴일"


class Patient(models.Model):
    name = models.CharField(verbose_name="환자 이름", max_length=128)

    class Meta:
        verbose_name = "환자"
        verbose_name_plural = "환자들"


class Department(models.Model):
    name = models.CharField(verbose_name="진료과목 이름", max_length=128)
    search_name = models.CharField(verbose_name="검색용 이름", max_length=128)
    is_reimbursement = models.BooleanField(verbose_name="급여여부", default=True)

    class Meta:
        verbose_name = "진료과"
        verbose_name_plural = "진료과들"


class Doctor(models.Model):
    name = models.CharField(verbose_name="의사 이름", max_length=128)
    hospital_name = models.CharField(verbose_name="병원 이름", max_length=128)
    department_set = models.ManyToManyField(to=Department, verbose_name="진료과", related_name="doctor_set")

    class Meta:
        verbose_name = "의사"
        verbose_name_plural = "의사들"


class OpenHours(models.Model):
    doctor = models.ForeignKey(to=Doctor, verbose_name="의사", on_delete=models.CASCADE)
    opened_time = models.TimeField(verbose_name="개점시간", null=True, blank=True)
    closed_time = models.TimeField(verbose_name="폐점시간", null=True, blank=True)
    day_type = models.PositiveSmallIntegerField(verbose_name="요일", choices=DayTypeChoices.choices)

    class Meta:
        verbose_name = "영업시간"
        verbose_name_plural = "영업시간들"


class Diagnosis(models.Model):
    patient = models.ForeignKey(verbose_name="환자", to=Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(verbose_name="의사", to=Doctor, on_delete=models.CASCADE)
    is_apply = models.BooleanField(verbose_name="수락 여부", default=False)
    request_date = models.DateTimeField(verbose_name="진료 요청 시간")
    expired_date = models.DateTimeField(verbose_name="진료 요청 만료 시간")

    class Meta:
        verbose_name = "진료 요청"
        verbose_name_plural = "진료 요청들"
