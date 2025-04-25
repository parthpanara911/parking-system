from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from app import mail
import logging
from datetime import datetime

def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        try:
            app.logger.info(f"Attempting to send email to {msg.recipients}")
            mail.send(msg)
            app.logger.info(f"Email successfully sent to {msg.recipients}")
        except Exception as e:
            app.logger.error(f"Error sending email: {str(e)}")
            # Log more detailed information for debugging
            app.logger.error(f"Mail config: MAIL_SERVER={app.config.get('MAIL_SERVER')}, "
                           f"MAIL_PORT={app.config.get('MAIL_PORT')}, "
                           f"MAIL_USE_TLS={app.config.get('MAIL_USE_TLS')}, "
                           f"MAIL_USERNAME={app.config.get('MAIL_USERNAME')}")

def send_email(subject, recipients, text_body, html_body=None, sender=None):
    """Send an email."""
    app = current_app._get_current_object()
    msg = Message(
        subject=subject,
        recipients=recipients,
        body=text_body,
        html=html_body,
        sender=sender or current_app.config.get('MAIL_DEFAULT_SENDER')
    )
    # Log message details for debugging
    app.logger.info(f"Preparing to send email to {recipients}")
    app.logger.info(f"Subject: {subject}")
    app.logger.info(f"From: {sender or current_app.config.get('MAIL_DEFAULT_SENDER')}")
    
    if current_app.config.get('TESTING', False):
        # Don't send emails in testing mode
        return
    
    # Send email in a background thread to avoid blocking
    Thread(target=send_async_email, args=(app, msg)).start()

def send_verification_email(user, token):
    """Send an email verification link to the user."""
    verification_url = current_app.config.get('BASE_URL', 'http://localhost:5000') + \
                       f'/auth/verify-email/{token}'
    
    current_app.logger.info(f"Sending verification email to {user.email} with token {token}")
    current_app.logger.info(f"Verification URL: {verification_url}")
    
    subject = 'Verify Your Email - Smart Parking System'
    
    send_email(
        subject=subject,
        recipients=[user.email],
        text_body=render_template(
            'email/verify/email.txt',
            user=user,
            verification_url=verification_url
        ),
        html_body=render_template(
            'email/verify/email.html',
            user=user,
            verification_url=verification_url
        )
    )

def send_password_reset_email(user, token):
    """Send a password reset link to the user."""
    reset_url = current_app.config.get('BASE_URL', 'http://localhost:5000') + \
                f'/auth/reset-password/{token}'
    
    current_app.logger.info(f"Sending password reset email to {user.email} with token {token}")
    current_app.logger.info(f"Reset URL: {reset_url}")
    
    subject = 'Reset Your Password - Smart Parking System'
    
    send_email(
        subject=subject,
        recipients=[user.email],
        text_body=render_template(
            'email/reset/email.txt',
            user=user,
            reset_url=reset_url
        ),
        html_body=render_template(
            'email/reset/email.html',
            user=user,
            reset_url=reset_url
        )
    )
def send_booking_confirmation(user, booking):
    """Send a booking confirmation email to the user."""
    subject = 'Booking Confirmation - Smart Parking System'
    text_body = f'''Hello {user.username},

Your booking (Reference: {booking.reference}) has been confirmed.
Details:
- Parking Slot: {booking.parking_slot.slot_number if booking.parking_slot else 'Not assigned yet'}
- Start Time: {booking.booking_start.strftime('%Y-%m-%d %H:%M') if booking.booking_start else 'Not specified'}
- End Time: {booking.booking_end.strftime('%Y-%m-%d %H:%M') if booking.booking_end else 'Not specified'}
- Amount: ${booking.total_amount if booking.total_amount else 'To be calculated'}

Thank you for using our service!

Best regards,
The Smart Parking System Team
'''
    
    html_body = f'''
    <p>Hello {user.username},</p>
    <p>Your booking (Reference: <strong>{booking.reference}</strong>) has been confirmed.</p>
    <h3>Details:</h3>
    <ul>
        <li>Parking Slot: {booking.parking_slot.slot_number if booking.parking_slot else 'Not assigned yet'}</li>
        <li>Start Time: {booking.booking_start.strftime('%Y-%m-%d %H:%M') if booking.booking_start else 'Not specified'}</li>
        <li>End Time: {booking.booking_end.strftime('%Y-%m-%d %H:%M') if booking.booking_end else 'Not specified'}</li>
        <li>Amount: ${booking.total_amount if booking.total_amount else 'To be calculated'}</li>
    </ul>
    <p>Thank you for using our service!</p>
    <p>Best regards,<br>The Smart Parking System Team</p>
    '''
    
    send_email(
        subject=subject,
        recipients=[user.email],
        text_body=text_body,
        html_body=html_body
    )

def send_payment_receipt(user, payment, booking):
    """Send a payment receipt email to the user."""
    send_email(
        subject='Payment Receipt - Smart Parking System',
        recipients=[user.email],
        text_body=render_template(
            'email/payment_receipt.txt',
            user=user,
            payment=payment,
            booking=booking,
            now=datetime.utcnow()
        ),
        html_body=render_template(
            'email/payment_receipt.html',
            user=user,
            payment=payment,
            booking=booking,
            now=datetime.utcnow()
        )
    ) 
