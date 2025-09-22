"""
Telegram Automation Module

Handles Telegram messaging, bot integration, and automated responses.
"""

import logging
import requests
import json
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import schedule
import threading

class TelegramAutomation:
    """Handles Telegram automation tasks"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.config = self.config_manager.load_config()
        self.telegram_config = self.config.get('telegram', {})
        self.bot_token = self.telegram_config.get('bot_token', '')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.auto_reply_rules = []
        self.scheduled_messages = []
        
    def setup_bot(self, bot_token: str) -> bool:
        """Setup Telegram bot with token"""
        try:
            self.bot_token = bot_token
            self.base_url = f"https://api.telegram.org/bot{bot_token}"
            
            # Test bot token
            response = requests.get(f"{self.base_url}/getMe")
            if response.status_code == 200:
                bot_info = response.json()
                self.logger.info(f"Bot setup successful: @{bot_info['result']['username']}")
                return True
            else:
                self.logger.error("Invalid bot token")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting up Telegram bot: {e}")
            return False
    
    def send_message(self, chat_id: str, message: str, parse_mode: str = "HTML") -> bool:
        """Send a message to a chat"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                self.logger.info(f"Message sent to chat {chat_id}")
                return True
            else:
                self.logger.error(f"Failed to send message: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    def send_photo(self, chat_id: str, photo_path: str, caption: str = "") -> bool:
        """Send a photo to a chat"""
        try:
            url = f"{self.base_url}/sendPhoto"
            
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': chat_id,
                    'caption': caption
                }
                
                response = requests.post(url, files=files, data=data)
                
                if response.status_code == 200:
                    self.logger.info(f"Photo sent to chat {chat_id}")
                    return True
                else:
                    self.logger.error(f"Failed to send photo: {response.text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error sending photo: {e}")
            return False
    
    def send_document(self, chat_id: str, document_path: str, caption: str = "") -> bool:
        """Send a document to a chat"""
        try:
            url = f"{self.base_url}/sendDocument"
            
            with open(document_path, 'rb') as document:
                files = {'document': document}
                data = {
                    'chat_id': chat_id,
                    'caption': caption
                }
                
                response = requests.post(url, files=files, data=data)
                
                if response.status_code == 200:
                    self.logger.info(f"Document sent to chat {chat_id}")
                    return True
                else:
                    self.logger.error(f"Failed to send document: {response.text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error sending document: {e}")
            return False
    
    def send_bulk_message(self, chat_ids: List[str], message: str, delay: int = 1) -> Dict[str, Any]:
        """Send message to multiple chats"""
        results = {
            'success': [],
            'failed': [],
            'total': len(chat_ids)
        }
        
        for chat_id in chat_ids:
            try:
                success = self.send_message(chat_id, message)
                
                if success:
                    results['success'].append(chat_id)
                else:
                    results['failed'].append(chat_id)
                
                # Delay between messages
                if delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"Error sending message to {chat_id}: {e}")
                results['failed'].append(chat_id)
        
        self.logger.info(f"Bulk messaging completed: {len(results['success'])}/{len(chat_ids)} sent successfully")
        return results
    
    def schedule_message(self, chat_id: str, message: str, send_time: datetime) -> bool:
        """Schedule a message for specific time"""
        try:
            message_data = {
                'chat_id': chat_id,
                'message': message,
                'send_time': send_time,
                'scheduled_at': datetime.now()
            }
            
            self.scheduled_messages.append(message_data)
            
            # Schedule the message
            schedule_time = send_time.strftime("%H:%M")
            schedule.every().day.at(schedule_time).do(
                self._send_scheduled_message, message_data
            )
            
            self.logger.info(f"Message scheduled for chat {chat_id} at {send_time}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error scheduling message: {e}")
            return False
    
    def _send_scheduled_message(self, message_data: Dict[str, Any]):
        """Send a scheduled message"""
        try:
            success = self.send_message(
                message_data['chat_id'],
                message_data['message']
            )
            
            if success:
                self.scheduled_messages.remove(message_data)
                self.logger.info(f"Scheduled message sent to {message_data['chat_id']}")
            else:
                self.logger.error(f"Failed to send scheduled message to {message_data['chat_id']}")
                
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
    
    def get_updates(self, offset: int = None) -> List[Dict[str, Any]]:
        """Get bot updates (messages)"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {}
            
            if offset:
                params['offset'] = offset
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('result', [])
            else:
                self.logger.error(f"Failed to get updates: {response.text}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting updates: {e}")
            return []
    
    def check_and_auto_reply(self, last_update_id: int = 0) -> int:
        """Check for new messages and send auto-replies"""
        try:
            updates = self.get_updates(offset=last_update_id + 1)
            replied_count = 0
            
            for update in updates:
                try:
                    if 'message' in update:
                        message = update['message']
                        chat_id = str(message['chat']['id'])
                        text = message.get('text', '')
                        
                        # Check auto-reply rules
                        for rule in self.auto_reply_rules:
                            if self._should_auto_reply(text, rule):
                                self._send_auto_reply(chat_id, rule)
                                replied_count += 1
                                break
                        
                        last_update_id = update['update_id']
                        
                except Exception as e:
                    self.logger.warning(f"Error processing update: {e}")
                    continue
            
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
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error checking auto-reply rule: {e}")
            return False
    
    def _send_auto_reply(self, chat_id: str, rule: Dict[str, Any]):
        """Send an auto-reply message"""
        try:
            self.send_message(chat_id, rule['reply_message'])
            self.logger.info(f"Auto-reply sent to chat {chat_id}")
            
        except Exception as e:
            self.logger.error(f"Error sending auto-reply: {e}")
    
    def create_inline_keyboard(self, buttons: List[List[Dict[str, str]]]) -> str:
        """Create inline keyboard markup"""
        try:
            keyboard = {
                'inline_keyboard': buttons
            }
            return json.dumps(keyboard)
            
        except Exception as e:
            self.logger.error(f"Error creating inline keyboard: {e}")
            return "{}"
    
    def send_message_with_keyboard(self, chat_id: str, message: str, keyboard: str) -> bool:
        """Send message with inline keyboard"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'reply_markup': keyboard
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                self.logger.info(f"Message with keyboard sent to chat {chat_id}")
                return True
            else:
                self.logger.error(f"Failed to send message with keyboard: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending message with keyboard: {e}")
            return False
    
    def start_bot_polling(self, interval: int = 1):
        """Start bot polling for updates"""
        def poll_updates():
            last_update_id = 0
            
            while True:
                try:
                    replied_count = self.check_and_auto_reply(last_update_id)
                    
                    if replied_count > 0:
                        self.logger.info(f"Processed {replied_count} auto-replies")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    self.logger.error(f"Error in bot polling: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=poll_updates, daemon=True)
        thread.start()
        self.logger.info(f"Started bot polling with {interval}s interval")
    
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
            templates = self.config.get('telegram_templates', {})
            templates[template_name] = template
            self.config['telegram_templates'] = templates
            self.config_manager.save_config(self.config)
            
            self.logger.info(f"Message template created: {template_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating message template: {e}")
            return False
    
    def send_template_message(self, template_name: str, chat_id: str, variables: Dict[str, str] = None) -> bool:
        """Send message using a template"""
        try:
            templates = self.config.get('telegram_templates', {})
            
            if template_name not in templates:
                self.logger.error(f"Template not found: {template_name}")
                return False
            
            template = templates[template_name]
            message = template['message']
            
            # Replace variables in message
            if variables:
                for key, value in variables.items():
                    message = message.replace(f'{{{key}}}', value)
            
            return self.send_message(chat_id, message)
            
        except Exception as e:
            self.logger.error(f"Error sending template message: {e}")
            return False
    
    def get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """Get information about a chat"""
        try:
            url = f"{self.base_url}/getChat"
            data = {'chat_id': chat_id}
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                return response.json()['result']
            else:
                self.logger.error(f"Failed to get chat info: {response.text}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting chat info: {e}")
            return {}
    
    def get_bot_info(self) -> Dict[str, Any]:
        """Get bot information"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()['result']
            else:
                self.logger.error(f"Failed to get bot info: {response.text}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting bot info: {e}")
            return {}
