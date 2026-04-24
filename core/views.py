from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
import random
import hashlib
from .models import AccessLog
from .models import User, MedicalRecord, Consent
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from .models import PatientSummary
from .ml_model import predict_disease
from django.http import JsonResponse
from .models import MedicalRecord


# ---------------- LOGIN PAGE ----------------
def login_page(request):
    return render(request, "login.html")


# ---------------- SEND OTP ----------------
@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        mobile = request.POST.get("mobile")

        if not mobile:
            return JsonResponse({"error": "Mobile number required"}, status=400)

        otp = str(random.randint(1000, 9999))

        request.session['otp'] = otp
        request.session['mobile'] = mobile

        print("OTP:", otp)

        return JsonResponse({"message": "OTP sent"})

    return JsonResponse({"error": "Invalid request"}, status=400)


# ---------------- VERIFY OTP ----------------
@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        entered = request.POST.get("otp")
        session_otp = request.session.get("otp")
        mobile = request.session.get("mobile")

        if not session_otp:
            return JsonResponse({"error": "Session expired"}, status=400)

        if entered == session_otp:
            user, created = User.objects.get_or_create(
                username=mobile,
                defaults={"mobile": mobile, "role": "patient"}
            )

            login(request, user)

            # ✅ Role-based redirect
            if user.role == "doctor":
                redirect_url = "/doctor-dashboard/"
            else:
                redirect_url = "/dashboard/"

            return JsonResponse({
                "message": "Login successful",
                "redirect": redirect_url
            })

        return JsonResponse({"error": "Invalid OTP"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)



# ---------------- UPLOAD RECORD ----------------
@csrf_exempt
def upload_record(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient_id")
        doctor_id = request.POST.get("doctor_id")
        description = request.POST.get("description")
        file = request.FILES.get("file")

        if not all([patient_id, doctor_id, file]):
            return JsonResponse({"error": "Missing fields"}, status=400)

        try:
            patient = User.objects.get(id=patient_id)
            doctor = User.objects.get(id=doctor_id)

            MedicalRecord.objects.create(
                patient=patient,
                doctor=doctor,
                description=description,
                file=file
            )

            return JsonResponse({"message": "Record uploaded successfully"})

        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid user"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


def upload_page(request):
    return render(request, "upload.html")


# ---------------- REQUEST CONSENT ----------------
@csrf_exempt
def request_consent(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient_id")
        doctor_id = request.POST.get("doctor_id")

        try:
            patient = User.objects.get(id=patient_id)
            doctor = User.objects.get(id=doctor_id)

            Consent.objects.create(
                patient=patient,
                doctor=doctor,
                status="pending"
            )

            return JsonResponse({"message": "Consent request sent"})

        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid user"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


# ---------------- UPDATE CONSENT ----------------
@csrf_exempt
def update_consent(request):
    if request.method == "POST":
        consent_id = request.POST.get("consent_id")
        status = request.POST.get("status")

        try:
            consent = Consent.objects.get(id=consent_id)
            consent.status = status
            consent.save()

            return JsonResponse({"message": "Consent updated"})

        except Consent.DoesNotExist:
            return JsonResponse({"error": "Consent not found"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


# ---------------- VIEW RECORDS ----------------
@csrf_exempt
def view_records(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient_id")
        doctor_id = request.POST.get("doctor_id")

        consent = Consent.objects.filter(
            patient_id=patient_id,
            doctor_id=doctor_id,
            status="approved"
        ).first()

        if not consent:
            return JsonResponse({"error": "Access denied"}, status=403)

        records = MedicalRecord.objects.filter(patient_id=patient_id)

        # 🔥 BLOCKCHAIN LOGGING
        log_data = f"{patient_id}-{doctor_id}-view"
        hash_value = generate_hash(log_data)

        AccessLog.objects.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            action="view_records",
            hash=hash_value
        )

        data = []
        for r in records:
            data.append({
                "description": r.description,
                "file": r.file.url
            })

        return JsonResponse({"records": data})

    return JsonResponse({"error": "Invalid request"}, status=400)
  


# ---------------- PAGE ----------------
def consent_page(request):
    return render(request, "consent.html")

# ---------------- Hash Function ----------------
def generate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

# ---------------- AI FUNCTION ----------------
def generate_summary(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()

    summary = summarizer(parser.document, 2)

    return " ".join(str(sentence) for sentence in summary)

@csrf_exempt
def generate_patient_summary(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient_id")

        records = MedicalRecord.objects.filter(patient_id=patient_id)

        if not records:
            return JsonResponse({"error": "No records found"}, status=400)

        # Combine all descriptions
        full_text = ""
        for r in records:
            full_text += r.description + " "

        # Generate AI summary
        summary_text = generate_summary(full_text)

        # Save in DB
        PatientSummary.objects.create(
            patient_id=patient_id,
            summary=summary_text
        )

        return JsonResponse({"summary": summary_text})

    return JsonResponse({"error": "Invalid request"}, status=400)

def summary_page(request):
    return render(request, "summary.html")

# ---------------- PREDICTION API ----------------

@csrf_exempt
def predict_disease_view(request):
    if request.method == "POST":
        try:
            glucose = float(request.POST.get("glucose"))
            bp = float(request.POST.get("bp"))
            bmi = float(request.POST.get("bmi"))
            age = float(request.POST.get("age"))

            input_data = [0, glucose, bp, 0, 0, bmi, 0, age]

            result = predict_disease(input_data)

            return JsonResponse({"risk": result})

        except:
            return JsonResponse({"error": "Invalid input"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

def predict_page(request):
    return render(request, "predict.html")

# ---------------- PREDICTION API ----------------
def dashboard(request):
    return render(request, "dashboard.html")

# ---------------- CHART API ----------------


def patient_chart_data(request):
    patient_id = request.GET.get("patient_id")

    records = MedicalRecord.objects.filter(patient_id=patient_id).order_by('created_at')

    labels = []
    glucose_values = []

    for r in records:
        labels.append(r.created_at.strftime("%d-%m"))

        # assume glucose is written in description like "glucose:120"
        try:
            text = r.description.lower()
            if "glucose" in text:
                value = int(text.split("glucose:")[1].split()[0])
                glucose_values.append(value)
            else:
                glucose_values.append(0)
        except:
            glucose_values.append(0)

    return JsonResponse({
        "labels": labels,
        "data": glucose_values
    })

# ---------------- QR-CODE API ----------------
def get_qr(request, user_id):
    try:
        user = User.objects.get(id=user_id)

        if user.qr_code:
            return JsonResponse({
                "qr": user.qr_code.url
            })

        return JsonResponse({"error": "QR not found"})

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"})
    
def qr_page(request):
    return render(request, "qr.html")   
#---------------------Dr. DASHBOARD---------------
def doctor_dashboard(request):
    return render(request, "doctor_dashboard.html")