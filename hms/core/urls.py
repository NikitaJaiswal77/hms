from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('add-slot/', views.add_slot, name='add_slot'),
    path('book-slot/<int:slot_id>/', views.book_slot, name='book_slot'),
    path('edit-slot/<int:slot_id>/', views.edit_slot, name='edit_slot'),
]