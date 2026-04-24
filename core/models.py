from django.db import models
from django.contrib.auth.models import AbstractUser


# ---------------- USER MODEL ----------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    mobile = models.CharField(max_length=10)
    qr_code = models.ImageField(upload_to='qr/', null=True, blank=True)


# ---------------- MEDICAL RECORD ----------------
class MedicalRecord(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_records')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_records')
    description = models.TextField()
    file = models.FileField(upload_to='records/')
    created_at = models.DateTimeField(auto_now_add=True)


# ---------------- CONSENT ----------------
class Consent(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_consents')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_consents')
    status = models.CharField(max_length=20, default='pending')  # approved/rejected


# ---------------- ACCESS LOG (BLOCKCHAIN) ----------------
class AccessLog(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_logs')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_logs')
    action = models.CharField(max_length=50)
    hash = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


# ---------------- AI SUMMARY ----------------
class PatientSummary(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='summaries')
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# ---------------- RISK PREDICTION ----------------
class RiskPrediction(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='risk_predictions')
    risk = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


# ---------------- REMINDER ----------------
class Reminder(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    message = models.TextField()
    time = models.DateTimeField()

# ---------------- QR CODE ----------------
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    mobile = models.CharField(max_length=10)
    