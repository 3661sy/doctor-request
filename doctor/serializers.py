from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
import datetime

from doctor.models import Diagnosis, OpenHours, Doctor, DayTypeChoices


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            "id",
            "name"
        ]

        extra_kwargs = {
            "id": {"read_only": True},
            "name": {"read_only": True}
        }


class DiagnosisListCreateSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    patient_id = serializers.IntegerField(write_only=True)
    doctor_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Diagnosis
        fields = [
            "id",
            "patient_id",
            "doctor_id",
            "patient_name",
            "request_date",
            "expired_date",
        ]

        extra_kwargs = {
            "id": {"read_only": True},
            "expired_date": {"read_only": True}
        }

    def validate(self, attrs):
        now_date = timezone.now()
        request_date = attrs["request_date"]
        open_hours = OpenHours.objects.filter(
            doctor_id=attrs["doctor_id"],
        ).order_by("day_type").values("day_type", "opened_time", "closed_time")

        open_hours = {
            i["day_type"]: {
                "opened_time": i["opened_time"], "closed_time": i["closed_time"]
            }
            for i in open_hours
        }

        lunch_time = open_hours.get(DayTypeChoices.LUNCH_TIME.value)

        if not (
                (
                        open_hours[request_date.weekday()]["opened_time"] <=
                        request_date.time() <=
                        open_hours[request_date.weekday()]["closed_time"]
                )
                if request_date.weekday() in open_hours else False
        ) or (
                (lunch_time["opened_time"] <= request_date.time() <= lunch_time["closed_time"])
                if lunch_time else False
        ):
            raise ValidationError({"request_date": "해당일시는 영업시간이 아닙니다."})

        now_time = now_date.time()
        now_weekday = now_date.weekday()

        if now_weekday in open_hours and (
                open_hours[now_weekday]["opened_time"] <= now_time <= open_hours[now_weekday]["closed_time"]
        ):
            if lunch_time["opened_time"] <= now_time <= lunch_time["closed_time"]:
                expired_date = datetime.datetime.combine(
                    now_date.date(), lunch_time["closed_time"]
                ) + datetime.timedelta(minutes=15)

            else:
                expired_date = now_date + datetime.timedelta(minutes=20)

        elif now_weekday in open_hours and open_hours[now_weekday]["opened_time"] > now_time:
            expired_date = datetime.datetime.combine(
                now_date.date(), open_hours[now_weekday]["opened_time"]
            ) + datetime.timedelta(minutes=15)

        else:
            date = now_date
            while True:
                date = date + datetime.timedelta(days=1)
                if date.weekday() in open_hours:
                    break

            expired_date = datetime.datetime.combine(
                date.date(), open_hours[date.weekday()]["opened_time"]
            ) + datetime.timedelta(minutes=15)

        attrs["expired_date"] = expired_date

        return attrs


class DiagnosisApplySerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)

    class Meta:
        model = Diagnosis
        fields = [
            "id",
            "patient_name",
            "request_date",
            "expired_date",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "request_date": {"read_only": True},
            "expired_date": {"read_only": True}
        }

    def validate(self, attrs):
        if timezone.now() > self.instance.expired_date:
            raise ValidationError("요청시간이 만료되었습니다.")
        attrs["is_apply"] = True
        return attrs
