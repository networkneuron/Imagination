# 🚀 Quick Start Guide

Get up and running with the Ultimate AI System Automation Agent in minutes!

## 📋 Prerequisites

- Python 3.8 or higher
- Windows, macOS, or Linux
- Internet connection (for AI features and web automation)

## ⚡ Installation

### 1. Download the Agent
```bash
git clone <repository-url>
cd ultimate-ai-automation-agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Agent
```bash
python main.py
```

## 🔧 Basic Configuration

### 1. Create Configuration File
The agent will create a default `config.json` file on first run.

### 2. Enable Features
Edit `config.json` to enable the features you need:

```json
{
  "email": {
    "enabled": true,
    "from_email": "your_email@example.com"
  },
  "telegram": {
    "enabled": true,
    "bot_token": "your_bot_token"
  }
}
```

## 🎯 Quick Examples

### System Information
```python
from main import UltimateAIAutomationAgent

agent = UltimateAIAutomationAgent()
agent.start()

# Get system info
system_info = agent.system_executor.get_system_info()
print(f"Platform: {system_info['platform']}")
```

### Send Email
```python
# Configure email first in config.json
agent.email_automation.send_email(
    to="recipient@example.com",
    subject="Hello from AI Agent",
    body="This is an automated email!"
)
```

### Voice Commands
```python
# Add a voice command
agent.voice_processor.add_voice_command(
    command="check status",
    callback=lambda: print("System is running!"),
    description="Check system status"
)

# Start listening
agent.voice_processor.start_continuous_listening()
```

### File Management
```python
# Create a file
agent.file_manager.create_file("test.txt", "Hello World!")

# Find files
files = agent.file_manager.find_files(".", "*.txt")

# Clean up old files
agent.file_manager.cleanup_old_files(".", days_old=30)
```

## 🛡️ Safety First

The agent includes built-in safety features:

- **Confirmation prompts** for dangerous actions
- **File quarantine** for suspicious files
- **Action logging** for audit trails
- **Command validation** before execution

## 📊 Monitoring

### System Health
```python
# Check system health
agent.system_health_check()

# Get process information
processes = agent.process_monitor.get_processes(limit=10)
```

### Alerts
The agent can send alerts for:
- High CPU usage
- Low disk space
- System errors
- Failed tasks

## 🤖 AI Features

### Setup OpenAI (Optional)
```python
agent.ai_chatbot.setup_openai(api_key="your_api_key")

# Generate AI response
response = agent.ai_chatbot.generate_response("What's the weather?")
```

### Voice Recognition
```python
# Listen for voice input
text = agent.voice_processor.listen()
print(f"You said: {text}")
```

## 📱 Communication

### WhatsApp
```python
# Send WhatsApp message
agent.whatsapp_automation.send_message(
    phone_number="+1234567890",
    message="Hello from AI Agent!"
)
```

### Telegram Bot
```python
# Setup bot
agent.telegram_automation.setup_bot("your_bot_token")

# Send message
agent.telegram_automation.send_message(
    chat_id="123456789",
    message="Hello from AI Agent!"
)
```

## 🔄 Automation Tasks

### Schedule Tasks
```python
# Register a custom task
agent.register_task(
    "daily_cleanup",
    "Daily Cleanup",
    "Clean up temporary files daily",
    agent.cleanup_temp_files,
    "0 2 * * *"  # Daily at 2 AM
)
```

### Auto-Reply Rules
```python
# Setup email auto-reply
agent.email_automation.setup_auto_reply({
    "name": "Out of Office",
    "keywords": ["urgent", "important"],
    "reply_message": "I'm currently out of office. I'll respond when I return."
})
```

## 🚨 Troubleshooting

### Common Issues

1. **Permission Errors**: Run as administrator/root if needed
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **Configuration Errors**: Check `config.json` syntax
4. **Voice Recognition**: Ensure microphone is working

### Logs
Check the log file: `automation_agent.log`

### Debug Mode
Set logging level to DEBUG in `config.json`:
```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

## 📚 Next Steps

1. **Read the full README.md** for detailed documentation
2. **Explore example_usage.py** for more examples
3. **Configure your integrations** (email, Telegram, etc.)
4. **Set up automation tasks** for your workflow
5. **Enable AI features** for intelligent automation

## 🆘 Need Help?

- Check the documentation in README.md
- Review example_usage.py for code examples
- Create an issue on GitHub
- Check the logs for error messages

---

**Happy Automating! 🚀**
