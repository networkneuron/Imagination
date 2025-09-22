"""
Safety Management Module

Handles safety checks, confirmation prompts, and security measures for the automation agent.
"""

import logging
import os
import hashlib
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path

class SafetyManager:
    """Manages safety checks and security measures"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.safety_config = {
            'confirm_dangerous_actions': True,
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'allowed_file_types': ['.txt', '.pdf', '.doc', '.docx', '.jpg', '.png', '.gif', '.mp4', '.mp3'],
            'blocked_commands': ['rm -rf /', 'format', 'del /s /q C:\\', 'shutdown', 'reboot'],
            'max_execution_time': 3600,  # 1 hour
            'quarantine_directory': './quarantine',
            'log_all_actions': True
        }
        self.action_log = []
        self.confirmation_callbacks = []
        
        # Create quarantine directory
        self._setup_quarantine()
    
    def _setup_quarantine(self):
        """Setup quarantine directory for suspicious files"""
        try:
            quarantine_path = Path(self.safety_config['quarantine_directory'])
            quarantine_path.mkdir(exist_ok=True)
            self.logger.info(f"Quarantine directory setup: {quarantine_path}")
        except Exception as e:
            self.logger.error(f"Error setting up quarantine directory: {e}")
    
    def confirm_dangerous_action(self, action_description: str, force: bool = False) -> bool:
        """Request confirmation for potentially dangerous actions"""
        try:
            if not self.safety_config['confirm_dangerous_actions'] or force:
                return True
            
            # Log the action request
            self._log_action('CONFIRMATION_REQUEST', action_description)
            
            # Check if running in interactive mode
            if not self._is_interactive_mode():
                self.logger.warning(f"Dangerous action blocked (non-interactive): {action_description}")
                return False
            
            # Use callbacks if available
            for callback in self.confirmation_callbacks:
                try:
                    result = callback(action_description)
                    if result is not None:
                        return result
                except Exception as e:
                    self.logger.warning(f"Error in confirmation callback: {e}")
            
            # Default confirmation (in a real implementation, this would be interactive)
            self.logger.warning(f"Dangerous action requires confirmation: {action_description}")
            return False  # Default to deny for safety
            
        except Exception as e:
            self.logger.error(f"Error in confirmation process: {e}")
            return False
    
    def add_confirmation_callback(self, callback: Callable[[str], bool]):
        """Add a callback for handling confirmation requests"""
        try:
            self.confirmation_callbacks.append(callback)
            self.logger.info("Confirmation callback added")
        except Exception as e:
            self.logger.error(f"Error adding confirmation callback: {e}")
    
    def is_safe_command(self, command: str) -> Dict[str, Any]:
        """Check if a command is safe to execute"""
        try:
            safety_result = {
                'safe': True,
                'warnings': [],
                'blocked': False,
                'reason': ''
            }
            
            command_lower = command.lower()
            
            # Check against blocked commands
            for blocked_cmd in self.safety_config['blocked_commands']:
                if blocked_cmd.lower() in command_lower:
                    safety_result['safe'] = False
                    safety_result['blocked'] = True
                    safety_result['reason'] = f"Command contains blocked pattern: {blocked_cmd}"
                    break
            
            # Check for dangerous patterns
            dangerous_patterns = [
                'rm -rf', 'del /s', 'format', 'fdisk', 'dd if=',
                'shutdown', 'reboot', 'halt', 'poweroff',
                'taskkill /f', 'kill -9', 'killall'
            ]
            
            for pattern in dangerous_patterns:
                if pattern in command_lower:
                    safety_result['warnings'].append(f"Command contains dangerous pattern: {pattern}")
                    if not safety_result['blocked']:
                        safety_result['safe'] = False
            
            # Check for file system operations
            if any(op in command_lower for op in ['rm ', 'del ', 'rmdir ', 'rd ']):
                safety_result['warnings'].append("Command performs file deletion")
            
            if any(op in command_lower for op in ['chmod ', 'chown ', 'attrib ']):
                safety_result['warnings'].append("Command modifies file permissions")
            
            return safety_result
            
        except Exception as e:
            self.logger.error(f"Error checking command safety: {e}")
            return {'safe': False, 'warnings': [], 'blocked': True, 'reason': 'Error in safety check'}
    
    def is_safe_file_operation(self, file_path: str, operation: str) -> Dict[str, Any]:
        """Check if a file operation is safe"""
        try:
            safety_result = {
                'safe': True,
                'warnings': [],
                'blocked': False,
                'reason': ''
            }
            
            path = Path(file_path)
            
            # Check file size
            if path.exists() and path.is_file():
                file_size = path.stat().st_size
                if file_size > self.safety_config['max_file_size']:
                    safety_result['warnings'].append(f"File size exceeds limit: {file_size} bytes")
                    if operation in ['copy', 'move', 'upload']:
                        safety_result['safe'] = False
                        safety_result['reason'] = "File too large for operation"
            
            # Check file extension
            if path.suffix and path.suffix.lower() not in self.safety_config['allowed_file_types']:
                safety_result['warnings'].append(f"File type not in allowed list: {path.suffix}")
                if operation in ['copy', 'move', 'upload']:
                    safety_result['safe'] = False
                    safety_result['reason'] = "File type not allowed"
            
            # Check for system directories
            system_dirs = ['/system', '/windows', '/program files', '/usr', '/bin', '/sbin']
            if any(sys_dir in str(path).lower() for sys_dir in system_dirs):
                safety_result['warnings'].append("Operation on system directory")
                if operation in ['delete', 'modify']:
                    safety_result['safe'] = False
                    safety_result['reason'] = "Cannot modify system directories"
            
            return safety_result
            
        except Exception as e:
            self.logger.error(f"Error checking file operation safety: {e}")
            return {'safe': False, 'warnings': [], 'blocked': True, 'reason': 'Error in safety check'}
    
    def quarantine_file(self, file_path: str, reason: str = "Suspicious file") -> bool:
        """Move a file to quarantine"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                self.logger.warning(f"File not found for quarantine: {file_path}")
                return False
            
            # Create quarantine filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_name = f"{timestamp}_{source_path.name}"
            quarantine_path = Path(self.safety_config['quarantine_directory']) / quarantine_name
            
            # Move file to quarantine
            source_path.rename(quarantine_path)
            
            # Log the quarantine action
            self._log_action('QUARANTINE', f"Moved {file_path} to quarantine: {reason}")
            
            self.logger.info(f"File quarantined: {file_path} -> {quarantine_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error quarantining file {file_path}: {e}")
            return False
    
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Scan a file for potential threats"""
        try:
            scan_result = {
                'safe': True,
                'threats': [],
                'file_info': {},
                'scan_time': datetime.now()
            }
            
            path = Path(file_path)
            if not path.exists():
                scan_result['safe'] = False
                scan_result['threats'].append("File not found")
                return scan_result
            
            # Get file information
            stat = path.stat()
            scan_result['file_info'] = {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'extension': path.suffix,
                'name': path.name
            }
            
            # Check file size
            if stat.st_size > self.safety_config['max_file_size']:
                scan_result['threats'].append("File size exceeds safety limit")
                scan_result['safe'] = False
            
            # Check file extension
            if path.suffix and path.suffix.lower() not in self.safety_config['allowed_file_types']:
                scan_result['threats'].append(f"File type not allowed: {path.suffix}")
                scan_result['safe'] = False
            
            # Check for suspicious content (basic text file scanning)
            if path.suffix.lower() in ['.txt', '.log', '.py', '.js', '.html', '.xml']:
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(1024)  # Read first 1KB
                        
                        # Check for suspicious patterns
                        suspicious_patterns = [
                            'eval(', 'exec(', 'system(', 'shell_exec(',
                            'rm -rf', 'del /s', 'format',
                            '<script>', 'javascript:',
                            'powershell', 'cmd.exe'
                        ]
                        
                        for pattern in suspicious_patterns:
                            if pattern.lower() in content.lower():
                                scan_result['threats'].append(f"Suspicious content detected: {pattern}")
                                scan_result['safe'] = False
                                
                except Exception as e:
                    scan_result['threats'].append(f"Error reading file content: {e}")
            
            # Calculate file hash for tracking
            try:
                file_hash = self._calculate_file_hash(file_path)
                scan_result['file_info']['hash'] = file_hash
            except Exception as e:
                scan_result['threats'].append(f"Error calculating file hash: {e}")
            
            return scan_result
            
        except Exception as e:
            self.logger.error(f"Error scanning file {file_path}: {e}")
            return {
                'safe': False,
                'threats': [f"Scan error: {e}"],
                'file_info': {},
                'scan_time': datetime.now()
            }
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of a file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating file hash: {e}")
            return ""
    
    def _is_interactive_mode(self) -> bool:
        """Check if running in interactive mode"""
        try:
            # Check if stdin is a terminal
            return os.isatty(0)
        except:
            return False
    
    def _log_action(self, action_type: str, description: str, details: Dict[str, Any] = None):
        """Log an action for audit purposes"""
        try:
            if not self.safety_config['log_all_actions']:
                return
            
            action_entry = {
                'timestamp': datetime.now(),
                'action_type': action_type,
                'description': description,
                'details': details or {}
            }
            
            self.action_log.append(action_entry)
            
            # Keep only last 1000 actions to prevent memory issues
            if len(self.action_log) > 1000:
                self.action_log = self.action_log[-1000:]
            
            self.logger.info(f"Action logged: {action_type} - {description}")
            
        except Exception as e:
            self.logger.error(f"Error logging action: {e}")
    
    def get_action_log(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get action log for specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return [action for action in self.action_log if action['timestamp'] >= cutoff_time]
        except Exception as e:
            self.logger.error(f"Error getting action log: {e}")
            return []
    
    def save_action_log(self, filename: str = None) -> bool:
        """Save action log to file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"action_log_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(self.action_log, f, indent=2, default=str)
            
            self.logger.info(f"Action log saved to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving action log: {e}")
            return False
    
    def clear_action_log(self):
        """Clear action log"""
        try:
            self.action_log.clear()
            self.logger.info("Action log cleared")
        except Exception as e:
            self.logger.error(f"Error clearing action log: {e}")
    
    def update_safety_config(self, new_config: Dict[str, Any]) -> bool:
        """Update safety configuration"""
        try:
            self.safety_config.update(new_config)
            self.logger.info("Safety configuration updated")
            return True
        except Exception as e:
            self.logger.error(f"Error updating safety configuration: {e}")
            return False
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety status and statistics"""
        try:
            recent_actions = self.get_action_log(24)  # Last 24 hours
            
            return {
                'safety_config': self.safety_config,
                'total_actions_logged': len(self.action_log),
                'recent_actions_count': len(recent_actions),
                'quarantine_directory': self.safety_config['quarantine_directory'],
                'quarantine_files_count': len(list(Path(self.safety_config['quarantine_directory']).glob('*'))),
                'confirmation_callbacks_count': len(self.confirmation_callbacks),
                'interactive_mode': self._is_interactive_mode()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting safety status: {e}")
            return {}
    
    def validate_safety_config(self) -> Dict[str, Any]:
        """Validate safety configuration"""
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Check quarantine directory
            quarantine_path = Path(self.safety_config['quarantine_directory'])
            if not quarantine_path.exists():
                validation_result['warnings'].append("Quarantine directory does not exist")
            
            # Check file size limit
            max_size = self.safety_config['max_file_size']
            if max_size <= 0:
                validation_result['errors'].append("Invalid max_file_size")
            elif max_size > 1024 * 1024 * 1024:  # 1GB
                validation_result['warnings'].append("max_file_size is very large")
            
            # Check allowed file types
            allowed_types = self.safety_config['allowed_file_types']
            if not isinstance(allowed_types, list) or len(allowed_types) == 0:
                validation_result['errors'].append("No allowed file types specified")
            
            # Check blocked commands
            blocked_commands = self.safety_config['blocked_commands']
            if not isinstance(blocked_commands, list):
                validation_result['errors'].append("blocked_commands must be a list")
            
            validation_result['valid'] = len(validation_result['errors']) == 0
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating safety configuration: {e}")
            return {'valid': False, 'errors': [str(e)], 'warnings': []}
