# AutomacaoSelic/email_notifier.py

from email.mime.nonmultipart import MIMENonMultipart
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def enviar_email_de_erro(
    assunto: str, corpo_email: str, destinatario: str, config_email: dict
):
    if not all(
        [
            config_email["servidor_smtp"],
            config_email["porta"],
            config_email["usuario"],
            config_email["senha"],
        ]
    ):
        logging.error(
            "Configurações de email incompletas. Não é possível enviar o alerta."
        )
        return

    remetente = config_email["usuario"]

    msg = MIMEMultipart()
    msg["From"] = remetente
    msg["To"] = destinatario
    msg["Subject"] = assunto

    msg.attach(MIMEText(corpo_email), "plain")

    try:
        logging.info(f"Tentando enviar email de alerta para {destinatario}...")

        server = smtplib.SMTP(config_email["servidor_smtp"], config_email["porta"])
        server.starttls()
        server.login(remetente, config_email["senha"])

        texto = msg.as_string()
        server.sendmail(remetente, destinatario, texto)

        logging.info("Email de alerta enviado com sucesso.")

    except Exception as e:
        logging.error(f"FALHA AO ENVIAR EMAIL DE ALERTA: {e}")

    finally:
        if "server" in locals():
            server.quit()
