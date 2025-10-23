import torch
from TTS.api import TTS
import threading
import queue
import tempfile
import os
import time
import pygame
import requests

class NaturalTTS:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🚀 Using device: {self.device}")
        
        self.tts = None
        self.speech_queue = queue.Queue()
        self.is_processing = False
        self.enabled = True
        
        # Initialize pygame for audio playback
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        
        self._init_tts_engine()
    
    def _init_tts_engine(self):
        """Initialize TTS engine with models that don't require speaker reference"""
        try:
            print("📦 Loading AI TTS model...")
            
            # Try models in order of preference (ones that don't need speaker_wav)
            models_to_try = [
                "tts_models/en/ljspeech/fast_pitch",     # Fast, good quality
                "tts_models/en/ljspeech/tacotron2-DDC",  # Good quality, no speaker needed
                "tts_models/en/ljspeech/glow-tts",       # Very natural
                "tts_models/en/vctk/vits",               # Multiple voices
                "tts_models/en/ek1/tacotron2"           # Another option
            ]
            
            for model_name in models_to_try:
                try:
                    print(f"🔄 Trying {model_name}...")
                    self.tts = TTS(model_name).to(self.device)
                    self.model_type = model_name
                    print(f"✅ Loaded: {model_name}")
                    
                    # Test the TTS
                    test_text = "Hello, I am your AI assistant."
                    print("🔊 Testing TTS...")
                    self._speak_immediate(test_text)
                    return
                    
                except Exception as e:
                    print(f"❌ {model_name} failed: {e}")
                    continue
            
            # If all models fail, try XTTS with a default speaker
            print("🔄 Trying XTTS with default speaker...")
            self._init_xtts_with_default_speaker()
            
        except Exception as e:
            print(f"❌ All AI TTS models failed: {e}")
            print("🔄 Falling back to pyttsx3...")
            self._init_fallback()
    
    def _init_xtts_with_default_speaker(self):
        """Initialize XTTS with a default speaker sample"""
        try:
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            self.model_type = "xtts_v2"
            
            # Create or download a default speaker reference
            self.default_speaker_path = self._get_default_speaker()
            print("✅ XTTS v2 loaded with default speaker")
            
        except Exception as e:
            print(f"❌ XTTS v2 failed: {e}")
            raise e
    
    def _get_default_speaker(self):
        """Get or create a default speaker reference file"""
        default_speaker_path = "default_speaker.wav"
        
        if not os.path.exists(default_speaker_path):
            print("📥 Creating default speaker reference...")
            # Create a simple default speaker using another TTS model
            try:
                # Use a simple model to generate reference audio
                temp_tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")
                reference_text = "Hello, this is my default voice."
                temp_tts.tts_to_file(text=reference_text, file_path=default_speaker_path)
                print("✅ Default speaker created")
            except:
                # If that fails, download a sample
                print("📥 Downloading speaker sample...")
                self._download_speaker_sample(default_speaker_path)
        
        return default_speaker_path
    
    def _download_speaker_sample(self, path: str):
        """Download a sample speaker audio file"""
        try:
            # You can replace this URL with any short WAV file of a clear speaker
            sample_url = "https://www2.cs.uic.edu/~i101/SoundFiles/taunt.wav"
            response = requests.get(sample_url, timeout=30)
            with open(path, 'wb') as f:
                f.write(response.content)
            print("✅ Speaker sample downloaded")
        except:
            # Create a silent WAV file as last resort
            import wave
            import struct
            with wave.open(path, 'w') as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(22050)
                # 0.5 seconds of silence
                frames = b''.join([struct.pack('<h', 0) for _ in range(11025)])
                f.writeframes(frames)
            print("⚠️ Created silent speaker reference")
    
    def _init_fallback(self):
        """Fallback to basic TTS if AI models fail"""
        try:
            import pyttsx3
            self.fallback_tts = pyttsx3.init()
            # Configure fallback for better sound
            voices = self.fallback_tts.getProperty('voices')
            for voice in voices:
                if 'female' in voice.name.lower():
                    self.fallback_tts.setProperty('voice', voice.id)
                    break
            self.fallback_tts.setProperty('rate', 145)
            self.fallback_tts.setProperty('volume', 0.9)
            self.model_type = "fallback"
            print("✅ Using pyttsx3 fallback")
        except Exception as e:
            print(f"❌ No TTS available: {e}")
            self.enabled = False
    
    def speak(self, text: str):
        """Add text to speech queue"""
        if not self.enabled or not text.strip():
            return
            
        clean_text = self._clean_text(text)
        
        # Add to queue
        self.speech_queue.put(clean_text)
        
        # Start processing if not already running
        if not self.is_processing:
            self._start_processing()
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better TTS"""
        import re
        
        # Remove markdown and special characters
        text = re.sub(r'[**#\[\](){}]', '', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common TTS issues
        replacements = {
            '...': '.',
            '..': '.',
            ' .': '.',
            ' ,': ',',
            ' ?': '?',
            ' !': '!'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Limit length for TTS
        if len(text) > 250:
            sentences = text.split('.')
            if len(sentences) > 2:
                text = '. '.join(sentences[:2]) + '.'
        
        return text.strip()
    
    def _start_processing(self):
        """Start processing the speech queue in a separate thread"""
        def process_queue():
            self.is_processing = True
            while not self.speech_queue.empty():
                try:
                    text = self.speech_queue.get_nowait()
                    if text:
                        self._synthesize_and_play(text)
                    time.sleep(0.1)  # Small pause between utterances
                except Exception as e:
                    print(f"TTS Error: {e}")
                    break
            self.is_processing = False
        
        # Run in background thread
        thread = threading.Thread(target=process_queue, daemon=True)
        thread.start()
    
    def _synthesize_and_play(self, text: str):
        """Synthesize and play speech using AI model"""
        try:
            print(f"🗣️ AI Speaking: {text}")
            
            if self.model_type == "fallback":
                # Use fallback TTS
                self.fallback_tts.say(text)
                self.fallback_tts.runAndWait()
                return
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech with appropriate method
            if self.model_type == "xtts_v2" and hasattr(self, 'default_speaker_path'):
                # XTTS v2 with default speaker
                self.tts.tts_to_file(
                    text=text,
                    file_path=temp_path,
                    speaker_wav=self.default_speaker_path,
                    language="en"
                )
            else:
                # Other models that don't need speaker reference
                self.tts.tts_to_file(text=text, file_path=temp_path)
            
            # Play the audio
            self._play_audio_file(temp_path)
            
            # Clean up
            os.unlink(temp_path)
            
        except Exception as e:
            print(f"❌ AI TTS synthesis failed: {e}")
            # Fallback to basic TTS if AI fails
            if hasattr(self, 'fallback_tts'):
                print("🔄 Using fallback TTS...")
                self.fallback_tts.say(text)
                self.fallback_tts.runAndWait()
    
    def _play_audio_file(self, file_path: str):
        """Play audio file using pygame"""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
    
    def _speak_immediate(self, text: str):
        """For testing - speak immediately without queue"""
        self._synthesize_and_play(text)
    
    def stop(self):
        """Stop any ongoing speech"""
        try:
            pygame.mixer.music.stop()
            if hasattr(self, 'fallback_tts'):
                self.fallback_tts.stop()
        except:
            pass
    
    def toggle(self):
        """Toggle TTS on/off"""
        self.enabled = not self.enabled
        status = "ON" if self.enabled else "OFF"
        print(f"🔊 TTS {status}")
        return self.enabled

# Global TTS instance
tts = NaturalTTS()
