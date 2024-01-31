from django.contrib import admin

from doctor.models import Doctor, Diagnosis, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    pass


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    pass


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    pass
