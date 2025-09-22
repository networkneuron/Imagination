# 🚀 Ultimate AI System Automation Agent 🚀

An advanced AI-powered system automation agent with full control over the computer and communication platforms. Capable of executing system-level commands, managing files, automating messaging and emails, and optimizing workflows.

## ✨ Features

### 🖥 System Management
- **Command Execution**: Run terminal, PowerShell, and command prompt commands safely
- **File Management**: Create, edit, copy, move, delete, and organize files/folders
- **Process Monitoring**: Monitor CPU, RAM, disk usage, and system processes
- **Resource Optimization**: Clean up temporary files and optimize system performance

### 📧 Communication Automation
- **Email Automation**: Send emails, schedule campaigns, auto-reply based on content
- **WhatsApp Integration**: Send messages, bulk messaging, auto-replies
- **Telegram Bot**: Full bot integration with inline keyboards and automation
- **Social Media**: Facebook, Instagram, LinkedIn posting and messaging

### 🤖 AI-Powered Features
- **Smart Chatbot**: AI-powered responses with sentiment analysis
- **Voice Commands**: Voice recognition and text-to-speech capabilities
- **Intelligent Automation**: Context-aware task execution
- **Natural Language Processing**: Understand and respond to natural language commands

### 🔒 Safety & Security
- **Safety Manager**: Confirmation prompts for dangerous actions
- **File Quarantine**: Automatic quarantine of suspicious files
- **Action Logging**: Complete audit trail of all actions
- **Security Scanning**: File threat detection and analysis

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ultimate-ai-automation-agent
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the agent**:
```bash
python main.py
```

### Configuration

1. **Create configuration file**:
```bash
python -c "from modules.config_manager import ConfigManager; ConfigManager().create_config_template()"
```

2. **Edit `config.json`** with your settings:
```json
{
  "email": {
    "enabled": true,
    "smtp": {
      "server": "smtp.gmail.com",
      "port": 587,
      "username": "your_email@gmail.com",
      "password": "your_password"
    }
  },
  "telegram": {
    "enabled": true,
    "bot_token": "your_bot_token"
  }
}
```

## 📖 Usage Examples

### System Commands
```python
from main import UltimateAIAutomationAgent

agent = UltimateAIAutomationAgent()
agent.start()

# Execute system command
success, stdout, stderr = agent.system_executor.execute_command("dir")

# Install package
agent.system_executor.install_package("requests")
```

### Email Automation
```python
# Send email
agent.email_automation.send_email(
    to="recipient@example.com",
    subject="Test Email",
    body="This is a test email from the automation agent"
)

# Schedule email
agent.email_automation.schedule_email(
    to="team@company.com",
    subject="Daily Report",
    body="Daily system summary...",
    send_time=datetime.now() + timedelta(hours=1)
)
```

### WhatsApp Messaging
```python
# Send WhatsApp message
agent.whatsapp_automation.send_message(
    phone_number="+1234567890",
    message="Hello from the automation agent!"
)

# Bulk messaging
recipients = ["+1234567890", "+0987654321"]
agent.whatsapp_automation.send_bulk_message(
    recipients=recipients,
    message="Bulk message to all contacts"
)
```

### Voice Commands
```python
# Add voice command
agent.voice_processor.add_voice_command(
    command="check system status",
    callback=lambda: agent.show_status(),
    description="Check current system status"
)

# Start voice listening
agent.voice_processor.start_continuous_listening()
```

### AI Chatbot
```python
# Setup OpenAI
agent.ai_chatbot.setup_openai(api_key="your_api_key")

# Generate response
response = agent.ai_chatbot.generate_response(
    message="What's the weather like?",
    context="User asking about weather"
)
```

## 🔧 Configuration

### Email Configuration
```json
{
  "email": {
    "enabled": true,
    "from_email": "your_email@example.com",
    "smtp": {
      "server": "smtp.gmail.com",
      "port": 587,
      "username": "your_email@gmail.com",
      "password": "your_app_password",
      "use_tls": true
    },
    "imap": {
      "server": "imap.gmail.com",
      "port": 993,
      "username": "your_email@gmail.com",
      "password": "your_app_password",
      "use_ssl": true
    }
  }
}
```

### Telegram Bot Configuration
```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "your_bot_token_from_botfather"
  }
}
```

### AI Configuration
```json
{
  "ai": {
    "openai": {
      "enabled": true,
      "api_key": "your_openai_api_key",
      "model": "gpt-3.5-turbo"
    },
    "anthropic": {
      "enabled": false,
      "api_key": "your_anthropic_api_key",
      "model": "claude-3-sonnet-20240229"
    }
  }
}
```

## 🛡️ Safety Features

### Dangerous Action Confirmation
The agent will ask for confirmation before executing potentially dangerous commands:
- File deletion operations
- System shutdown/reboot
- Format operations
- Process termination

### File Safety
- Automatic file type validation
- File size limits
- Suspicious content scanning
- Quarantine system for suspicious files

### Action Logging
All actions are logged for audit purposes:
- Command execution
- File operations
- Email sending
- Message sending

## 📊 Monitoring & Alerts

### System Monitoring
- CPU usage monitoring
- Memory usage tracking
- Disk space monitoring
- Temperature monitoring (if available)

### Alert System
- Email alerts for system issues
- Desktop notifications
- Sound alerts (optional)
- Custom alert thresholds

## 🔌 API Integration

### Supported APIs
- **OpenAI GPT**: For AI-powered responses
- **Anthropic Claude**: Alternative AI provider
- **Telegram Bot API**: For messaging automation
- **Email APIs**: SMTP/IMAP for email automation

### Web Scraping
- BeautifulSoup for HTML parsing
- Selenium for dynamic content
- Requests for API calls

## 🎯 Use Cases

### Business Automation
- Daily email reports
- Automated customer responses
- Social media posting
- System monitoring and alerts

### Personal Productivity
- File organization
- Automated backups
- Voice-controlled tasks
- Smart home integration

### Development Workflow
- Automated testing
- Code deployment
- Environment monitoring
- Log analysis

## 🚨 Safety Guidelines

1. **Always review** configuration before enabling features
2. **Test commands** in a safe environment first
3. **Keep backups** of important data
4. **Monitor logs** regularly for suspicious activity
5. **Use strong passwords** for all accounts
6. **Enable two-factor authentication** where possible

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the configuration examples

## 🔄 Updates

The agent automatically checks for updates and can be configured to:
- Auto-update dependencies
- Download new features
- Apply security patches

---

**⚠️ Disclaimer**: This tool has powerful capabilities. Use responsibly and always ensure you have proper authorization for any automated actions on systems you don't own.
