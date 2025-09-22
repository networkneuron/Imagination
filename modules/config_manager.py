"""
Configuration Management Module

Handles loading, saving, and managing configuration files for the automation agent.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

class ConfigManager:
    """Manages configuration files and settings"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        self.config = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.logger.info("Configuration file not found, creating default configuration")
                self.config = self._create_default_config()
                self.save_config(self.config)
            
            return self.config
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.config = self._create_default_config()
            return self.config
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """Save configuration to file"""
        try:
            if config is None:
                config = self.config
            
            # Create backup of existing config
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.backup"
                with open(self.config_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
            
            # Save new config
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            
            self.config = config
            self.logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting configuration value for key '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value by key"""
        try:
            keys = key.split('.')
            config = self.config
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the value
            config[keys[-1]] = value
            
            self.logger.info(f"Configuration value set: {key} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting configuration value for key '{key}': {e}")
            return False
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """Update multiple configuration values"""
        try:
            for key, value in updates.items():
                self.set(key, value)
            
            self.logger.info(f"Updated {len(updates)} configuration values")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a configuration value by key"""
        try:
            keys = key.split('.')
            config = self.config
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if isinstance(config, dict) and k in config:
                    config = config[k]
                else:
                    return False
            
            # Delete the value
            if isinstance(config, dict) and keys[-1] in config:
                del config[keys[-1]]
                self.logger.info(f"Configuration value deleted: {key}")
                return True
            else:
                self.logger.warning(f"Configuration key not found: {key}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting configuration value for key '{key}': {e}")
            return False
    
    def reset_to_default(self) -> bool:
        """Reset configuration to default values"""
        try:
            self.config = self._create_default_config()
            self.save_config()
            self.logger.info("Configuration reset to default values")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resetting configuration: {e}")
            return False
    
    def export_config(self, filename: str = None) -> bool:
        """Export configuration to a file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"config_export_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2, default=str)
            
            self.logger.info(f"Configuration exported to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            return False
    
    def import_config(self, filename: str) -> bool:
        """Import configuration from a file"""
        try:
            if not os.path.exists(filename):
                self.logger.error(f"Configuration file not found: {filename}")
                return False
            
            with open(filename, 'r') as f:
                imported_config = json.load(f)
            
            # Merge with existing config
            self.config.update(imported_config)
            self.save_config()
            
            self.logger.info(f"Configuration imported from {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return validation results"""
        try:
            validation_results = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Check required sections
            required_sections = ['email', 'whatsapp', 'telegram', 'social_media', 'ai']
            
            for section in required_sections:
                if section not in self.config:
                    validation_results['warnings'].append(f"Missing section: {section}")
            
            # Validate email configuration
            if 'email' in self.config:
                email_config = self.config['email']
                if email_config.get('enabled', False):
                    required_email_fields = ['smtp', 'imap']
                    for field in required_email_fields:
                        if field not in email_config:
                            validation_results['errors'].append(f"Missing email.{field} configuration")
            
            # Validate WhatsApp configuration
            if 'whatsapp' in self.config:
                whatsapp_config = self.config['whatsapp']
                if whatsapp_config.get('enabled', False):
                    # WhatsApp doesn't require specific configuration for basic functionality
                    pass
            
            # Validate Telegram configuration
            if 'telegram' in self.config:
                telegram_config = self.config['telegram']
                if telegram_config.get('enabled', False):
                    if 'bot_token' not in telegram_config:
                        validation_results['errors'].append("Missing telegram.bot_token")
            
            # Validate AI configuration
            if 'ai' in self.config:
                ai_config = self.config['ai']
                if ai_config.get('openai', {}).get('enabled', False):
                    if 'api_key' not in ai_config['openai']:
                        validation_results['errors'].append("Missing ai.openai.api_key")
                
                if ai_config.get('anthropic', {}).get('enabled', False):
                    if 'api_key' not in ai_config['anthropic']:
                        validation_results['errors'].append("Missing ai.anthropic.api_key")
            
            # Check for invalid values
            if 'logging' in self.config:
                log_level = self.config['logging'].get('level', 'INFO')
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if log_level not in valid_levels:
                    validation_results['errors'].append(f"Invalid logging level: {log_level}")
            
            validation_results['valid'] = len(validation_results['errors']) == 0
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error validating configuration: {e}")
            return {'valid': False, 'errors': [str(e)], 'warnings': []}
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            
            "logging": {
                "level": "INFO",
                "file": "automation_agent.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            
            "email": {
                "enabled": False,
                "from_email": "",
                "smtp": {
                    "server": "",
                    "port": 587,
                    "username": "",
                    "password": "",
                    "use_tls": True
                },
                "imap": {
                    "server": "",
                    "port": 993,
                    "username": "",
                    "password": "",
                    "use_ssl": True
                },
                "recipients": [],
                "templates": {}
            },
            
            "whatsapp": {
                "enabled": False,
                "templates": {}
            },
            
            "telegram": {
                "enabled": False,
                "bot_token": "",
                "templates": {}
            },
            
            "social_media": {
                "enabled": False,
                "facebook": {
                    "email": "",
                    "password": ""
                },
                "instagram": {
                    "username": "",
                    "password": ""
                },
                "linkedin": {
                    "email": "",
                    "password": ""
                }
            },
            
            "ai": {
                "openai": {
                    "enabled": False,
                    "api_key": "",
                    "model": "gpt-3.5-turbo"
                },
                "anthropic": {
                    "enabled": False,
                    "api_key": "",
                    "model": "claude-3-sonnet-20240229"
                }
            },
            
            "voice_commands": {
                "enabled": True,
                "continuous_listening": True,
                "timeout": 5,
                "phrase_time_limit": 5
            },
            
            "safety": {
                "confirm_dangerous_actions": True,
                "max_file_size": "100MB",
                "allowed_file_types": [".txt", ".pdf", ".doc", ".docx", ".jpg", ".png", ".gif"],
                "blocked_commands": ["rm -rf /", "format", "del /s /q C:\\"]
            },
            
            "automation": {
                "enabled": True,
                "check_interval": 300,
                "max_concurrent_tasks": 5,
                "task_timeout": 3600
            },
            
            "notifications": {
                "enabled": True,
                "email_alerts": True,
                "desktop_notifications": True,
                "sound_alerts": False
            }
        }
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get configuration information and statistics"""
        try:
            return {
                "config_file": self.config_file,
                "file_exists": os.path.exists(self.config_file),
                "file_size": os.path.getsize(self.config_file) if os.path.exists(self.config_file) else 0,
                "last_modified": datetime.fromtimestamp(os.path.getmtime(self.config_file)).isoformat() if os.path.exists(self.config_file) else None,
                "version": self.config.get("version", "unknown"),
                "created_at": self.config.get("created_at", "unknown"),
                "updated_at": self.config.get("updated_at", "unknown"),
                "sections": list(self.config.keys()),
                "validation": self.validate_config()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting configuration info: {e}")
            return {}
    
    def create_config_template(self, filename: str = "config_template.json") -> bool:
        """Create a configuration template file"""
        try:
            template_config = self._create_default_config()
            
            # Remove sensitive information
            template_config["email"]["smtp"]["username"] = "your_email@example.com"
            template_config["email"]["smtp"]["password"] = "your_password"
            template_config["email"]["imap"]["username"] = "your_email@example.com"
            template_config["email"]["imap"]["password"] = "your_password"
            template_config["telegram"]["bot_token"] = "your_bot_token"
            template_config["ai"]["openai"]["api_key"] = "your_openai_api_key"
            template_config["ai"]["anthropic"]["api_key"] = "your_anthropic_api_key"
            template_config["social_media"]["facebook"]["email"] = "your_facebook_email"
            template_config["social_media"]["facebook"]["password"] = "your_facebook_password"
            template_config["social_media"]["instagram"]["username"] = "your_instagram_username"
            template_config["social_media"]["instagram"]["password"] = "your_instagram_password"
            template_config["social_media"]["linkedin"]["email"] = "your_linkedin_email"
            template_config["social_media"]["linkedin"]["password"] = "your_linkedin_password"
            
            with open(filename, 'w') as f:
                json.dump(template_config, f, indent=2, default=str)
            
            self.logger.info(f"Configuration template created: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating configuration template: {e}")
            return False
