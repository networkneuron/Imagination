"""
System Command Execution Module

Handles execution of system-level commands with safety checks and logging.
"""

import os
import sys
import subprocess
import logging
import platform
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

class SystemCommandExecutor:
    """Handles safe execution of system commands"""
    
    def __init__(self, safety_manager):
        self.safety_manager = safety_manager
        self.logger = logging.getLogger(__name__)
        self.system = platform.system().lower()
        
        # Dangerous commands that require confirmation
        self.dangerous_commands = [
            'rm -rf', 'del /s', 'format', 'fdisk', 'dd if=', 'shutdown', 'reboot',
            'halt', 'poweroff', 'init 0', 'init 6', 'systemctl poweroff',
            'systemctl reboot', 'taskkill /f', 'kill -9', 'killall'
        ]
    
    def execute_command(self, command: str, confirm_dangerous: bool = True) -> Tuple[bool, str, str]:
        """
        Execute a system command safely
        
        Args:
            command: The command to execute
            confirm_dangerous: Whether to confirm before executing dangerous commands
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            # Check if command is dangerous
            if self.is_dangerous_command(command) and confirm_dangerous:
                if not self.safety_manager.confirm_dangerous_action(f"Execute dangerous command: {command}"):
                    return False, "", "Command execution cancelled by user"
            
            # Log the command
            self.logger.info(f"Executing command: {command}")
            
            # Execute the command
            if self.system == "windows":
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=300  # 5 minute timeout
                )
            else:
                result = subprocess.run(
                    command.split(), 
                    capture_output=True, 
                    text=True, 
                    timeout=300
                )
            
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            
            if success:
                self.logger.info(f"Command executed successfully: {command}")
            else:
                self.logger.warning(f"Command failed with return code {result.returncode}: {command}")
                self.logger.warning(f"Error output: {stderr}")
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {command}")
            return False, "", "Command timed out"
        except Exception as e:
            self.logger.error(f"Error executing command '{command}': {e}")
            return False, "", str(e)
    
    def is_dangerous_command(self, command: str) -> bool:
        """Check if a command is potentially dangerous"""
        command_lower = command.lower()
        return any(dangerous in command_lower for dangerous in self.dangerous_commands)
    
    def run_powershell_command(self, command: str) -> Tuple[bool, str, str]:
        """Execute a PowerShell command on Windows"""
        if self.system != "windows":
            return False, "", "PowerShell is only available on Windows"
        
        ps_command = f"powershell -Command \"{command}\""
        return self.execute_command(ps_command)
    
    def run_bash_command(self, command: str) -> Tuple[bool, str, str]:
        """Execute a bash command on Unix-like systems"""
        if self.system == "windows":
            return False, "", "Bash is not available on Windows"
        
        bash_command = f"bash -c \"{command}\""
        return self.execute_command(bash_command)
    
    def install_package(self, package_name: str, package_manager: str = "auto") -> bool:
        """
        Install a package using the appropriate package manager
        
        Args:
            package_name: Name of the package to install
            package_manager: Package manager to use (auto, pip, apt, yum, brew, choco)
        """
        try:
            if package_manager == "auto":
                package_manager = self.detect_package_manager()
            
            commands = {
                "pip": f"pip install {package_name}",
                "pip3": f"pip3 install {package_name}",
                "apt": f"sudo apt update && sudo apt install -y {package_name}",
                "yum": f"sudo yum install -y {package_name}",
                "dnf": f"sudo dnf install -y {package_name}",
                "brew": f"brew install {package_name}",
                "choco": f"choco install {package_name} -y",
                "winget": f"winget install {package_name}",
            }
            
            if package_manager not in commands:
                self.logger.error(f"Unsupported package manager: {package_manager}")
                return False
            
            success, stdout, stderr = self.execute_command(commands[package_manager])
            
            if success:
                self.logger.info(f"Successfully installed package: {package_name}")
            else:
                self.logger.error(f"Failed to install package {package_name}: {stderr}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error installing package {package_name}: {e}")
            return False
    
    def detect_package_manager(self) -> str:
        """Detect the appropriate package manager for the system"""
        if self.system == "windows":
            # Check for Chocolatey
            success, _, _ = self.execute_command("choco --version", confirm_dangerous=False)
            if success:
                return "choco"
            
            # Check for winget
            success, _, _ = self.execute_command("winget --version", confirm_dangerous=False)
            if success:
                return "winget"
            
            return "pip"  # Fallback to pip
        
        elif self.system == "linux":
            # Check for apt
            success, _, _ = self.execute_command("apt --version", confirm_dangerous=False)
            if success:
                return "apt"
            
            # Check for yum
            success, _, _ = self.execute_command("yum --version", confirm_dangerous=False)
            if success:
                return "yum"
            
            # Check for dnf
            success, _, _ = self.execute_command("dnf --version", confirm_dangerous=False)
            if success:
                return "dnf"
            
            return "pip"  # Fallback to pip
        
        elif self.system == "darwin":  # macOS
            # Check for Homebrew
            success, _, _ = self.execute_command("brew --version", confirm_dangerous=False)
            if success:
                return "brew"
            
            return "pip"  # Fallback to pip
        
        return "pip"  # Default fallback
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        info = {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }
        
        # Get additional system info
        try:
            import psutil
            info.update({
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_total": psutil.disk_usage('/').total if os.path.exists('/') else 0,
            })
        except ImportError:
            pass
        
        return info
    
    def create_startup_script(self, script_name: str, script_content: str) -> bool:
        """Create a startup script for the current platform"""
        try:
            if self.system == "windows":
                # Create batch file in startup folder
                startup_path = os.path.expanduser("~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup")
                script_path = os.path.join(startup_path, f"{script_name}.bat")
            else:
                # Create shell script in user's home directory
                script_path = os.path.expanduser(f"~/{script_name}.sh")
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make executable on Unix systems
            if self.system != "windows":
                os.chmod(script_path, 0o755)
            
            self.logger.info(f"Created startup script: {script_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating startup script: {e}")
            return False
    
    def run_script(self, script_path: str) -> Tuple[bool, str, str]:
        """Execute a script file"""
        try:
            if not os.path.exists(script_path):
                return False, "", f"Script not found: {script_path}"
            
            # Make executable on Unix systems
            if self.system != "windows":
                os.chmod(script_path, 0o755)
            
            # Execute the script
            if self.system == "windows":
                return self.execute_command(script_path)
            else:
                return self.execute_command(f"./{script_path}")
                
        except Exception as e:
            self.logger.error(f"Error running script {script_path}: {e}")
            return False, "", str(e)
