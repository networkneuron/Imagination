#!/usr/bin/env python3
"""
Build script to convert the Ultimate AI System Automation Agent to an executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_gui.txt"])
        print("✅ Requirements installed successfully")
        return True
    except Exception as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui_main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'psutil',
        'requests',
        'schedule',
        'pyautogui',
        'pywhatkit',
        'yagmail',
        'selenium',
        'beautifulsoup4',
        'speechrecognition',
        'pyttsx3'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='UltimateAIAutomationAgent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('automation_agent.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Spec file created")

def create_icon():
    """Create a simple icon file (if not exists)"""
    if not os.path.exists('icon.ico'):
        print("📝 Creating default icon...")
        # Create a simple text-based icon placeholder
        icon_content = '''# This is a placeholder for the icon
# In a real implementation, you would use a proper .ico file
# You can create one using online tools or image editors
'''
        with open('icon.txt', 'w') as f:
            f.write(icon_content)
        print("💡 Please add a proper icon.ico file for the executable")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    try:
        # Clean previous builds
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        
        # Run PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", "--onefile", "--windowed", "--name", "UltimateAIAutomationAgent", "gui_main.py"]
        
        if os.path.exists('icon.ico'):
            cmd.extend(["--icon", "icon.ico"])
        
        subprocess.check_call(cmd)
        
        print("✅ Executable built successfully!")
        print("📁 Executable location: dist/UltimateAIAutomationAgent.exe")
        return True
        
    except Exception as e:
        print(f"❌ Error building executable: {e}")
        return False

def create_installer_script():
    """Create a simple installer script"""
    installer_content = '''@echo off
echo Installing Ultimate AI System Automation Agent...

REM Create installation directory
if not exist "C:\\Program Files\\UltimateAIAutomationAgent" mkdir "C:\\Program Files\\UltimateAIAutomationAgent"

REM Copy executable
copy "dist\\UltimateAIAutomationAgent.exe" "C:\\Program Files\\UltimateAIAutomationAgent\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Ultimate AI Automation Agent.lnk'); $Shortcut.TargetPath = 'C:\\Program Files\\UltimateAIAutomationAgent\\UltimateAIAutomationAgent.exe'; $Shortcut.Save()"

echo Installation completed!
echo You can now run the agent from the desktop shortcut or Start Menu.
pause
'''
    
    with open('install.bat', 'w') as f:
        f.write(installer_content)
    
    print("✅ Installer script created: install.bat")

def create_readme():
    """Create a README for the executable"""
    readme_content = '''# 🚀 Ultimate AI System Automation Agent - Executable Version

## Installation
1. Run `install.bat` as Administrator to install the application
2. The application will be installed to `C:\\Program Files\\UltimateAIAutomationAgent\\`
3. A desktop shortcut will be created automatically

## Usage
1. Double-click the desktop shortcut or run `UltimateAIAutomationAgent.exe`
2. Click "START AGENT" to begin automation
3. Use the control panel to manage tasks and monitor system status

## Features
- Modern Sci-Fi GUI interface
- Real-time system monitoring
- Automated task execution
- Activity logging
- System health checks
- File cleanup automation

## System Requirements
- Windows 10/11 (64-bit)
- 4GB RAM minimum
- 100MB free disk space
- Internet connection (for some features)

## Troubleshooting
- If the application doesn't start, try running as Administrator
- Check the activity log for error messages
- Ensure all required permissions are granted

## Support
For support and updates, visit the project repository.

---
© 2024 Ultimate AI System Automation Agent
'''
    
    with open('README_EXECUTABLE.txt', 'w') as f:
        f.write(readme_content)
    
    print("✅ README created: README_EXECUTABLE.txt")

def main():
    """Main build process"""
    print("🚀 Ultimate AI System Automation Agent - Build Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('gui_main.py'):
        print("❌ gui_main.py not found. Please run this script from the project directory.")
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Create spec file
    create_spec_file()
    
    # Create icon placeholder
    create_icon()
    
    # Build executable
    if not build_executable():
        return False
    
    # Create installer
    create_installer_script()
    
    # Create README
    create_readme()
    
    print("\n🎉 Build process completed successfully!")
    print("\nFiles created:")
    print("- dist/UltimateAIAutomationAgent.exe (Main executable)")
    print("- install.bat (Installer script)")
    print("- README_EXECUTABLE.txt (User documentation)")
    print("\nTo install the application, run 'install.bat' as Administrator")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Build process failed. Please check the error messages above.")
        sys.exit(1)
    else:
        print("\n✅ Build process completed successfully!")
