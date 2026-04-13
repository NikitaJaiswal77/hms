from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import User
from django.contrib.auth.decorators import login_required
from .models import Availability, Booking
from django.db import transaction
from django.shortcuts import get_object_or_404
import requests
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.urls import reverse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from datetime import datetime
from pathlib import Path

GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']
GOOGLE_CLIENT_SECRET_FILE = Path(settings.BASE_DIR) / 'client_secret.json'


def _build_flow(redirect_uri, state=None):
    return Flow.from_client_secrets_file(
        str(GOOGLE_CLIENT_SECRET_FILE),
        scopes=GOOGLE_CALENDAR_SCOPES,
        state=state,
        redirect_uri=redirect_uri
    )

@login_required
def google_connect(request):
    redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
    flow = _build_flow(redirect_uri=redirect_uri)

    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    request.session['state'] = state
    request.session['google_redirect_uri'] = redirect_uri
    if getattr(flow, "code_verifier", None):
        request.session['google_code_verifier'] = flow.code_verifier
    return redirect(auth_url)

@login_required
def google_callback(request):
    state = request.session.get('state') or request.GET.get('state')
    redirect_uri = request.session.get('google_redirect_uri') or settings.GOOGLE_OAUTH_REDIRECT_URI
    code_verifier = request.session.get('google_code_verifier')
    if not state:
        return HttpResponseBadRequest("Google auth state missing. Please reconnect calendar.")

    flow = _build_flow(redirect_uri=redirect_uri, state=state)
    if code_verifier:
        flow.code_verifier = code_verifier

    try:
        flow.fetch_token(
            authorization_response=request.build_absolute_uri()
        )
    except Exception:
        request.session.pop('state', None)
        request.session.pop('google_redirect_uri', None)
        request.session.pop('google_code_verifier', None)
        return redirect(reverse('google_connect'))

    credentials = flow.credentials
    user = request.user
    

    user.google_token = credentials.token
    if credentials.refresh_token:
        user.refresh_token = credentials.refresh_token
    user.token_uri = credentials.token_uri or "https://oauth2.googleapis.com/token"

    client_config = flow.client_config.get('web', flow.client_config)
    user.client_id = client_config.get('client_id', '')
    user.client_secret = client_config.get('client_secret', '')
    user.save()
    request.session.pop('state', None)
    request.session.pop('google_redirect_uri', None)
    request.session.pop('google_code_verifier', None)

    return redirect('patient_dashboard')

def create_event(user, title, date, start_time, end_time):
    if not user.google_token:
        raise ValueError(f"User {user.username} has not connected Google Calendar.")

    start_dt = datetime.combine(date, start_time)
    end_dt = datetime.combine(date, end_time)

    creds = Credentials(
        token=user.google_token,
        refresh_token=user.refresh_token,
        token_uri=user.token_uri or "https://oauth2.googleapis.com/token",
        client_id=user.client_id,
        client_secret=user.client_secret,
        scopes=GOOGLE_CALENDAR_SCOPES
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        user.google_token = creds.token
        user.save(update_fields=['google_token'])

    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': title,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
    }

    print("CALENDAR FUNCTION CALLED")

    service.events().insert(calendarId='primary', body=event).execute()
    print("EVENT CREATED:", title)
# def book_appointment(request):
#     booking = Booking.objects.create(...)

#     doctor = booking.doctor
#     patient = booking.patient

#     title_doctor = f"Appointment with {patient.username}"
#     title_patient = f"Appointment with Dr {doctor.username}"

#     create_event(doctor, title_doctor, booking.start_time, booking.end_time)
#     create_event(patient, title_patient, booking.start_time, booking.end_time)

# return JsonResponse({"message": "Booked + Calendar updated"})
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )

        try:
            requests.post("http://localhost:3000/dev/send-email", json={
                "type": "SIGNUP_WELCOME",
                "email": user.email
            })
        except Exception as e:
            print("Email API failed:", e)

        login(request, user)

        if role == 'doctor':
            return redirect('doctor_dashboard')
        else:
            return redirect('patient_dashboard')

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if request.user.role == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def doctor_dashboard(request):
    if request.user.role != 'doctor':
        return redirect('login')

    slots = Availability.objects.filter(doctor=request.user)
    bookings = Booking.objects.filter(doctor=request.user)

    return render(request, 'doctor_dashboard.html', {
        'slots': slots,
        'bookings': bookings,
        'is_google_connected': bool(request.user.google_token)
    })
    
@login_required
def add_slot(request):
    if request.user.role != 'doctor':
        return redirect('login')

    if request.method == 'POST':
        date = request.POST['date']
        start = request.POST['start']
        end = request.POST['end']

        Availability.objects.create(
            doctor=request.user,
            date=date,
            start_time=start,
            end_time=end
        )

        return redirect('doctor_dashboard')

    return render(request, 'add_slot.html')

@login_required
def patient_dashboard(request):
    if request.user.role != 'patient':
        return redirect('login')

    slots = Availability.objects.filter(is_booked=False)

    return render(request, 'patient_dashboard.html', {
        'slots': slots,
        'is_google_connected': bool(request.user.google_token)
    })
    

@login_required
def book_slot(request, slot_id):
    if request.user.role != 'patient':
        return redirect('login')

    with transaction.atomic():
        slot = Availability.objects.select_for_update().get(id=slot_id)

        if slot.is_booked:
            return redirect('patient_dashboard')

        slot.is_booked = True
        slot.save()

        booking = Booking.objects.create(
            patient=request.user,
            doctor=slot.doctor,
            slot=slot
        )

    #  EMAIL SERVICE 
    try:
        requests.post("http://localhost:3000/dev/send-email", json={
            "type": "BOOKING_CONFIRMATION",
            "email": request.user.email
        })
    except Exception as e:
        print("Email API failed:", e)

    #  GOOGLE CALENDAR
    try:
        create_event(
            booking.doctor,
            f"Appointment with {booking.patient.username}",
            slot.date,
            slot.start_time,
            slot.end_time
        )
    except Exception as e:
        print("Doctor calendar API failed:", e)

    try:
        create_event(
            booking.patient,
            f"Appointment with Dr {booking.doctor.username}",
            slot.date,
            slot.start_time,
            slot.end_time
        )
    except Exception as e:
        print("Patient calendar API failed:", e)

    return redirect('patient_dashboard')



@login_required
def edit_slot(request, slot_id):
    slot = get_object_or_404(Availability, id=slot_id)

    
    if slot.doctor != request.user:
        return redirect('doctor_dashboard')

    
    if slot.is_booked:
        return redirect('doctor_dashboard')

    if request.method == 'POST':
        slot.date = request.POST['date']
        slot.start_time = request.POST['start']
        slot.end_time = request.POST['end']
        slot.save()

        return redirect('doctor_dashboard')

    return render(request, 'edit_slot.html', {'slot': slot})

