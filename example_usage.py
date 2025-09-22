#!/usr/bin/env python3
"""
Example usage of the Ultimate AI System Automation Agent

This script demonstrates various features and capabilities of the automation agent.
"""

import time
from datetime import datetime, timedelta
from main import UltimateAIAutomationAgent

def main():
    """Example usage of the automation agent"""
    
    print("🚀 Ultimate AI System Automation Agent - Example Usage")
    print("=" * 60)
    
    # Initialize the agent
    print("Initializing automation agent...")
    agent = UltimateAIAutomationAgent()
    
    # Start the agent
    print("Starting automation agent...")
    agent.start()
    
    try:
        # Example 1: System Information
        print("\n📊 System Information:")
        print("-" * 30)
        system_info = agent.system_executor.get_system_info()
        print(f"Platform: {system_info.get('platform', 'Unknown')}")
        print(f"CPU Count: {system_info.get('cpu_count', 'Unknown')}")
        print(f"Memory Total: {system_info.get('memory_total', 0) / (1024**3):.2f} GB")
        
        # Example 2: File Operations
        print("\n📁 File Operations:")
        print("-" * 30)
        
        # Create a test file
        test_file = "test_automation.txt"
        content = f"Created by Ultimate AI Automation Agent at {datetime.now()}"
        
        if agent.file_manager.create_file(test_file, content):
            print(f"✅ Created file: {test_file}")
            
            # Get file info
            file_info = agent.file_manager.get_file_info(test_file)
            print(f"File size: {file_info.get('size', 0)} bytes")
            print(f"Created: {file_info.get('created', 'Unknown')}")
        
        # Example 3: Process Monitoring
        print("\n🔍 Process Monitoring:")
        print("-" * 30)
        
        # Get top processes by CPU usage
        processes = agent.process_monitor.get_processes(sort_by="cpu", limit=5)
        print("Top 5 processes by CPU usage:")
        for i, proc in enumerate(processes, 1):
            print(f"{i}. {proc.name}: {proc.cpu_percent:.1f}% CPU, {proc.memory_mb:.1f} MB RAM")
        
        # Example 4: System Health Check
        print("\n🏥 System Health Check:")
        print("-" * 30)
        
        # Perform health check
        agent.system_health_check()
        
        # Get system info
        system_info = agent.process_monitor.get_system_info()
        print(f"CPU Usage: {system_info.get('cpu', {}).get('percent', 0):.1f}%")
        print(f"Memory Usage: {system_info.get('memory', {}).get('percent', 0):.1f}%")
        print(f"Disk Usage: {system_info.get('disk', {}).get('percent', 0):.1f}%")
        
        # Example 5: Voice Commands (if available)
        print("\n🎤 Voice Commands:")
        print("-" * 30)
        
        # Add some example voice commands
        agent.voice_processor.add_voice_command(
            command="show status",
            callback=lambda: print("System status displayed!"),
            description="Show current system status"
        )
        
        agent.voice_processor.add_voice_command(
            command="clean files",
            callback=lambda: agent.cleanup_temp_files(),
            description="Clean up temporary files"
        )
        
        print("Voice commands added:")
        commands = agent.voice_processor.get_available_commands()
        for cmd, desc in commands.items():
            print(f"  - '{cmd}': {desc}")
        
        # Example 6: AI Chatbot (if configured)
        print("\n🤖 AI Chatbot:")
        print("-" * 30)
        
        # Test AI response (will use fallback if no API configured)
        test_message = "Hello, how are you today?"
        response = agent.ai_chatbot.generate_response(test_message)
        print(f"User: {test_message}")
        print(f"AI: {response}")
        
        # Example 7: Task Management
        print("\n📋 Task Management:")
        print("-" * 30)
        
        # List all registered tasks
        print("Registered automation tasks:")
        for task_id, task in agent.tasks.items():
            status = "✅ Enabled" if task.enabled else "❌ Disabled"
            print(f"  - {task.name} ({task_id}): {status}")
        
        # Example 8: Safety Features
        print("\n🛡️ Safety Features:")
        print("-" * 30)
        
        # Check safety status
        safety_status = agent.safety_manager.get_safety_status()
        print(f"Safety logging enabled: {safety_status.get('safety_config', {}).get('log_all_actions', False)}")
        print(f"Total actions logged: {safety_status.get('total_actions_logged', 0)}")
        print(f"Quarantine directory: {safety_status.get('quarantine_directory', 'Not set')}")
        
        # Example 9: Configuration
        print("\n⚙️ Configuration:")
        print("-" * 30)
        
        # Get configuration info
        config_info = agent.config_manager.get_config_info()
        print(f"Config file: {config_info.get('config_file', 'Unknown')}")
        print(f"Version: {config_info.get('version', 'Unknown')}")
        print(f"Last updated: {config_info.get('updated_at', 'Unknown')}")
        
        # Example 10: Cleanup
        print("\n🧹 Cleanup:")
        print("-" * 30)
        
        # Clean up the test file
        if agent.file_manager.delete_file(test_file, confirm=False):
            print(f"✅ Deleted test file: {test_file}")
        
        print("\n✨ Example completed successfully!")
        print("The automation agent is running in the background.")
        print("You can now use the interactive mode or let it run automated tasks.")
        
        # Keep the agent running for demonstration
        print("\nPress Ctrl+C to stop the agent...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down automation agent...")
        agent.stop()
        print("✅ Agent stopped successfully!")

if __name__ == "__main__":
    main()
