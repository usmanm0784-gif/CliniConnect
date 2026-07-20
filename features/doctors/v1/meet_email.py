import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader
from core.config import (SMTP_SERVER, SMTP_PORT, SMTP_EMAIL,SMTP_PASSWORD)

from logger import logger


env = Environment(
    loader=FileSystemLoader("templates")
)


def send_appointment_email(receiver_email: str, name: str, doctor_name: str, patient_name: str, appointment_date: str,
    appointment_time: str, appointment_id: str, appointment_link: str):

    template = env.get_template("google_meet_email.html")

    html = template.render(year=2026, name=name, doctor_name=doctor_name, patient_name=patient_name,appointment_date=appointment_date,
        appointment_time=appointment_time, appointment_id=appointment_id, appointment_link= appointment_link)

    message = MIMEMultipart("alternative")

    message["Subject"] = "Appointment Booked Successfully"
    message["From"] = SMTP_EMAIL
    message["To"] = receiver_email

    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
            smtp.sendmail(
                SMTP_EMAIL,
                receiver_email,
                message.as_string()
            )
    except Exception as e:
        logger.exception(f"Failed to send email to {receiver_email}: {e}")
        print(f"Failed to send email to {receiver_email}: {e}")
        return False