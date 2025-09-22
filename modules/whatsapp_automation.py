"""
WhatsApp Automation Module

Handles WhatsApp messaging, auto-replies, and bulk messaging.
"""

import logging
import time
import json
import pywhatkit
import pyautogui
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import schedule
import threading

class WhatsAppAutomation:
    """Handles WhatsApp automation tasks"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.config = self.config_manager.load_config()
        self.whatsapp_config = self.config.get('whatsapp', {})
        self.driver = None
        self.auto_reply_rules = []
        self.scheduled_messages = []
        
    def setup_web_whatsapp(self, headless: bool = False) -> bool:
        """Setup WhatsApp Web automation"""
        try:
            options = Options()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--user-data-dir=./whatsapp_data")  # Persist login
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.get("https://web.whatsapp.com")
            
            # Wait for QR code scan
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='chat-list']"))
            )
            
            self.logger.info("WhatsApp Web setup successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up WhatsApp Web: {e}")
            return False
    
    def send_message(self, phone_number: str, message: str, hour: int = None, minute: int = None) -> bool:
        """Send a WhatsApp message"""
        try:
            if hour is not None and minute is not None:
                # Schedule message for specific time
                return self.schedule_message(phone_number, message, hour, minute)
            
            if self.driver:
                return self._send_message_web(phone_number, message)
            else:
                return self._send_message_pywhatkit(phone_number, message)
                
        except Exception as e:
            self.logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    def _send_message_web(self, phone_number: str, message: str) -> bool:
        """Send message using WhatsApp Web"""
        try:
            # Format phone number
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
            
            # Open chat
            chat_url = f"https://web.whatsapp.com/send?phone={phone_number.replace('+', '')}"
            self.driver.get(chat_url)
            
            # Wait for chat to load
            time.sleep(5)
            
            # Find message input box
            message_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='conversation-compose-box-input']"))
            )
            
            # Type message
            message_box.send_keys(message)
            
            # Send message
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='send']")
            send_button.click()
            
            self.logger.info(f"Message sent to {phone_number}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message via WhatsApp Web: {e}")
            return False
    
    def _send_message_pywhatkit(self, phone_number: str, message: str) -> bool:
        """Send message using pywhatkit"""
        try:
            # Format phone number
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
            
            # Get current time
            now = datetime.now()
            hour = now.hour
            minute = now.minute + 1  # Send in 1 minute
            
            # Send message
            pywhatkit.sendwhatmsg(phone_number, message, hour, minute)
            
            self.logger.info(f"Message scheduled to {phone_number} at {hour}:{minute:02d}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message via pywhatkit: {e}")
            return False
    
    def send_bulk_message(self, phone_numbers: List[str], message: str, delay: int = 5) -> Dict[str, Any]:
        """Send message to multiple phone numbers"""
        results = {
            'success': [],
            'failed': [],
            'total': len(phone_numbers)
        }
        
        for phone_number in phone_numbers:
            try:
                success = self.send_message(phone_number, message)
                
                if success:
                    results['success'].append(phone_number)
                else:
                    results['failed'].append(phone_number)
                
                # Delay between messages
                if delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"Error sending message to {phone_number}: {e}")
                results['failed'].append(phone_number)
        
        self.logger.info(f"Bulk messaging completed: {len(results['success'])}/{len(phone_numbers)} sent successfully")
        return results
    
    def schedule_message(self, phone_number: str, message: str, hour: int, minute: int) -> bool:
        """Schedule a message for specific time"""
        try:
            message_data = {
                'phone_number': phone_number,
                'message': message,
                'hour': hour,
                'minute': minute,
                'scheduled_at': datetime.now()
            }
            
            self.scheduled_messages.append(message_data)
            
            # Schedule the message
            schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(
                self._send_scheduled_message, message_data
            )
            
            self.logger.info(f"Message scheduled for {phone_number} at {hour:02d}:{minute:02d}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error scheduling message: {e}")
            return False
    
    def _send_scheduled_message(self, message_data: Dict[str, Any]):
        """Send a scheduled message"""
        try:
            success = self.send_message(
                message_data['phone_number'],
                message_data['message']
            )
            
            if success:
                self.scheduled_messages.remove(message_data)
                self.logger.info(f"Scheduled message sent to {message_data['phone_number']}")
            else:
                self.logger.error(f"Failed to send scheduled message to {message_data['phone_number']}")
                
        except Exception as e:
            self.logger.error(f"Error sending scheduled message: {e}")
    
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
        """Check for new messages and send auto-replies"""
        try:
            if not self.driver:
                self.logger.warning("WhatsApp Web not initialized")
                return 0
            
            # Look for unread messages
            unread_chats = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='unread-count']")
            
            replied_count = 0
            
            for chat in unread_chats:
                try:
                    # Click on chat
                    chat.click()
                    time.sleep(2)
                    
                    # Get last message
                    messages = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='msg-container']")
                    
                    if messages:
                        last_message = messages[-1].text
                        
                        # Check auto-reply rules
                        for rule in self.auto_reply_rules:
                            if self._should_auto_reply(last_message, rule):
                                self._send_auto_reply(rule)
                                replied_count += 1
                                break
                                
                except Exception as e:
                    self.logger.warning(f"Error processing chat: {e}")
                    continue
            
            if replied_count > 0:
                self.logger.info(f"Sent {replied_count} auto-replies")
            
            return replied_count
            
        except Exception as e:
            self.logger.error(f"Error checking and auto-replying: {e}")
            return 0
    
    def _should_auto_reply(self, message: str, rule: Dict[str, Any]) -> bool:
        """Check if a message should trigger an auto-reply"""
        try:
            # Check keywords
            if 'keywords' in rule:
                keywords = rule['keywords']
                if isinstance(keywords, list):
                    if not any(keyword.lower() in message.lower() for keyword in keywords):
                        return False
                else:
                    if keywords.lower() not in message.lower():
                        return False
            
            # Check sender
            if 'sender_contains' in rule:
                # This would need to be implemented based on how you identify senders
                pass
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error checking auto-reply rule: {e}")
            return False
    
    def _send_auto_reply(self, rule: Dict[str, Any]):
        """Send an auto-reply message"""
        try:
            # Find message input box
            message_box = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='conversation-compose-box-input']")
            
            # Type auto-reply message
            message_box.send_keys(rule['reply_message'])
            
            # Send message
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='send']")
            send_button.click()
            
            self.logger.info("Auto-reply sent")
            
        except Exception as e:
            self.logger.error(f"Error sending auto-reply: {e}")
    
    def get_chat_list(self) -> List[Dict[str, Any]]:
        """Get list of recent chats"""
        try:
            if not self.driver:
                return []
            
            chats = []
            chat_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='chat-list'] > div")
            
            for chat_element in chat_elements:
                try:
                    # Get chat name
                    name_element = chat_element.find_element(By.CSS_SELECTOR, "[data-testid='chat-title']")
                    name = name_element.text
                    
                    # Get last message
                    last_message_element = chat_element.find_element(By.CSS_SELECTOR, "[data-testid='last-msg-lbl']")
                    last_message = last_message_element.text
                    
                    # Get timestamp
                    time_element = chat_element.find_element(By.CSS_SELECTOR, "[data-testid='msg-time']")
                    timestamp = time_element.text
                    
                    # Check if unread
                    unread_count = 0
                    try:
                        unread_element = chat_element.find_element(By.CSS_SELECTOR, "[data-testid='unread-count']")
                        unread_count = int(unread_element.text)
                    except:
                        pass
                    
                    chats.append({
                        'name': name,
                        'last_message': last_message,
                        'timestamp': timestamp,
                        'unread_count': unread_count
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Error parsing chat element: {e}")
                    continue
            
            return chats
            
        except Exception as e:
            self.logger.error(f"Error getting chat list: {e}")
            return []
    
    def send_image(self, phone_number: str, image_path: str, caption: str = "") -> bool:
        """Send an image with optional caption"""
        try:
            if not self.driver:
                return False
            
            # Format phone number
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
            
            # Open chat
            chat_url = f"https://web.whatsapp.com/send?phone={phone_number.replace('+', '')}"
            self.driver.get(chat_url)
            
            # Wait for chat to load
            time.sleep(5)
            
            # Click attachment button
            attachment_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='attach-image']")
            attachment_button.click()
            
            # Upload image
            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(image_path)
            
            # Add caption if provided
            if caption:
                caption_box = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='media-caption']")
                caption_box.send_keys(caption)
            
            # Send image
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='send']")
            send_button.click()
            
            self.logger.info(f"Image sent to {phone_number}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending image: {e}")
            return False
    
    def send_document(self, phone_number: str, document_path: str, caption: str = "") -> bool:
        """Send a document with optional caption"""
        try:
            if not self.driver:
                return False
            
            # Format phone number
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
            
            # Open chat
            chat_url = f"https://web.whatsapp.com/send?phone={phone_number.replace('+', '')}"
            self.driver.get(chat_url)
            
            # Wait for chat to load
            time.sleep(5)
            
            # Click attachment button
            attachment_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='attach-document']")
            attachment_button.click()
            
            # Upload document
            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(document_path)
            
            # Add caption if provided
            if caption:
                caption_box = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='media-caption']")
                caption_box.send_keys(caption)
            
            # Send document
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='send']")
            send_button.click()
            
            self.logger.info(f"Document sent to {phone_number}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending document: {e}")
            return False
    
    def start_message_monitoring(self, interval: int = 30):
        """Start monitoring messages for auto-replies"""
        def monitor_messages():
            while True:
                try:
                    self.check_and_auto_reply()
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Error in message monitoring: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=monitor_messages, daemon=True)
        thread.start()
        self.logger.info(f"Started message monitoring with {interval}s interval")
    
    def create_message_template(self, template_name: str, message: str, variables: List[str] = None) -> bool:
        """Create a message template"""
        try:
            template = {
                'name': template_name,
                'message': message,
                'variables': variables or [],
                'created_at': datetime.now().isoformat()
            }
            
            # Save template to config
            templates = self.config.get('whatsapp_templates', {})
            templates[template_name] = template
            self.config['whatsapp_templates'] = templates
            self.config_manager.save_config(self.config)
            
            self.logger.info(f"Message template created: {template_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating message template: {e}")
            return False
    
    def send_template_message(self, template_name: str, phone_number: str, variables: Dict[str, str] = None) -> bool:
        """Send message using a template"""
        try:
            templates = self.config.get('whatsapp_templates', {})
            
            if template_name not in templates:
                self.logger.error(f"Template not found: {template_name}")
                return False
            
            template = templates[template_name]
            message = template['message']
            
            # Replace variables in message
            if variables:
                for key, value in variables.items():
                    message = message.replace(f'{{{key}}}', value)
            
            return self.send_message(phone_number, message)
            
        except Exception as e:
            self.logger.error(f"Error sending template message: {e}")
            return False
    
    def close_whatsapp(self):
        """Close WhatsApp Web"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("WhatsApp Web closed")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close_whatsapp()
