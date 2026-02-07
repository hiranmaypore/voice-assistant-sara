import pyttsx3
import threading

class TTSEngine:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            # Try to set properties (might fail on some systems)
            try:
                self.engine.setProperty('rate', 150)
                self.engine.setProperty('volume', 0.9)
                
                # Try to pick a female/better voice
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if "zira" in voice.name.lower() or "female" in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            except Exception:
                pass 
                
        except Exception as e:
            print(f"TTS Init Error: {e}")
            self.engine = None

    def speak(self, text):
        if not text:
            return

        def _speak_thread():
            try:
                # Create a new engine instance per thread if the global one is busy/stuck
                # This is safer for concurrency in simple scripts
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.say(text)
                engine.runAndWait()
                # self.engine.say(text)
                # self.engine.runAndWait() 
            except Exception as e:
                # print(f"TTS Error: {e}")
                # Fallback to console
                print(f"[SILENT MODE] Agent: {text}")

        # Run in a thread so functionality doesn't block
        threading.Thread(target=_speak_thread, daemon=True).start()

# Global instance
tts = TTSEngine()

if __name__ == "__main__":
    tts.speak("Hi Hiranmay, I'm Sara, your personal assistant. I'm ready for commands.")
    import time
    time.sleep(8)
