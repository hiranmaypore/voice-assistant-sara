import speech_recognition as sr
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os
import sys

# Add FFmpeg to PATH manually for this session
ffmpeg_path = r"C:\Users\hiran\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] += os.pathsep + ffmpeg_path

def record_audio(filename="input.wav", silence_threshold=0.015, silence_duration=2.0, fs=16000):
    print("🎤 Listening... (Speak now)")
    # print("DEBUG: Active - Waiting for sound...", end='\r')
    
    recording = []
    silent_chunks = 0
    is_recording = False
    
    # Thresholds (Float32)
    # 0.015 is roughly equivalent to 500 in int16
    
    try:
        # Use float32 for better compatibility
        with sd.InputStream(samplerate=fs, channels=1, dtype='float32') as stream:
            
            while True:
                # Read a chunk (4000 samples = 0.25s)
                indata, overflowed = stream.read(4000)
                
                # Fix NaNs if microphone returns garbage
                indata = np.nan_to_num(indata)
                
                # Calculate RMSE (Root Mean Square Energy)
                volume = np.sqrt(np.mean(indata**2))
                
                # Debug print (overwrite line)
                # print(f"DEBUG: Vol: {volume:.4f} | Rec: {is_recording}", end='\r')
                
                if not is_recording:
                    if volume > silence_threshold:
                        print(f"\n🗣️ Started recording... (Vol: {volume:.4f})")
                        is_recording = True
                        
                        # Convert to int16 for saving
                        audio_int16 = (indata * 32767).astype(np.int16)
                        recording.append(audio_int16.copy())
                        silent_chunks = 0
                else:
                    # Capture audio
                    audio_int16 = (indata * 32767).astype(np.int16)
                    recording.append(audio_int16.copy())
                    
                    if volume < silence_threshold:
                        silent_chunks += 1
                    else:
                        silent_chunks = 0
                    
                    # Check silence duration
                    max_silent_chunks = int(silence_duration / 0.25)
                    
                    if silent_chunks > max_silent_chunks:
                        print("\n✅ Silence detected. Stopping.")
                        break
                        
        if len(recording) == 0:
            return False

        # Concatenate and save
        full_recording = np.concatenate(recording, axis=0)
        write(filename, fs, full_recording)
        
        # Check if recording is too short (< 0.5s)
        if len(full_recording) / fs < 0.5:
             print("⚠️ Audio too short, ignoring.")
             return False
             
        print(f"✅ Audio saved ({len(full_recording)/fs:.1f}s)")
        return True

    except Exception as e:
        print(f"\n❌ Error recording audio: {e}")
        return False

def transcribe_audio(filename="input.wav"):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(filename) as source:
            print("📝 Reading audio file...")
            audio_data = recognizer.record(source)
            
        print("☁️ Sending to Google Speech API...")
        # recognize_google uses Google's free API key. It's good for testing.
        text = recognizer.recognize_google(audio_data)
        return {"text": text, "language": "en"}
        
    except sr.UnknownValueError:
        print("❌ Google Speech Recognition could not understand audio")
        return {"text": "", "error": "UnknownValueError"}
    except sr.RequestError as e:
        print(f"❌ Could not request results from Google Speech Recognition service; {e}")
        return {"text": "", "error": f"RequestError: {e}"}
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        return {"text": "", "error": str(e)}

if __name__ == "__main__":
    WAVE_OUTPUT_FILENAME = "input.wav"
    if record_audio(WAVE_OUTPUT_FILENAME):
        res = transcribe_audio(WAVE_OUTPUT_FILENAME)
        print(f"Transcription: {res['text']}")
