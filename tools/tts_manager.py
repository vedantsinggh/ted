import pyttsx3
import threading
import queue
import time

class TTSManager:
    def __init__(self):
        self.engine = None
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.enabled = True
        self._init_engine()
        
    def _init_engine(self):
        """Initialize the TTS engine with pleasant settings"""
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice settings
            voices = self.engine.getProperty('voices')
            
            # Prefer female voice if available, it often sounds more natural for assistants
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
                elif 'david' in voice.name.lower():  # Fallback to a male voice
                    self.engine.setProperty('voice', voice.id)
            
            # Set speech properties
            self.engine.setProperty('rate', 160)    # Slightly slower than default
            self.engine.setProperty('volume', 0.8)  # Slightly lower volume
            self.engine.setProperty('pitch', 110)   # Slightly higher pitch
            
            print(f"🔊 TTS Ready - Voice: {self.engine.getProperty('voice')}")
            
        except Exception as e:
            print(f"⚠️  TTS initialization failed: {e}")
            self.enabled = False
    
    def speak(self, text: str):
        """Add text to speech queue"""
        if not self.enabled or not text.strip():
            return
            
        # Clean the text - remove any markdown, extra spaces
        clean_text = self._clean_text(text)
        
        # Add to queue
        self.speech_queue.put(clean_text)
        
        # Start processing if not already running
        if not self.is_speaking:
            self._start_processing()
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better TTS"""
        # Remove common AI response artifacts
        replacements = {
            '**': '',
            '*': '',
            '#': '',
            '[': '',
            ']': '',
            '(': '',
            ')': '',
            '  ': ' '
        }
        
        clean = text
        for old, new in replacements.items():
            clean = clean.replace(old, new)
        
        # Limit length for TTS
        if len(clean) > 200:
            sentences = clean.split('.')
            if len(sentences) > 2:
                clean = '.'.join(sentences[:2]) + '.'
        
        return clean.strip()
    
    def _start_processing(self):
        """Start processing the speech queue in a separate thread"""
        def process_queue():
            self.is_speaking = True
            while not self.speech_queue.empty():
                try:
                    text = self.speech_queue.get_nowait()
                    if self.engine:
                        self.engine.say(text)
                        self.engine.runAndWait()
                    time.sleep(0.1)  # Small pause between utterances
                except Exception as e:
                    print(f"TTS Error: {e}")
                    break
            self.is_speaking = False
        
        # Run in background thread to not block main execution
        thread = threading.Thread(target=process_queue, daemon=True)
        thread.start()
    
    def stop(self):
        """Stop any ongoing speech"""
        if self.engine:
            self.engine.stop()
    
    def toggle(self):
        """Toggle TTS on/off"""
        self.enabled = not self.enabled
        status = "ON" if self.enabled else "OFF"
        print(f"🔊 TTS {status}")
        return self.enabled

# Global TTS instance
tts = TTSManager()
