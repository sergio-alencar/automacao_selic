import smtplib
import logging
from pathlib import Path
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from config.settings import EmailConfig

MIME_TEXT_FORMAT: str = "plain"
MIME_FILE_MAIN_TYPE: str = "application"
MIME_FILE_SUB_TYPE: str = "octet-stream"
HEADER_DISPOSITION: str = "Content-Disposition"


def _is_config_valid(config: EmailConfig) -> bool:
    return all(
        [
            config.smtp_server,
            config.port,
            config.user,
            config.password,
        ]
    )


def _build_email_message(
    subject: str,
    body: str,
    sender: str,
    recipient: str,
    attachment_path: Optional[Path] = None,
) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, MIME_TEXT_FORMAT))

    if attachment_path and attachment_path.is_file():
        try:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase(MIME_FILE_MAIN_TYPE, MIME_FILE_SUB_TYPE)
                part.set_payload(attachment.read())

            encoders.encode_base64(part)

            part.add_header(
                HEADER_DISPOSITION,
                f"attachment; filename={attachment_path.name}",
            )
            msg.attach(part)

        except Exception as e:
            logging.error(f"Failed to attach file '{attachment_path.name}': {e}")

    return msg


def send_alert_email(
    subject: str,
    body: str,
    recipient: str,
    config: EmailConfig,
    attachment_path: Optional[Path] = None,
) -> None:
    """Valida as configurações, monta a mensagem e dispara o e-mail via SMTP."""

    if not _is_config_valid(config):
        logging.error("Incomplete email configuration. Cannot send alert.")
        return

    sender: str = config.user
    msg: MIMEMultipart = _build_email_message(subject, body, sender, recipient, attachment_path)

    try:
        logging.info(f"Attempting to send alert email to {recipient}...")

        with smtplib.SMTP(config.smtp_server, config.port) as server:
            server.starttls()
            server.login(sender, config.password)
            server.sendmail(sender, recipient, msg.as_string())

        logging.info("Alert email sent successfully.")

    except Exception as e:
        logging.error(f"FAILED TO SEND ALERT EMAIL: {e}")
