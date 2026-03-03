import speech_recognition as sr
import edge_tts
import asyncio
import pygame
import os
import time

class VoiceModule:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        pygame.mixer.init()
        # Türkçe Erkek sesi (Ahmet) veya Kadın sesi (Emel) seçebilirsin
        self.voice_name = "tr-TR-AhmetNeural" 

    def listen(self):
        """Senin sesini duyar ve yazıya döker dayı."""
        with self.microphone as source:
            print("🎤 Dinliyorum dayı...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio, language="tr-TR")
                return text
            except:
                return None

    def speak(self, text):
        """Microsoft Edge'in o efsane sesiyle cevap verir."""
        asyncio.run(self._generate_and_play(text))

    async def _generate_and_play(self, text):
        communicate = edge_tts.Communicate(text, self.voice_name, rate="+10%")
        file_path = "speech.mp3"
        await communicate.save(file_path)
        
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        pygame.mixer.music.unload()
        if os.path.exists(file_path):
            os.remove(file_path)