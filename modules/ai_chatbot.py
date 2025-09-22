"""
AI Chatbot Integration Module

Handles AI-powered chatbot functionality, sentiment analysis, and intelligent responses.
"""

import logging
import json
import requests
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import threading
import time

class AIChatbot:
    """Handles AI chatbot functionality"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.config = self.config_manager.load_config()
        self.ai_config = self.config.get('ai', {})
        self.conversation_history = []
        self.response_rules = []
        
    def setup_openai(self, api_key: str, model: str = "gpt-3.5-turbo") -> bool:
        """Setup OpenAI API"""
        try:
            self.ai_config['openai'] = {
                'api_key': api_key,
                'model': model,
                'enabled': True
            }
            self.logger.info("OpenAI API configured")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up OpenAI: {e}")
            return False
    
    def setup_anthropic(self, api_key: str, model: str = "claude-3-sonnet-20240229") -> bool:
        """Setup Anthropic Claude API"""
        try:
            self.ai_config['anthropic'] = {
                'api_key': api_key,
                'model': model,
                'enabled': True
            }
            self.logger.info("Anthropic Claude API configured")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up Anthropic: {e}")
            return False
    
    def generate_response(self, message: str, context: str = "", platform: str = "general") -> str:
        """Generate AI response to a message"""
        try:
            # Add to conversation history
            self.conversation_history.append({
                'timestamp': datetime.now(),
                'user_message': message,
                'platform': platform
            })
            
            # Check for rule-based responses first
            rule_response = self._check_response_rules(message, platform)
            if rule_response:
                return rule_response
            
            # Generate AI response
            if self.ai_config.get('openai', {}).get('enabled', False):
                return self._generate_openai_response(message, context)
            elif self.ai_config.get('anthropic', {}).get('enabled', False):
                return self._generate_anthropic_response(message, context)
            else:
                return self._generate_fallback_response(message)
                
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "I'm sorry, I'm having trouble processing your message right now."
    
    def _generate_openai_response(self, message: str, context: str) -> str:
        """Generate response using OpenAI API"""
        try:
            api_key = self.ai_config['openai']['api_key']
            model = self.ai_config['openai']['model']
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Prepare messages
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant. Be concise and helpful."}
            ]
            
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            
            # Add conversation history
            for conv in self.conversation_history[-5:]:  # Last 5 messages
                messages.append({"role": "user", "content": conv['user_message']})
            
            messages.append({"role": "user", "content": message})
            
            data = {
                "model": model,
                "messages": messages,
                "max_tokens": 150,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Add to conversation history
                self.conversation_history.append({
                    'timestamp': datetime.now(),
                    'ai_response': ai_response,
                    'platform': 'openai'
                })
                
                return ai_response
            else:
                self.logger.error(f"OpenAI API error: {response.text}")
                return self._generate_fallback_response(message)
                
        except Exception as e:
            self.logger.error(f"Error generating OpenAI response: {e}")
            return self._generate_fallback_response(message)
    
    def _generate_anthropic_response(self, message: str, context: str) -> str:
        """Generate response using Anthropic Claude API"""
        try:
            api_key = self.ai_config['anthropic']['api_key']
            model = self.ai_config['anthropic']['model']
            
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            # Prepare prompt
            prompt = "You are a helpful AI assistant. Be concise and helpful.\n\n"
            
            if context:
                prompt += f"Context: {context}\n\n"
            
            # Add conversation history
            for conv in self.conversation_history[-5:]:  # Last 5 messages
                prompt += f"Human: {conv['user_message']}\n"
                if 'ai_response' in conv:
                    prompt += f"Assistant: {conv['ai_response']}\n"
            
            prompt += f"Human: {message}\nAssistant:"
            
            data = {
                "model": model,
                "max_tokens": 150,
                "prompt": prompt
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['content'][0]['text']
                
                # Add to conversation history
                self.conversation_history.append({
                    'timestamp': datetime.now(),
                    'ai_response': ai_response,
                    'platform': 'anthropic'
                })
                
                return ai_response
            else:
                self.logger.error(f"Anthropic API error: {response.text}")
                return self._generate_fallback_response(message)
                
        except Exception as e:
            self.logger.error(f"Error generating Anthropic response: {e}")
            return self._generate_fallback_response(message)
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate fallback response when AI services are unavailable"""
        fallback_responses = [
            "I understand your message. How can I help you further?",
            "Thank you for your message. I'm here to assist you.",
            "I received your message. What would you like to know?",
            "Thanks for reaching out! How can I be of service?",
            "I'm here to help. What do you need assistance with?"
        ]
        
        # Simple keyword-based responses
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! How can I help you today?"
        elif any(word in message_lower for word in ['thank', 'thanks']):
            return "You're welcome! Is there anything else I can help you with?"
        elif any(word in message_lower for word in ['help', 'support']):
            return "I'm here to help! What do you need assistance with?"
        elif any(word in message_lower for word in ['bye', 'goodbye', 'see you']):
            return "Goodbye! Have a great day!"
        else:
            return fallback_responses[len(message) % len(fallback_responses)]
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            # Simple sentiment analysis (in production, use a proper NLP library)
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'happy', 'pleased']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'angry', 'sad', 'disappointed', 'frustrated', 'annoyed']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                sentiment = 'positive'
                score = 0.5 + (positive_count - negative_count) * 0.1
            elif negative_count > positive_count:
                sentiment = 'negative'
                score = 0.5 - (negative_count - positive_count) * 0.1
            else:
                sentiment = 'neutral'
                score = 0.5
            
            return {
                'sentiment': sentiment,
                'score': min(max(score, 0), 1),
                'positive_words': positive_count,
                'negative_words': negative_count
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
            return {'sentiment': 'neutral', 'score': 0.5, 'positive_words': 0, 'negative_words': 0}
    
    def add_response_rule(self, rule: Dict[str, Any]):
        """Add a response rule for the chatbot"""
        try:
            self.response_rules.append(rule)
            self.logger.info(f"Response rule added: {rule.get('name', 'Unnamed')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding response rule: {e}")
            return False
    
    def _check_response_rules(self, message: str, platform: str) -> Optional[str]:
        """Check if message matches any response rules"""
        try:
            message_lower = message.lower()
            
            for rule in self.response_rules:
                # Check if rule applies to this platform
                if 'platforms' in rule and platform not in rule['platforms']:
                    continue
                
                # Check keywords
                if 'keywords' in rule:
                    keywords = rule['keywords']
                    if isinstance(keywords, list):
                        if not any(keyword.lower() in message_lower for keyword in keywords):
                            continue
                    else:
                        if keywords.lower() not in message_lower:
                            continue
                
                # Check sentiment
                if 'sentiment' in rule:
                    sentiment_analysis = self.analyze_sentiment(message)
                    if sentiment_analysis['sentiment'] != rule['sentiment']:
                        continue
                
                # Return response
                return rule['response']
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error checking response rules: {e}")
            return None
    
    def create_faq_bot(self, faq_data: List[Dict[str, str]]) -> bool:
        """Create an FAQ bot with predefined Q&A pairs"""
        try:
            for faq in faq_data:
                rule = {
                    'name': f"FAQ: {faq['question']}",
                    'keywords': [faq['question']],
                    'response': faq['answer'],
                    'platforms': ['general']
                }
                self.add_response_rule(rule)
            
            self.logger.info(f"FAQ bot created with {len(faq_data)} Q&A pairs")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating FAQ bot: {e}")
            return False
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        try:
            return self.conversation_history[-limit:]
            
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {e}")
            return []
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        try:
            self.conversation_history.clear()
            self.logger.info("Conversation history cleared")
            
        except Exception as e:
            self.logger.error(f"Error clearing conversation history: {e}")
    
    def save_conversation_history(self, filename: str = None):
        """Save conversation history to file"""
        try:
            if not filename:
                filename = f"conversation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w') as f:
                json.dump(self.conversation_history, f, indent=2, default=str)
            
            self.logger.info(f"Conversation history saved to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving conversation history: {e}")
            return False
    
    def load_conversation_history(self, filename: str) -> bool:
        """Load conversation history from file"""
        try:
            with open(filename, 'r') as f:
                self.conversation_history = json.load(f)
            
            self.logger.info(f"Conversation history loaded from {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading conversation history: {e}")
            return False
    
    def get_response_statistics(self) -> Dict[str, Any]:
        """Get statistics about chatbot responses"""
        try:
            total_messages = len(self.conversation_history)
            ai_responses = len([conv for conv in self.conversation_history if 'ai_response' in conv])
            rule_responses = len([conv for conv in self.conversation_history if conv.get('response_type') == 'rule'])
            
            # Sentiment analysis of user messages
            sentiments = []
            for conv in self.conversation_history:
                if 'user_message' in conv:
                    sentiment = self.analyze_sentiment(conv['user_message'])
                    sentiments.append(sentiment['sentiment'])
            
            sentiment_counts = {}
            for sentiment in sentiments:
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            return {
                'total_messages': total_messages,
                'ai_responses': ai_responses,
                'rule_responses': rule_responses,
                'sentiment_distribution': sentiment_counts,
                'response_rules_count': len(self.response_rules)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting response statistics: {e}")
            return {}
    
    def train_on_conversation(self, conversation_file: str) -> bool:
        """Train the chatbot on a conversation file"""
        try:
            with open(conversation_file, 'r') as f:
                conversations = json.load(f)
            
            # Extract patterns and create rules
            for conv in conversations:
                if 'user_message' in conv and 'ai_response' in conv:
                    # Create a simple rule based on the conversation
                    rule = {
                        'name': f"Trained: {conv['user_message'][:50]}...",
                        'keywords': [conv['user_message']],
                        'response': conv['ai_response'],
                        'platforms': ['general']
                    }
                    self.add_response_rule(rule)
            
            self.logger.info(f"Trained chatbot on {len(conversations)} conversations")
            return True
            
        except Exception as e:
            self.logger.error(f"Error training chatbot: {e}")
            return False
