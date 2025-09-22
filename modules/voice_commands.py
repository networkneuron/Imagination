"""
Voice Command Integration Module

Handles voice recognition, text-to-speech, and voice command processing.
"""

import logging
import speech_recognition as sr
import pyttsx3
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json
import os

class VoiceCommandProcessor:
    """Handles voice command processing and text-to-speech"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = None
        self.voice_commands = {}
        self.is_listening = False
        self.listen_thread = None
        self.command_callbacks = {}
        
        # Initialize TTS engine
        self._setup_tts()
        
        # Calibrate microphone
        self._calibrate_microphone()
    
    def _setup_tts(self):
        """Setup text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to set a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.8)  # Volume level (0.0 to 1.0)
            
            self.logger.info("Text-to-speech engine initialized")
            
        except Exception as e:
            self.logger.error(f"Error setting up TTS engine: {e}")
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                self.logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            self.logger.info("Microphone calibration complete")
            
        except Exception as e:
            self.logger.error(f"Error calibrating microphone: {e}")
    
    def speak(self, text: str, interrupt: bool = True):
        """Convert text to speech"""
        try:
            if interrupt and self.tts_engine.isBusy():
                self.tts_engine.stop()
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            self.logger.error(f"Error speaking text: {e}")
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 5) -> Optional[str]:
        """Listen for voice input and return transcribed text"""
        try:
            with self.microphone as source:
                self.logger.info("Listening for voice input...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            try:
                # Use Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                self.logger.info(f"Recognized: {text}")
                return text.lower()
                
            except sr.UnknownValueError:
                self.logger.warning("Could not understand audio")
                return None
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition service error: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error listening for voice input: {e}")
            return None
    
    def add_voice_command(self, command: str, callback: Callable, description: str = ""):
        """Add a voice command with callback function"""
        try:
            self.voice_commands[command.lower()] = {
                'callback': callback,
                'description': description,
                'added_at': datetime.now()
            }
            self.logger.info(f"Voice command added: {command}")
            
        except Exception as e:
            self.logger.error(f"Error adding voice command: {e}")
    
    def remove_voice_command(self, command: str):
        """Remove a voice command"""
        try:
            if command.lower() in self.voice_commands:
                del self.voice_commands[command.lower()]
                self.logger.info(f"Voice command removed: {command}")
                return True
            else:
                self.logger.warning(f"Voice command not found: {command}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing voice command: {e}")
            return False
    
    def process_voice_command(self, text: str) -> bool:
        """Process a voice command and execute callback if found"""
        try:
            if not text:
                return False
            
            # Check for exact command matches first
            if text in self.voice_commands:
                command_info = self.voice_commands[text]
                command_info['callback']()
                self.logger.info(f"Executed voice command: {text}")
                return True
            
            # Check for partial matches
            for command, info in self.voice_commands.items():
                if command in text or text in command:
                    info['callback']()
                    self.logger.info(f"Executed voice command (partial match): {command}")
                    return True
            
            # Check for keyword-based commands
            for command, info in self.voice_commands.items():
                if any(word in text for word in command.split()):
                    info['callback']()
                    self.logger.info(f"Executed voice command (keyword match): {command}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error processing voice command: {e}")
            return False
    
    def start_continuous_listening(self, timeout: int = 5, phrase_time_limit: int = 5):
        """Start continuous voice command listening"""
        if self.is_listening:
            self.logger.warning("Already listening for voice commands")
            return
        
        self.is_listening = True
        
        def listen_loop():
            while self.is_listening:
                try:
                    text = self.listen(timeout, phrase_time_limit)
                    
                    if text:
                        # Process the voice command
                        if not self.process_voice_command(text):
                            self.speak("I didn't understand that command. Please try again.")
                    
                    time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                    
                except Exception as e:
                    self.logger.error(f"Error in continuous listening: {e}")
                    time.sleep(1)
        
        self.listen_thread = threading.Thread(target=listen_loop, daemon=True)
        self.listen_thread.start()
        self.logger.info("Started continuous voice command listening")
    
    def stop_continuous_listening(self):
        """Stop continuous voice command listening"""
        if not self.is_listening:
            self.logger.warning("Not currently listening for voice commands")
            return
        
        self.is_listening = False
        
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
        
        self.logger.info("Stopped continuous voice command listening")
    
    def start(self):
        """Start the voice command processor"""
        self.start_continuous_listening()
    
    def stop(self):
        """Stop the voice command processor"""
        self.stop_continuous_listening()
    
    def get_available_commands(self) -> Dict[str, str]:
        """Get list of available voice commands"""
        try:
            return {cmd: info['description'] for cmd, info in self.voice_commands.items()}
            
        except Exception as e:
            self.logger.error(f"Error getting available commands: {e}")
            return {}
    
    def save_voice_commands(self, filename: str = "voice_commands.json"):
        """Save voice commands to file"""
        try:
            commands_data = {}
            for cmd, info in self.voice_commands.items():
                commands_data[cmd] = {
                    'description': info['description'],
                    'added_at': info['added_at'].isoformat()
                }
            
            with open(filename, 'w') as f:
                json.dump(commands_data, f, indent=2)
            
            self.logger.info(f"Voice commands saved to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving voice commands: {e}")
            return False
    
    def load_voice_commands(self, filename: str = "voice_commands.json"):
        """Load voice commands from file"""
        try:
            if not os.path.exists(filename):
                self.logger.warning(f"Voice commands file not found: {filename}")
                return False
            
            with open(filename, 'r') as f:
                commands_data = json.load(f)
            
            # Note: Callbacks cannot be loaded from JSON, so only metadata is loaded
            for cmd, info in commands_data.items():
                if cmd not in self.voice_commands:
                    self.voice_commands[cmd] = {
                        'callback': None,  # Will need to be re-registered
                        'description': info['description'],
                        'added_at': datetime.fromisoformat(info['added_at'])
                    }
            
            self.logger.info(f"Voice commands loaded from {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading voice commands: {e}")
            return False
    
    def set_voice_properties(self, rate: int = None, volume: float = None, voice_id: str = None):
        """Set TTS voice properties"""
        try:
            if rate is not None:
                self.tts_engine.setProperty('rate', rate)
            
            if volume is not None:
                self.tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))
            
            if voice_id is not None:
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if voice_id in voice.id or voice_id in voice.name:
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            self.logger.info("Voice properties updated")
            
        except Exception as e:
            self.logger.error(f"Error setting voice properties: {e}")
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """Get list of available TTS voices"""
        try:
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            
            for voice in voices:
                voice_list.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages
                })
            
            return voice_list
            
        except Exception as e:
            self.logger.error(f"Error getting available voices: {e}")
            return []
    
    def create_voice_shortcut(self, shortcut: str, command: str, description: str = ""):
        """Create a voice shortcut that maps to another command"""
        try:
            if command.lower() in self.voice_commands:
                self.voice_commands[shortcut.lower()] = {
                    'callback': self.voice_commands[command.lower()]['callback'],
                    'description': f"Shortcut for: {description or command}",
                    'added_at': datetime.now()
                }
                self.logger.info(f"Voice shortcut created: {shortcut} -> {command}")
                return True
            else:
                self.logger.error(f"Target command not found: {command}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating voice shortcut: {e}")
            return False
    
    def test_voice_recognition(self, duration: int = 10) -> List[str]:
        """Test voice recognition for a specified duration"""
        try:
            self.logger.info(f"Testing voice recognition for {duration} seconds...")
            recognized_texts = []
            start_time = time.time()
            
            while time.time() - start_time < duration:
                text = self.listen(timeout=1, phrase_time_limit=3)
                if text:
                    recognized_texts.append(text)
                    self.logger.info(f"Recognized: {text}")
            
            self.logger.info(f"Voice recognition test completed. Recognized {len(recognized_texts)} phrases.")
            return recognized_texts
            
        except Exception as e:
            self.logger.error(f"Error testing voice recognition: {e}")
            return []
    
    def create_voice_script(self, script_name: str, commands: List[str]) -> bool:
        """Create a voice script that executes multiple commands in sequence"""
        try:
            def script_callback():
                for command in commands:
                    if command.lower() in self.voice_commands:
                        self.voice_commands[command.lower()]['callback']()
                        time.sleep(0.5)  # Small delay between commands
            
            self.voice_commands[script_name.lower()] = {
                'callback': script_callback,
                'description': f"Script: {' -> '.join(commands)}",
                'added_at': datetime.now()
            }
            
            self.logger.info(f"Voice script created: {script_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating voice script: {e}")
            return False
