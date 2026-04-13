from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

class Availability(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.doctor.username} - {self.date} {self.start_time}"

class Booking(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_bookings')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_bookings')
    slot = models.OneToOneField(Availability, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} booked {self.doctor.username}"