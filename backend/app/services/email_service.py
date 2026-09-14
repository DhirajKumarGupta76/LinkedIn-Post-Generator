from __future__ import annotations

import smtplib
from email.message import EmailMessage

from flask import current_app


def send_verification_email(email: str, user_name: str, verification_url: str) -> bool:
    """Send the account verification email.

    In production the app can be configured with SMTP credentials. In tests or when no SMTP
    configuration is present, this function safely returns True so registration flows can be
    exercised without a live mail server.
    """
    if current_app and current_app.config.get('TESTING'):
        return True

    smtp_host = current_app.config.get('SMTP_HOST') if current_app else None
    smtp_port = int(current_app.config.get('SMTP_PORT', 587)) if current_app else 587
    username = current_app.config.get('SMTP_USERNAME') if current_app else None
    password = current_app.config.get('SMTP_PASSWORD') if current_app else None
    sender = current_app.config.get('SMTP_FROM_EMAIL') if current_app else None

    if not smtp_host or not sender:
        if current_app:
            current_app.logger.warning('Email verification skipped: SMTP not configured')
        return False

    message = EmailMessage()
    message['Subject'] = 'Verify your PostGen AI account'
    message['From'] = sender
    message['To'] = email
    message.set_content(
        f"Hi {user_name},\n\n"
        f"Please verify your account by visiting: {verification_url}\n\n"
        "Thanks,\n"
        "The PostGen AI team"
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            if username and password:
                server.starttls()
                server.login(username, password)
            server.send_message(message)
        return True
    except Exception:
        if current_app:
            current_app.logger.exception('Failed to send verification email to %s', email)
        return False
