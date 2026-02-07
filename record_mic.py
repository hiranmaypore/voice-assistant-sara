import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

def record_audio(filename="input.wav", duration=5, fs=16000):
    print(f"🎤 Recording for {duration} seconds...")
    try:
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  # Wait until recording is finished
        write(filename, fs, recording)
        print(f"✅ Audio saved to {filename}")
    except Exception as e:
        print(f"❌ Error recording audio: {e}")

if __name__ == "__main__":
    record_audio()
