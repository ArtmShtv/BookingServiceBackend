import smtplib
import os
from email.message import EmailMessage

from celery import shared_task

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from booking.models import UnitSchedule

User = get_user_model()
sender_email = os.environ.get("SENDER_EMAIL")
email_password = os.environ.get("EMAIL_PASSWORD")


@shared_task(ignore_result=True)
def send_confirm_email(
    user_id: int,
    unit_schedule_id: int,
    notes: str,
) -> None:
    user = get_object_or_404(User, id=user_id)
    unit_schedule = get_object_or_404(UnitSchedule, id=unit_schedule_id)

    receiver_email = "artemfilippov1985@gmail.com"
    body = f"""
        Dear {user.last_name} {user.first_name}

        We confirm your request for booking a {unit_schedule.unit.unit_type} {unit_schedule.unit.label}
        On {unit_schedule.date} {unit_schedule.start_time}-{unit_schedule.end_time}
        By {unit_schedule.unit.floor.building.address} {unit_schedule.unit.floor.building} {unit_schedule.unit.floor}

        Additional notes: {notes}
        
        If you decide to cancell a booking send us email on {sender_email}

        With best regards,
        Shitov Artem BookingService
    """

    message = EmailMessage()
    message["From"] = f"Shitov Artem BookingService <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = "Unit booking confirmation"
    message.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, email_password)
            server.send_message(message)

        print("Email sent successfully!")

    except smtplib.SMTPAuthenticationError as e:
        print("Authentication failed:", e)

    except smtplib.SMTPException as e:
        print("SMTP error:", e)