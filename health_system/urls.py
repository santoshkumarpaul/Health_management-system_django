from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from core import views as core_views


urlpatterns = [
    path('admin/', admin.site.urls),

    # Login Page
    path('', core_views.login_page, name='login'),

    # OTP APIs
    path('auth/send-otp/', core_views.send_otp, name='send_otp'),
    path('auth/verify-otp/', core_views.verify_otp, name='verify_otp'),

    # UPLOAD
    path('upload/', core_views.upload_record, name='upload_record'),
    path('upload-page/', core_views.upload_page, name='upload_page'),

    #Consent API
    path('request-consent/', core_views.request_consent, name='request_consent'),
    path('request-consent/', core_views.request_consent, name='request_consent'),
    path('view-records/', core_views.view_records, name='view_records'),
    path('consent-page/', core_views.consent_page),

    #AI FUNCTION 
    path('generate-summary/', core_views.generate_patient_summary, name='generate_summary'),
    path('summary-page/', core_views.summary_page, name='summary_page'),

    #ML PREDICTION
    path('predict/', core_views.predict_disease_view),
    path('predict-page/', core_views.predict_page),

    #DASHBOARD
    path('dashboard/', core_views.dashboard),
    
    #CHART API
    path('chart-data/', core_views.patient_chart_data),

    #QR-CODE
    path('get-qr/<int:user_id>/', core_views.get_qr),
    path('qr-page/', core_views.qr_page),

    #Dr. DASHBOARD
    path('doctor-dashboard/', core_views.doctor_dashboard),
]

# Media files (for uploads, QR)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

