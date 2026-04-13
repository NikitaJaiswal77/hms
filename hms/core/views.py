from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import User
from django.contrib.auth.decorators import login_required
from .models import Availability, Booking
from django.db import transaction
from django.shortcuts import get_object_or_404
import requests


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

            if user.role == 'doctor':
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
        'bookings': bookings
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
        'slots': slots
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

        Booking.objects.create(
            patient=request.user,
            doctor=slot.doctor,
            slot=slot
        )

    
    try:
        requests.post("http://localhost:3000/dev/send-email", json={
            "type": "BOOKING_CONFIRMATION",
            "email": request.user.email
        })
    except Exception as e:
        print("Email API failed:", e)

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