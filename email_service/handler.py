import json
import smtplib
from email.mime.text import MIMEText

import json
import smtplib
from email.mime.text import MIMEText


def send_email(event, context):
    try:
       
        body = json.loads(event['body'])

        to_email = body.get("email")
        email_type = body.get("type")

        sender = "nikitajaiswal1907@gmail.com"
        password = "ayje xfur bigc qgpz"

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(sender, password)

       
        subject = "Test"
        message = "Test email"

        
        if email_type == "SIGNUP_WELCOME":
            subject = "Welcome to Hospital Management System 🎉"
            message = "Thanks for signing up! We are happy to have you."

        elif email_type == "BOOKING_CONFIRMATION":
            subject = "Booking Confirmed 🎊"
            message = "Your appointment has been successfully booked. Thank you for choosing us 😊"

        
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email

       
        server.send_message(msg)
        server.quit()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Email sent successfully",
                "type": email_type,
                "to": to_email
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }