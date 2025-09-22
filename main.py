#!/usr/bin/env python3
"""
🚀 Ultimate AI System Automation Agent 🚀

An advanced AI-powered system automation agent with full control over the computer
and communication platforms. Capable of executing system-level commands, managing
files, automating messaging and emails, and optimizing workflows.

Author: AI Assistant
Version: 1.0.0
"""

import os
import sys
import json
import time
import logging
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from pathlib import Path

# Core modules
from modules.system_commands import SystemCommandExecutor
from modules.file_manager import FileManager
from modules.process_monitor import ProcessMonitor
from modules.network_automation import NetworkAutomation
from modules.email_automation import EmailAutomation
from modules.whatsapp_automation import WhatsAppAutomation
from modules.telegram_automation import TelegramAutomation
from modules.social_media_automation import SocialMediaAutomation
from modules.ai_chatbot import AIChatbot
from modules.voice_commands import VoiceCommandProcessor
from modules.config_manager import ConfigManager
from modules.safety_manager import SafetyManager

@dataclass
class AutomationTask:
    """Represents an automation task"""
    id: str
    name: str
    description: str
    function: Callable
    schedule: Optional[str] = None
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

class UltimateAIAutomationAgent:
    """
    🚀 Ultimate AI System Automation Agent 🚀
    
    Main class that orchestrates all automation capabilities
    """
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the automation agent"""
        self.config_manager = ConfigManager(config_file)
        self.safety_manager = SafetyManager()
        
        # Initialize core modules
        self.system_executor = SystemCommandExecutor(self.safety_manager)
        self.file_manager = FileManager(self.safety_manager)
        self.process_monitor = ProcessMonitor()
        self.network_automation = NetworkAutomation()
        self.email_automation = EmailAutomation(self.config_manager)
        self.whatsapp_automation = WhatsAppAutomation(self.config_manager)
        self.telegram_automation = TelegramAutomation(self.config_manager)
        self.social_media_automation = SocialMediaAutomation(self.config_manager)
        self.ai_chatbot = AIChatbot(self.config_manager)
        self.voice_processor = VoiceCommandProcessor()
        
        # Task management
        self.tasks: Dict[str, AutomationTask] = {}
        self.running = False
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.config = self.config_manager.load_config()
        
        # Register default tasks
        self.register_default_tasks()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('automation_agent.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def register_default_tasks(self):
        """Register default automation tasks"""
        # System monitoring tasks
        self.register_task(
            "system_health_check",
            "System Health Check",
            "Monitor system resources and alert if issues detected",
            self.system_health_check,
            "*/5 * * * *"  # Every 5 minutes
        )
        
        # File cleanup tasks
        self.register_task(
            "cleanup_temp_files",
            "Cleanup Temporary Files",
            "Remove temporary files and optimize disk space",
            self.cleanup_temp_files,
            "0 2 * * *"  # Daily at 2 AM
        )
        
        # Email automation tasks
        self.register_task(
            "daily_email_summary",
            "Daily Email Summary",
            "Send daily summary email to team",
            self.send_daily_summary,
            "0 8 * * *"  # Daily at 8 AM
        )
    
    def register_task(self, task_id: str, name: str, description: str, 
                     function: Callable, schedule: Optional[str] = None):
        """Register a new automation task"""
        task = AutomationTask(
            id=task_id,
            name=name,
            description=description,
            function=function,
            schedule=schedule,
            enabled=True
        )
        self.tasks[task_id] = task
        self.logger.info(f"Registered task: {name}")
    
    def start(self):
        """Start the automation agent"""
        self.logger.info("🚀 Starting Ultimate AI System Automation Agent...")
        self.running = True
        
        # Start background monitoring
        self.start_background_monitoring()
        
        # Start task scheduler
        self.start_task_scheduler()
        
        # Start voice command processor
        self.voice_processor.start()
        
        self.logger.info("✅ Automation Agent started successfully!")
    
    def stop(self):
        """Stop the automation agent"""
        self.logger.info("🛑 Stopping Ultimate AI System Automation Agent...")
        self.running = False
        self.voice_processor.stop()
        self.logger.info("✅ Automation Agent stopped")
    
    def start_background_monitoring(self):
        """Start background system monitoring"""
        def monitor():
            while self.running:
                try:
                    # Monitor system resources
                    cpu_percent = psutil.cpu_percent()
                    memory_percent = psutil.virtual_memory().percent
                    disk_percent = psutil.disk_usage('/').percent
                    
                    # Alert if resources are high
                    if cpu_percent > 80:
                        self.logger.warning(f"High CPU usage: {cpu_percent}%")
                    
                    if memory_percent > 85:
                        self.logger.warning(f"High memory usage: {memory_percent}%")
                    
                    if disk_percent > 90:
                        self.logger.warning(f"High disk usage: {disk_percent}%")
                    
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    self.logger.error(f"Error in background monitoring: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def start_task_scheduler(self):
        """Start the task scheduler"""
        def scheduler():
            while self.running:
                try:
                    # Check for scheduled tasks
                    for task in self.tasks.values():
                        if task.enabled and task.schedule:
                            # Simple cron-like scheduling (basic implementation)
                            if self.should_run_task(task):
                                self.execute_task(task)
                    
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    self.logger.error(f"Error in task scheduler: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=scheduler, daemon=True)
        thread.start()
    
    def should_run_task(self, task: AutomationTask) -> bool:
        """Check if a task should run based on its schedule"""
        # Basic implementation - in production, use a proper cron parser
        now = datetime.now()
        if task.last_run and (now - task.last_run).seconds < 300:  # 5 minutes cooldown
            return False
        return True
    
    def execute_task(self, task: AutomationTask):
        """Execute a specific task"""
        try:
            self.logger.info(f"Executing task: {task.name}")
            task.function()
            task.last_run = datetime.now()
            self.logger.info(f"Task completed: {task.name}")
        except Exception as e:
            self.logger.error(f"Error executing task {task.name}: {e}")
    
    # System Health Check Task
    def system_health_check(self):
        """Perform system health check"""
        try:
            # Check CPU temperature (if available)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current > 80:
                                self.logger.warning(f"High temperature detected: {name} = {entry.current}°C")
            except:
                pass
            
            # Check disk space
            disk_usage = psutil.disk_usage('/')
            free_gb = disk_usage.free / (1024**3)
            if free_gb < 5:
                self.logger.warning(f"Low disk space: {free_gb:.2f} GB remaining")
            
            # Check memory
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self.logger.warning(f"Critical memory usage: {memory.percent}%")
            
        except Exception as e:
            self.logger.error(f"Error in system health check: {e}")
    
    # File Cleanup Task
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            temp_dirs = [
                os.path.expanduser("~/AppData/Local/Temp"),  # Windows
                "/tmp",  # Linux/Mac
                os.path.expanduser("~/Library/Caches"),  # Mac
            ]
            
            cleaned_files = 0
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                # Only delete files older than 7 days
                                if os.path.getmtime(file_path) < time.time() - (7 * 24 * 3600):
                                    os.remove(file_path)
                                    cleaned_files += 1
                            except:
                                pass
            
            self.logger.info(f"Cleaned up {cleaned_files} temporary files")
        except Exception as e:
            self.logger.error(f"Error cleaning up temp files: {e}")
    
    # Email Automation Task
    def send_daily_summary(self):
        """Send daily summary email"""
        try:
            # Get system stats
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            # Create summary message
            summary = f"""
Daily System Summary - {datetime.now().strftime('%Y-%m-%d')}

System Status:
- CPU Usage: {cpu_percent}%
- Memory Usage: {memory_percent}%
- Disk Usage: {disk_percent}%

Automation Tasks:
- Tasks registered: {len(self.tasks)}
- Tasks enabled: {sum(1 for t in self.tasks.values() if t.enabled)}
- Last health check: {datetime.now().strftime('%H:%M:%S')}

All systems operational! 🚀
            """
            
            # Send email (if configured)
            if self.config.get('email', {}).get('enabled', False):
                self.email_automation.send_email(
                    to=self.config['email']['recipients'],
                    subject="Daily System Summary",
                    body=summary
                )
                self.logger.info("Daily summary email sent")
            
        except Exception as e:
            self.logger.error(f"Error sending daily summary: {e}")
    
    def run_interactive_mode(self):
        """Run the agent in interactive mode"""
        print("🚀 Ultimate AI System Automation Agent - Interactive Mode")
        print("Type 'help' for available commands or 'quit' to exit")
        
        while True:
            try:
                command = input("\n🤖 Agent> ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    break
                elif command == 'help':
                    self.show_help()
                elif command == 'status':
                    self.show_status()
                elif command == 'tasks':
                    self.list_tasks()
                elif command.startswith('run '):
                    task_id = command[4:]
                    self.run_task_manual(task_id)
                elif command.startswith('enable '):
                    task_id = command[7:]
                    self.enable_task(task_id)
                elif command.startswith('disable '):
                    task_id = command[8:]
                    self.disable_task(task_id)
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("👋 Goodbye!")
    
    def show_help(self):
        """Show available commands"""
        print("""
Available Commands:
- help: Show this help message
- status: Show system status
- tasks: List all registered tasks
- run <task_id>: Manually run a specific task
- enable <task_id>: Enable a task
- disable <task_id>: Disable a task
- quit/exit: Exit the program
        """)
    
    def show_status(self):
        """Show current system status"""
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        print(f"""
System Status:
- CPU Usage: {cpu_percent}%
- Memory Usage: {memory_percent}%
- Disk Usage: {disk_percent}%
- Tasks Registered: {len(self.tasks)}
- Tasks Enabled: {sum(1 for t in self.tasks.values() if t.enabled)}
- Agent Running: {self.running}
        """)
    
    def list_tasks(self):
        """List all registered tasks"""
        print("\nRegistered Tasks:")
        for task in self.tasks.values():
            status = "✅ Enabled" if task.enabled else "❌ Disabled"
            schedule_info = f" (Schedule: {task.schedule})" if task.schedule else ""
            print(f"- {task.id}: {task.name} - {status}{schedule_info}")
            print(f"  Description: {task.description}")
    
    def run_task_manual(self, task_id: str):
        """Manually run a specific task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            print(f"Running task: {task.name}")
            self.execute_task(task)
        else:
            print(f"Task '{task_id}' not found")
    
    def enable_task(self, task_id: str):
        """Enable a specific task"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            print(f"Task '{task_id}' enabled")
        else:
            print(f"Task '{task_id}' not found")
    
    def disable_task(self, task_id: str):
        """Disable a specific task"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            print(f"Task '{task_id}' disabled")
        else:
            print(f"Task '{task_id}' not found")

def main():
    """Main entry point"""
    try:
        # Create and start the automation agent
        agent = UltimateAIAutomationAgent()
        agent.start()
        
        # Run in interactive mode
        agent.run_interactive_mode()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'agent' in locals():
            agent.stop()

if __name__ == "__main__":
    main()
