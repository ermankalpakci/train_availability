import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass

@dataclass
class EmailConfig:
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    timeout: int = 30

class EmailSendError(Exception):
    pass
class EmailSender:
    def __init__(self, config: EmailConfig = None):
        self.config = config or EmailConfig()
        self.logger = logging.getLogger(__name__)

    def send_test_email(self, email: str, password: str) -> None:

        subject = "Train Availability Notification Test"
        # Convert result dict to a formatted string
        body = "This is a test email."

        try:
            message = MIMEMultipart()
            message["From"] = email
            message["To"] = email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port, 
                            timeout=self.config.timeout) as server:
                server.starttls()
                server.login(email, password)
                server.sendmail(email, email, message.as_string())
                
            self.logger.info(f"Email sent successfully to {email}")
            
        except smtplib.SMTPAuthenticationError as e:
            logging.error("SMTP authentication failed")
            raise EmailSendError("Failed to authenticate with email server") from e
        except smtplib.SMTPConnectError as e:
            logging.error("Failed to connect to SMTP server")
            raise EmailSendError("Could not connect to email server") from e
        except smtplib.SMTPException as e:
            logging.error(f"SMTP error occurred: {str(e)}")
            raise EmailSendError(f"Email sending failed: {str(e)}") from e
        except Exception as e:
            logging.exception("Unexpected error while sending email")  # Logs full traceback
            raise EmailSendError(f"Unexpected error: {str(e)}") from e