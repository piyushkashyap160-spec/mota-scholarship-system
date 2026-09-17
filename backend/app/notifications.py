import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from .models import NotificationLog, User, Application, Deficiency

class NotificationService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", "noreply@mota.gov.in")

    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        notification_type: str = "GENERAL_EMAIL",
        application_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> str:
        """
        Tries real SMTP if SMTP_HOST env var is set and configured with credentials.
        Falls back to logging email content to console + saving to NotificationLog table.
        Returns status: "SENT", "SIMULATED", or "FAILED".
        """
        status = "SIMULATED"
        preview = (body_html[:197] + "...") if len(body_html) > 200 else body_html

        # Try real SMTP only if host and credentials are configured
        if self.smtp_host and self.smtp_user and self.smtp_password:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = self.smtp_from
                msg["To"] = to_email
                part = MIMEText(body_html, "html")
                msg.attach(part)

                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=5) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.smtp_from, [to_email], msg.as_string())
                status = "SENT"
                print(f"[NOTIFICATION SERVICE - SMTP SENT] To: {to_email} | Subject: {subject}")
            except Exception as e:
                print(f"[NOTIFICATION SERVICE - SMTP FAILED] {e}. Falling back to SIMULATED.")
                status = "SIMULATED"
        else:
            print(f"[NOTIFICATION SERVICE - SIMULATED EMAIL] To: {to_email} | Subject: {subject}")
            print(f"[PREVIEW] {preview}")

        if db is not None:
            try:
                log_entry = NotificationLog(
                    recipient_email=to_email,
                    recipient_phone=None,
                    notification_type=notification_type,
                    subject=subject,
                    body_preview=preview,
                    status=status,
                    application_id=application_id,
                    created_at=datetime.utcnow()
                )
                db.add(log_entry)
                db.flush()
            except Exception as ex:
                print(f"[NOTIFICATION SERVICE - DB LOG ERROR] {ex}")

        return status

    def send_sms_stub(
        self,
        phone: str,
        message: str,
        notification_type: str = "SMS_ALERT",
        application_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> str:
        """
        Always logs to console + notification log (SMS is stub only).
        """
        status = "SIMULATED"
        preview = (message[:197] + "...") if len(message) > 200 else message
        print(f"[NOTIFICATION SERVICE - SIMULATED SMS] Phone: {phone} | Message: {message}")

        if db is not None:
            try:
                log_entry = NotificationLog(
                    recipient_email=None,
                    recipient_phone=phone,
                    notification_type=notification_type,
                    subject="SMS Dispatch Alert",
                    body_preview=preview,
                    status=status,
                    application_id=application_id,
                    created_at=datetime.utcnow()
                )
                db.add(log_entry)
                db.flush()
            except Exception as ex:
                print(f"[NOTIFICATION SERVICE - DB LOG ERROR] {ex}")

        return status

    def notify_submission_received(self, applicant: User, application: Application, db: Optional[Session] = None):
        app_num = application.application_number
        scheme_name = application.scheme.name if application.scheme else "MoTA Fellowship Scheme"
        subject = f"MoTA Application {app_num} Received Successfully"
        body = (
            f"Dear {applicant.full_name},<br/><br/>"
            f"Your application for <strong>{scheme_name}</strong> has been successfully received "
            f"under Application Number: <strong>{app_num}</strong>.<br/>"
            f"Your documents are currently undergoing automated scrutiny and verification.<br/>"
            f"You can track the progress of your application on the MoTA Fellowship Portal.<br/><br/>"
            f"Regards,<br/>Ministry of Tribal Affairs, Government of India"
        )
        self.send_email(
            to_email=applicant.email,
            subject=subject,
            body_html=body,
            notification_type="SUBMISSION_RECEIVED",
            application_id=application.id,
            db=db
        )
        if applicant.phone:
            self.send_sms_stub(
                phone=applicant.phone,
                message=f"MoTA: Application {app_num} for {scheme_name} received successfully. Check status on fellowship.tribal.gov.in",
                notification_type="SMS_SUBMISSION",
                application_id=application.id,
                db=db
            )

    def notify_deficiency_raised(self, applicant: User, application: Application, deficiency: Deficiency, db: Optional[Session] = None):
        app_num = application.application_number
        doc_name = (deficiency.doc_type or "Document").replace("_", " ").title()
        subject = f"Action Required: Document Deficiency in your MoTA Application {app_num}"
        body = (
            f"Dear {applicant.full_name},<br/><br/>"
            f"A document deficiency has been flagged by the MoTA Scrutiny Officer for Application <strong>{app_num}</strong>:<br/>"
            f"<strong>Document Type:</strong> {doc_name}<br/>"
            f"<strong>Reason / Remarks:</strong> {deficiency.reason}<br/><br/>"
            f"Please visit your Applicant Dashboard to resubmit the corrected document immediately.<br/>"
            f"Resubmission link: <a href='https://fellowship.tribal.gov.in/dashboard'>MoTA Applicant Dashboard</a><br/><br/>"
            f"Regards,<br/>Scrutiny Committee, Ministry of Tribal Affairs"
        )
        self.send_email(
            to_email=applicant.email,
            subject=subject,
            body_html=body,
            notification_type="DEFICIENCY_RAISED",
            application_id=application.id,
            db=db
        )
        if applicant.phone:
            self.send_sms_stub(
                phone=applicant.phone,
                message=f"MoTA Alert: Deficiency raised on {doc_name} for App {app_num}. Reason: {deficiency.reason}. Please resubmit on portal.",
                notification_type="SMS_DEFICIENCY",
                application_id=application.id,
                db=db
            )

    def notify_application_selected(self, applicant: User, application: Application, db: Optional[Session] = None):
        app_num = application.application_number
        scheme_name = application.scheme.name if application.scheme else "MoTA Fellowship Scheme"
        amt = f"Rs. {int(application.disbursement_amount):,}" if application.disbursement_amount else "Prescribed Scheme Rate"
        subject = "Congratulations! Your MoTA Fellowship Application has been Selected"
        body = (
            f"Dear {applicant.full_name},<br/><br/>"
            f"Congratulations! Your application <strong>{app_num}</strong> under <strong>{scheme_name}</strong> "
            f"has been officially <strong>SELECTED</strong> by the Ministry Selection Committee.<br/>"
            f"<strong>Sanctioned Disbursement Amount:</strong> {amt} per annum.<br/><br/>"
            f"<strong>Next Steps:</strong><br/>"
            f"1. Your PFMS DBT registration has been initialized with Canara Bank / National Payment Gateway.<br/>"
            f"2. Ensure your Aadhaar is linked to your bank account for seamless DBT credit.<br/>"
            f"3. Submit your annual fellowship renewal progress report prior to {application.renewal_due_date or '31st March'}.<br/><br/>"
            f"Warm regards,<br/>Ministry of Tribal Affairs, Government of India"
        )
        self.send_email(
            to_email=applicant.email,
            subject=subject,
            body_html=body,
            notification_type="APPLICATION_SELECTED",
            application_id=application.id,
            db=db
        )
        if applicant.phone:
            self.send_sms_stub(
                phone=applicant.phone,
                message=f"MoTA: Hearty Congratulations! Application {app_num} has been SELECTED for {scheme_name}. Amount: {amt}. Check portal for sanction letter.",
                notification_type="SMS_SELECTED",
                application_id=application.id,
                db=db
            )

    def notify_application_rejected(self, applicant: User, application: Application, reason: str, db: Optional[Session] = None):
        app_num = application.application_number
        subject = f"MoTA Application Update: {app_num}"
        body = (
            f"Dear {applicant.full_name},<br/><br/>"
            f"This is an update regarding your Application <strong>{app_num}</strong>.<br/>"
            f"After thorough scrutiny against statutory scheme guidelines, your application could not be selected for award.<br/>"
            f"<strong>Reason:</strong> {reason or 'Did not fulfill mandatory eligibility criteria.'}<br/><br/>"
            f"If you believe this determination was made in error, you may file a formal grievance on the "
            f"<a href='https://tribal.nic.in/Grievance.aspx'>MoTA Central Grievance Redressal Portal</a> within 30 days.<br/><br/>"
            f"Regards,<br/>Scrutiny Committee, Ministry of Tribal Affairs"
        )
        self.send_email(
            to_email=applicant.email,
            subject=subject,
            body_html=body,
            notification_type="APPLICATION_REJECTED",
            application_id=application.id,
            db=db
        )
        if applicant.phone:
            self.send_sms_stub(
                phone=applicant.phone,
                message=f"MoTA Update: Application {app_num} could not be selected. Reason: {reason or 'Eligibility criteria not met'}. Details on portal.",
                notification_type="SMS_REJECTED",
                application_id=application.id,
                db=db
            )

notification_service = NotificationService()
