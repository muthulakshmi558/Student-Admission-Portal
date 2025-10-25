# utils/notifications.py
import threading
from flask_mail import Message
from twilio.rest import Client

def send_email_async(app, mail, subject, recipients, html_body):
    with app.app_context():
        msg = Message(subject=subject, recipients=recipients, html=html_body)
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Failed to send email: {e}")

def send_sms_async(app, twilio_sid, twilio_token, from_number, to_number, body):
    def _send():
        try:
            client = Client(twilio_sid, twilio_token)
            client.messages.create(body=body, from_=from_number, to=to_number)
        except Exception as e:
            app.logger.error(f"Failed to send SMS: {e}")

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()

def notify_student(app, mail, twilio_cfg, student, subject, html_body, sms_body):
    # send email in background
    t1 = threading.Thread(target=send_email_async, args=(app, mail, subject, [student.email], html_body), daemon=True)
    t1.start()

    # send sms in background if phone exists
    if twilio_cfg.get('TWILIO_ACCOUNT_SID') and student.phone:
        send_sms_async(app, twilio_cfg['TWILIO_ACCOUNT_SID'], twilio_cfg['TWILIO_AUTH_TOKEN'],
                       twilio_cfg['TWILIO_PHONE_NUMBER'], student.phone, sms_body)
