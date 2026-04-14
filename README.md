#  Hospital Management System (Django + Serverless Email + Calendar Integration)

A full-stack Hospital Management System built using **Django (backend)** with a **Serverless Email Service (SMTP Gmail)** and **Calendar Integration** for managing appointments efficiently.

--- 
### signup page
<img width="1240" height="607" alt="image" src="https://github.com/user-attachments/assets/d3c43ff9-38a3-4d63-b5d7-e722c57edf91" />

### login page
<img width="1159" height="576" alt="image" src="https://github.com/user-attachments/assets/0fc865fd-5de4-461d-92c1-941e0da9bac0" />

### doctor dashboard
<img width="1230" height="605" alt="image" src="https://github.com/user-attachments/assets/d0dd412e-1a0d-42d8-b1f5-c215132909f3" />

### patient dashboard
<img width="1209" height="609" alt="image" src="https://github.com/user-attachments/assets/896dfeb9-d8db-4d62-881c-875b0a72051c" />



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
