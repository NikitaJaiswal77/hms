#  Hospital Management System (Django + Serverless Email + Calendar Integration)

A full-stack Hospital Management System built using **Django (backend)** with a **Serverless Email Service (SMTP Gmail)** and **Calendar Integration** for managing appointments efficiently.

---

##  Features

### Doctor Features
- Create availability slots 
- View booked appointments
- Manage schedule

### Patient Features
- View available slots
- Book appointments
- Receive booking confirmation email

###  Email System
- Signup welcome email
- Booking confirmation email
- Gmail SMTP integration
- Serverless Python email API

###  Calendar Integration 
- Appointment date & time tracking
- Structured scheduling system
- Easy slot management
-  Google Calendar integration 

---

##  Project Structure
hms/ → Django backend
email_service/ → Serverless email API

---

##  Tech Stack

- Python 
- Django 
- PostgreSQL  
- SMTP (Gmail Email Service)
- Serverless Python Function
- HTML, CSS
- Calendar Scheduling 

---

##  Email Types

| Type | Description |
|------|------------|
| SIGNUP_WELCOME | Sent after user registration |
| BOOKING_CONFIRMATION | Sent after successful booking |

---

##  Appointment Flow

1. Doctor creates slots
2. Patient selects slot
3. Booking is saved
4. Email confirmation sent
5. Appointment tracked via calendar system

---

##  API Endpoint

### Send Email
POST /dev/send-email


### Request Body

```json
{
  "type": "SIGNUP_WELCOME",
  "email": "user@gmail.com"
}
