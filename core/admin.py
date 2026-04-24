from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(MedicalRecord)
admin.site.register(Consent)
admin.site.register(AccessLog)
admin.site.register(PatientSummary)
admin.site.register(RiskPrediction)
admin.site.register(Reminder)
