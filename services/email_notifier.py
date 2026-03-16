import smtplib
import logging
from typing import Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_alert_email(subject: str, body: str, recipient: str, config: Dict[str, Any]) -> None:
    if not all(
        [
            config.get("smtp_server"),
            config.get("port"),
            config.get("user"),
            config.get("password"),
        ]
    ):
        logging.error("Incomplete email configuration. Cannot send alert.")
        return

    sender: str = config["user"]
    msg: MIMEMultipart = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        logging.info(f"Attempting to send alert email to {recipient}...")

        with smtplib.SMTP(config["smtp_server"], config["port"]) as server:
            server.starttls()
            server.login(sender, config["password"])
            server.sendmail(sender, recipient, msg.as_string())

        logging.info("Alert email sent successfully.")

    except Exception as e:
        logging.error(f"FAILED TO SEND ALERT EMAIL: {e}")
