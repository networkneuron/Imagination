"""
Email Automation Module

Handles email sending, scheduling, and automated responses.
"""

import smtplib
import logging
import json
import schedule
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import yagmail
import imaplib
import email
from email.header import decode_header

class EmailAutomation:
    """Handles email automation tasks"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.config = self.config_manager.load_config()
        self.email_config = self.config.get('email', {})
        self.scheduled_emails = []
        self.auto_reply_rules = []
        
        # Initialize email client
        self.smtp_client = None
        self.imap_client = None
        
    def setup_smtp(self, smtp_server: str, smtp_port: int, username: str, password: str, 
                   use_tls: bool = True) -> bool:
        """Setup SMTP connection for sending emails"""
        try:
            self.smtp_client = smtplib.SMTP(smtp_server, smtp_port)
            
            if use_tls:
                self.smtp_client.starttls()
            
            self.smtp_client.login(username, password)
            
            self.logger.info("SMTP connection established successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up SMTP: {e}")
            return False
    
    def setup_imap(self, imap_server: str, imap_port: int, username: str, password: str, 
                   use_ssl: bool = True) -> bool:
        """Setup IMAP connection for reading emails"""
        try:
            if use_ssl:
                self.imap_client = imaplib.IMAP4_SSL(imap_server, imap_port)
            else:
                self.imap_client = imaplib.IMAP4(imap_server, imap_port)
            
            self.imap_client.login(username, password)
            
            self.logger.info("IMAP connection established successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up IMAP: {e}")
            return False
    
    def send_email(self, to: str, subject: str, body: str, from_email: str = None, 
                   cc: List[str] = None, bcc: List[str] = None, attachments: List[str] = None,
                   html: bool = False) -> bool:
        """Send an email"""
        try:
            if not self.smtp_client:
                # Try to setup SMTP from config
                if not self._setup_from_config():
                    return False
            
            # Create message
            msg = MIMEMultipart('alternative') if html else MIMEMultipart()
            msg['From'] = from_email or self.email_config.get('from_email', '')
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # Add body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {file_path.split("/")[-1]}'
                        )
                        msg.attach(part)
                    except Exception as e:
                        self.logger.warning(f"Error attaching file {file_path}: {e}")
            
            # Send email
            recipients = [to]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            self.smtp_client.send_message(msg)
            self.logger.info(f"Email sent successfully to {to}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return False
    
    def send_bulk_email(self, recipients: List[str], subject: str, body: str, 
                       from_email: str = None, delay: int = 1) -> Dict[str, Any]:
        """Send email to multiple recipients with delay"""
        results = {
            'success': [],
            'failed': [],
            'total': len(recipients)
        }
        
        for recipient in recipients:
            try:
                success = self.send_email(recipient, subject, body, from_email)
                
                if success:
                    results['success'].append(recipient)
                else:
                    results['failed'].append(recipient)
                
                # Delay between emails to avoid spam filters
                if delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"Error sending email to {recipient}: {e}")
                results['failed'].append(recipient)
        
        self.logger.info(f"Bulk email completed: {len(results['success'])}/{len(recipients)} sent successfully")
        return results
    
    def schedule_email(self, to: str, subject: str, body: str, send_time: datetime,
                      from_email: str = None, **kwargs) -> bool:
        """Schedule an email to be sent at a specific time"""
        try:
            email_data = {
                'to': to,
                'subject': subject,
                'body': body,
                'from_email': from_email or self.email_config.get('from_email', ''),
                'send_time': send_time,
                'kwargs': kwargs
            }
            
            self.scheduled_emails.append(email_data)
            
            # Schedule the email
            schedule_time = send_time.strftime("%H:%M")
            schedule.every().day.at(schedule_time).do(
                self._send_scheduled_email, email_data
            )
            
            self.logger.info(f"Email scheduled for {send_time}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error scheduling email: {e}")
            return False
    
    def _send_scheduled_email(self, email_data: Dict[str, Any]):
        """Send a scheduled email"""
        try:
            success = self.send_email(
                email_data['to'],
                email_data['subject'],
                email_data['body'],
                email_data['from_email'],
                **email_data['kwargs']
            )
            
            if success:
                self.scheduled_emails.remove(email_data)
                self.logger.info(f"Scheduled email sent successfully to {email_data['to']}")
            else:
                self.logger.error(f"Failed to send scheduled email to {email_data['to']}")
                
        except Exception as e:
            self.logger.error(f"Error sending scheduled email: {e}")
    
    def setup_auto_reply(self, rule: Dict[str, Any]):
        """Setup auto-reply rule"""
        try:
            self.auto_reply_rules.append(rule)
            self.logger.info(f"Auto-reply rule added: {rule.get('name', 'Unnamed')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up auto-reply rule: {e}")
            return False
    
    def check_and_auto_reply(self) -> int:
        """Check for new emails and send auto-replies"""
        try:
            if not self.imap_client:
                if not self._setup_imap_from_config():
                    return 0
            
            # Select inbox
            self.imap_client.select('INBOX')
            
            # Search for unread emails
            status, messages = self.imap_client.search(None, 'UNSEEN')
            
            if status != 'OK':
                return 0
            
            email_ids = messages[0].split()
            replied_count = 0
            
            for email_id in email_ids:
                try:
                    # Fetch email
                    status, msg_data = self.imap_client.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    email_message = email.message_from_bytes(msg_data[0][1])
                    
                    # Check auto-reply rules
                    for rule in self.auto_reply_rules:
                        if self._should_auto_reply(email_message, rule):
                            self._send_auto_reply(email_message, rule)
                            replied_count += 1
                            break
                            
                except Exception as e:
                    self.logger.warning(f"Error processing email {email_id}: {e}")
                    continue
            
            if replied_count > 0:
                self.logger.info(f"Sent {replied_count} auto-replies")
            
            return replied_count
            
        except Exception as e:
            self.logger.error(f"Error checking and auto-replying: {e}")
            return 0
    
    def _should_auto_reply(self, email_message, rule: Dict[str, Any]) -> bool:
        """Check if an email should trigger an auto-reply"""
        try:
            # Check sender
            sender = email_message.get('From', '')
            if 'sender_contains' in rule:
                if rule['sender_contains'].lower() not in sender.lower():
                    return False
            
            # Check subject
            subject = email_message.get('Subject', '')
            if 'subject_contains' in rule:
                if rule['subject_contains'].lower() not in subject.lower():
                    return False
            
            # Check body content
            body = self._get_email_body(email_message)
            if 'body_contains' in rule:
                if rule['body_contains'].lower() not in body.lower():
                    return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error checking auto-reply rule: {e}")
            return False
    
    def _send_auto_reply(self, original_email, rule: Dict[str, Any]):
        """Send an auto-reply email"""
        try:
            sender = original_email.get('From', '')
            subject = original_email.get('Subject', '')
            
            # Create auto-reply subject
            auto_reply_subject = f"Re: {subject}"
            if not auto_reply_subject.startswith("Re: "):
                auto_reply_subject = f"Re: {auto_reply_subject}"
            
            # Send auto-reply
            success = self.send_email(
                sender,
                auto_reply_subject,
                rule['reply_message'],
                self.email_config.get('from_email', '')
            )
            
            if success:
                self.logger.info(f"Auto-reply sent to {sender}")
            
        except Exception as e:
            self.logger.error(f"Error sending auto-reply: {e}")
    
    def _get_email_body(self, email_message) -> str:
        """Extract text body from email message"""
        try:
            body = ""
            
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = email_message.get_payload(decode=True).decode()
            
            return body
            
        except Exception as e:
            self.logger.warning(f"Error extracting email body: {e}")
            return ""
    
    def get_recent_emails(self, limit: int = 10, folder: str = 'INBOX') -> List[Dict[str, Any]]:
        """Get recent emails from a folder"""
        try:
            if not self.imap_client:
                if not self._setup_imap_from_config():
                    return []
            
            # Select folder
            self.imap_client.select(folder)
            
            # Search for recent emails
            status, messages = self.imap_client.search(None, 'ALL')
            
            if status != 'OK':
                return []
            
            email_ids = messages[0].split()
            recent_emails = []
            
            # Get the most recent emails
            for email_id in email_ids[-limit:]:
                try:
                    status, msg_data = self.imap_client.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    email_message = email.message_from_bytes(msg_data[0][1])
                    
                    email_data = {
                        'id': email_id.decode(),
                        'from': email_message.get('From', ''),
                        'to': email_message.get('To', ''),
                        'subject': email_message.get('Subject', ''),
                        'date': email_message.get('Date', ''),
                        'body': self._get_email_body(email_message)[:500] + '...' if len(self._get_email_body(email_message)) > 500 else self._get_email_body(email_message)
                    }
                    
                    recent_emails.append(email_data)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing email {email_id}: {e}")
                    continue
            
            return recent_emails
            
        except Exception as e:
            self.logger.error(f"Error getting recent emails: {e}")
            return []
    
    def create_email_template(self, template_name: str, subject: str, body: str, 
                            variables: List[str] = None) -> bool:
        """Create an email template"""
        try:
            template = {
                'name': template_name,
                'subject': subject,
                'body': body,
                'variables': variables or [],
                'created_at': datetime.now().isoformat()
            }
            
            # Save template to config
            templates = self.config.get('email_templates', {})
            templates[template_name] = template
            self.config['email_templates'] = templates
            self.config_manager.save_config(self.config)
            
            self.logger.info(f"Email template created: {template_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating email template: {e}")
            return False
    
    def send_template_email(self, template_name: str, to: str, variables: Dict[str, str] = None) -> bool:
        """Send email using a template"""
        try:
            templates = self.config.get('email_templates', {})
            
            if template_name not in templates:
                self.logger.error(f"Template not found: {template_name}")
                return False
            
            template = templates[template_name]
            subject = template['subject']
            body = template['body']
            
            # Replace variables in subject and body
            if variables:
                for key, value in variables.items():
                    subject = subject.replace(f'{{{key}}}', value)
                    body = body.replace(f'{{{key}}}', value)
            
            return self.send_email(to, subject, body)
            
        except Exception as e:
            self.logger.error(f"Error sending template email: {e}")
            return False
    
    def _setup_from_config(self) -> bool:
        """Setup SMTP from configuration"""
        try:
            smtp_config = self.email_config.get('smtp', {})
            
            if not all(key in smtp_config for key in ['server', 'port', 'username', 'password']):
                self.logger.error("SMTP configuration incomplete")
                return False
            
            return self.setup_smtp(
                smtp_config['server'],
                smtp_config['port'],
                smtp_config['username'],
                smtp_config['password'],
                smtp_config.get('use_tls', True)
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up SMTP from config: {e}")
            return False
    
    def _setup_imap_from_config(self) -> bool:
        """Setup IMAP from configuration"""
        try:
            imap_config = self.email_config.get('imap', {})
            
            if not all(key in imap_config for key in ['server', 'port', 'username', 'password']):
                self.logger.error("IMAP configuration incomplete")
                return False
            
            return self.setup_imap(
                imap_config['server'],
                imap_config['port'],
                imap_config['username'],
                imap_config['password'],
                imap_config.get('use_ssl', True)
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up IMAP from config: {e}")
            return False
    
    def start_email_monitoring(self, interval: int = 300):
        """Start monitoring emails for auto-replies"""
        def monitor_emails():
            while True:
                try:
                    self.check_and_auto_reply()
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Error in email monitoring: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=monitor_emails, daemon=True)
        thread.start()
        self.logger.info(f"Started email monitoring with {interval}s interval")
    
    def close_connections(self):
        """Close email connections"""
        try:
            if self.smtp_client:
                self.smtp_client.quit()
                self.smtp_client = None
            
            if self.imap_client:
                self.imap_client.close()
                self.imap_client.logout()
                self.imap_client = None
            
            self.logger.info("Email connections closed")
            
        except Exception as e:
            self.logger.error(f"Error closing email connections: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close_connections()
