import datetime
import json
import logging
import os
import platform
import shutil
import smtplib
import socket
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(address, subject, text, attachment_path=None):
    msg = MIMEMultipart()
    msg["From"] = os.environ["EMAIL_ADDRESS"]
    msg["To"] = address
    msg["Subject"] = subject
    msg.attach(MIMEText(text, "plain"))
    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}"
            )
            msg.attach(part)
    try:
        with smtplib.SMTP("smtp-mail.outlook.com", "587") as server:
            server.ehlo(socket.gethostname().lower())  # workaround to avoid SMTPError
            server.starttls()
            server.ehlo(socket.gethostname().lower())
            server.login(os.environ["EMAIL_ADDRESS"], os.environ["EMAIL_PASSWORD"])
            server.sendmail(os.environ["EMAIL_ADDRESS"], address, msg.as_string())
            logging.info(f"{subject} email is sent successfully to {address}!")
    except Exception as e:
        logging.exception(f"Failed to send email: {e}", exc_info=True)
    else:
        if os.path.exists(attachment_path):
            os.remove(attachment_path)


def get_system_info():
    return {
        "platform": platform.platform(),
        "architecture": platform.architecture(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "java_version": platform.java_ver(),
        "libc_version": platform.libc_ver(),
    }


def archive_kivy_logs():
    logs_archive_filename = f"kivy_logs_{datetime.date.today().isoformat()}"
    archive_path = os.path.join(os.environ["STORAGE_PATH"], logs_archive_filename)
    shutil.make_archive(archive_path, "zip", os.path.join(os.environ["STORAGE_PATH"], "logs"))
    return f"{archive_path}.zip"


def send_crash_report(func, e=None):
    cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = f"{cur_time}\n{json.dumps(get_system_info(), indent=3)}\nException in {func.__module__}.{func.__name__}: {e}"
    send_email("helgamogish@gmail.com", "Crash report", text, archive_kivy_logs())
