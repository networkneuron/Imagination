"""
Social Media Automation Module

Handles Facebook, Instagram, LinkedIn, and other social media automation.
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import schedule
import threading

class SocialMediaAutomation:
    """Handles social media automation tasks"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.config = self.config_manager.load_config()
        self.social_config = self.config.get('social_media', {})
        self.driver = None
        self.auto_reply_rules = []
        self.scheduled_posts = []
        
    def setup_driver(self, headless: bool = False) -> bool:
        """Setup Selenium WebDriver for social media automation"""
        try:
            options = Options()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--user-data-dir=./social_media_data")  # Persist login
            
            self.driver = webdriver.Chrome(options=options)
            self.logger.info("Social media WebDriver setup successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up WebDriver: {e}")
            return False
    
    def facebook_login(self, email: str, password: str) -> bool:
        """Login to Facebook"""
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False
            
            self.driver.get("https://www.facebook.com")
            
            # Wait for login form
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            
            # Enter credentials
            email_field.send_keys(email)
            password_field = self.driver.find_element(By.ID, "pass")
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='search']"))
            )
            
            self.logger.info("Facebook login successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging into Facebook: {e}")
            return False
    
    def facebook_post(self, content: str, image_path: str = None) -> bool:
        """Post content to Facebook"""
        try:
            if not self.driver:
                return False
            
            # Go to Facebook home
            self.driver.get("https://www.facebook.com")
            time.sleep(3)
            
            # Find post composer
            post_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='status-attachment-mentions-input']"))
            )
            
            # Type content
            post_box.click()
            post_box.send_keys(content)
            
            # Add image if provided
            if image_path:
                photo_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='media-attachment-photo']")
                photo_button.click()
                
                # Upload image
                file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                file_input.send_keys(image_path)
                
                # Wait for image to upload
                time.sleep(3)
            
            # Post the content
            post_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='react-composer-post-button']")
            post_button.click()
            
            self.logger.info("Facebook post published")
            return True
            
        except Exception as e:
            self.logger.error(f"Error posting to Facebook: {e}")
            return False
    
    def instagram_login(self, username: str, password: str) -> bool:
        """Login to Instagram"""
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False
            
            self.driver.get("https://www.instagram.com")
            time.sleep(3)
            
            # Enter credentials
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(username)
            
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='new-post-button']"))
            )
            
            self.logger.info("Instagram login successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging into Instagram: {e}")
            return False
    
    def instagram_post(self, caption: str, image_path: str) -> bool:
        """Post image to Instagram"""
        try:
            if not self.driver:
                return False
            
            # Click new post button
            new_post_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='new-post-button']"))
            )
            new_post_button.click()
            
            # Upload image
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            file_input.send_keys(image_path)
            
            # Wait for image to load
            time.sleep(3)
            
            # Click next
            next_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='button']")
            next_button.click()
            
            # Add caption
            caption_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[aria-label='Write a caption...']"))
            )
            caption_field.send_keys(caption)
            
            # Share post
            share_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='button']")
            share_button.click()
            
            self.logger.info("Instagram post published")
            return True
            
        except Exception as e:
            self.logger.error(f"Error posting to Instagram: {e}")
            return False
    
    def linkedin_login(self, email: str, password: str) -> bool:
        """Login to LinkedIn"""
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False
            
            self.driver.get("https://www.linkedin.com/login")
            
            # Enter credentials
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(email)
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='post-share-button']"))
            )
            
            self.logger.info("LinkedIn login successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging into LinkedIn: {e}")
            return False
    
    def linkedin_post(self, content: str, image_path: str = None) -> bool:
        """Post content to LinkedIn"""
        try:
            if not self.driver:
                return False
            
            # Go to LinkedIn home
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Click start a post
            start_post_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='post-share-button']"))
            )
            start_post_button.click()
            
            # Type content
            post_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='post-share-text']"))
            )
            post_box.send_keys(content)
            
            # Add image if provided
            if image_path:
                photo_button = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='post-share-image']")
                photo_button.click()
                
                # Upload image
                file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                file_input.send_keys(image_path)
                
                # Wait for image to upload
                time.sleep(3)
            
            # Post the content
            post_button = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='post-share-submit']")
            post_button.click()
            
            self.logger.info("LinkedIn post published")
            return True
            
        except Exception as e:
            self.logger.error(f"Error posting to LinkedIn: {e}")
            return False
    
    def schedule_post(self, platform: str, content: str, post_time: datetime, 
                     image_path: str = None) -> bool:
        """Schedule a post for specific time"""
        try:
            post_data = {
                'platform': platform,
                'content': content,
                'image_path': image_path,
                'post_time': post_time,
                'scheduled_at': datetime.now()
            }
            
            self.scheduled_posts.append(post_data)
            
            # Schedule the post
            schedule_time = post_time.strftime("%H:%M")
            schedule.every().day.at(schedule_time).do(
                self._publish_scheduled_post, post_data
            )
            
            self.logger.info(f"Post scheduled for {platform} at {post_time}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error scheduling post: {e}")
            return False
    
    def _publish_scheduled_post(self, post_data: Dict[str, Any]):
        """Publish a scheduled post"""
        try:
            platform = post_data['platform']
            content = post_data['content']
            image_path = post_data.get('image_path')
            
            success = False
            
            if platform.lower() == 'facebook':
                success = self.facebook_post(content, image_path)
            elif platform.lower() == 'instagram':
                if image_path:
                    success = self.instagram_post(content, image_path)
                else:
                    self.logger.error("Instagram posts require an image")
            elif platform.lower() == 'linkedin':
                success = self.linkedin_post(content, image_path)
            
            if success:
                self.scheduled_posts.remove(post_data)
                self.logger.info(f"Scheduled post published on {platform}")
            else:
                self.logger.error(f"Failed to publish scheduled post on {platform}")
                
        except Exception as e:
            self.logger.error(f"Error publishing scheduled post: {e}")
    
    def setup_auto_reply(self, platform: str, rule: Dict[str, Any]):
        """Setup auto-reply rule for social media"""
        try:
            rule['platform'] = platform
            self.auto_reply_rules.append(rule)
            self.logger.info(f"Auto-reply rule added for {platform}: {rule.get('name', 'Unnamed')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up auto-reply rule: {e}")
            return False
    
    def check_and_auto_reply(self, platform: str) -> int:
        """Check for new messages and send auto-replies"""
        try:
            if not self.driver:
                return 0
            
            replied_count = 0
            
            if platform.lower() == 'facebook':
                replied_count = self._check_facebook_messages()
            elif platform.lower() == 'instagram':
                replied_count = self._check_instagram_messages()
            elif platform.lower() == 'linkedin':
                replied_count = self._check_linkedin_messages()
            
            if replied_count > 0:
                self.logger.info(f"Sent {replied_count} auto-replies on {platform}")
            
            return replied_count
            
        except Exception as e:
            self.logger.error(f"Error checking and auto-replying on {platform}: {e}")
            return 0
    
    def _check_facebook_messages(self) -> int:
        """Check Facebook messages for auto-replies"""
        try:
            # Navigate to messages
            self.driver.get("https://www.facebook.com/messages")
            time.sleep(3)
            
            # Look for unread messages
            unread_chats = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='unread-message']")
            
            replied_count = 0
            
            for chat in unread_chats:
                try:
                    chat.click()
                    time.sleep(2)
                    
                    # Get last message
                    messages = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='message-text']")
                    
                    if messages:
                        last_message = messages[-1].text
                        
                        # Check auto-reply rules
                        for rule in self.auto_reply_rules:
                            if rule.get('platform') == 'facebook' and self._should_auto_reply(last_message, rule):
                                self._send_facebook_auto_reply(rule)
                                replied_count += 1
                                break
                                
                except Exception as e:
                    self.logger.warning(f"Error processing Facebook chat: {e}")
                    continue
            
            return replied_count
            
        except Exception as e:
            self.logger.error(f"Error checking Facebook messages: {e}")
            return 0
    
    def _check_instagram_messages(self) -> int:
        """Check Instagram messages for auto-replies"""
        try:
            # Navigate to messages
            self.driver.get("https://www.instagram.com/direct/inbox/")
            time.sleep(3)
            
            # Look for unread messages
            unread_chats = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='unread-message']")
            
            replied_count = 0
            
            for chat in unread_chats:
                try:
                    chat.click()
                    time.sleep(2)
                    
                    # Get last message
                    messages = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='message-text']")
                    
                    if messages:
                        last_message = messages[-1].text
                        
                        # Check auto-reply rules
                        for rule in self.auto_reply_rules:
                            if rule.get('platform') == 'instagram' and self._should_auto_reply(last_message, rule):
                                self._send_instagram_auto_reply(rule)
                                replied_count += 1
                                break
                                
                except Exception as e:
                    self.logger.warning(f"Error processing Instagram chat: {e}")
                    continue
            
            return replied_count
            
        except Exception as e:
            self.logger.error(f"Error checking Instagram messages: {e}")
            return 0
    
    def _check_linkedin_messages(self) -> int:
        """Check LinkedIn messages for auto-replies"""
        try:
            # Navigate to messages
            self.driver.get("https://www.linkedin.com/messaging/")
            time.sleep(3)
            
            # Look for unread messages
            unread_chats = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='unread-message']")
            
            replied_count = 0
            
            for chat in unread_chats:
                try:
                    chat.click()
                    time.sleep(2)
                    
                    # Get last message
                    messages = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='message-text']")
                    
                    if messages:
                        last_message = messages[-1].text
                        
                        # Check auto-reply rules
                        for rule in self.auto_reply_rules:
                            if rule.get('platform') == 'linkedin' and self._should_auto_reply(last_message, rule):
                                self._send_linkedin_auto_reply(rule)
                                replied_count += 1
                                break
                                
                except Exception as e:
                    self.logger.warning(f"Error processing LinkedIn chat: {e}")
                    continue
            
            return replied_count
            
        except Exception as e:
            self.logger.error(f"Error checking LinkedIn messages: {e}")
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
    
    def _send_facebook_auto_reply(self, rule: Dict[str, Any]):
        """Send Facebook auto-reply"""
        try:
            # Find message input
            message_input = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='message-compose-input']")
            message_input.send_keys(rule['reply_message'])
            
            # Send message
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='message-compose-send']")
            send_button.click()
            
            self.logger.info("Facebook auto-reply sent")
            
        except Exception as e:
            self.logger.error(f"Error sending Facebook auto-reply: {e}")
    
    def _send_instagram_auto_reply(self, rule: Dict[str, Any]):
        """Send Instagram auto-reply"""
        try:
            # Find message input
            message_input = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='message-compose-input']")
            message_input.send_keys(rule['reply_message'])
            
            # Send message
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='message-compose-send']")
            send_button.click()
            
            self.logger.info("Instagram auto-reply sent")
            
        except Exception as e:
            self.logger.error(f"Error sending Instagram auto-reply: {e}")
    
    def _send_linkedin_auto_reply(self, rule: Dict[str, Any]):
        """Send LinkedIn auto-reply"""
        try:
            # Find message input
            message_input = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='message-compose-input']")
            message_input.send_keys(rule['reply_message'])
            
            # Send message
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='message-compose-send']")
            send_button.click()
            
            self.logger.info("LinkedIn auto-reply sent")
            
        except Exception as e:
            self.logger.error(f"Error sending LinkedIn auto-reply: {e}")
    
    def start_social_media_monitoring(self, platforms: List[str], interval: int = 300):
        """Start monitoring social media for auto-replies"""
        def monitor_social_media():
            while True:
                try:
                    for platform in platforms:
                        self.check_and_auto_reply(platform)
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Error in social media monitoring: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=monitor_social_media, daemon=True)
        thread.start()
        self.logger.info(f"Started social media monitoring for {platforms} with {interval}s interval")
    
    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("Social media WebDriver closed")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close_driver()
