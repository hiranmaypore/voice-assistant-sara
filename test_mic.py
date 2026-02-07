import sounddevice as sd
import numpy as np

def callback(indata, frames, time, status):
    if status:
        print(status)
    # Print max amplitude and RMS
    peak = np.max(np.abs(indata))
    rms = np.sqrt(np.mean(indata**2))
    print(f"RMS: {int(rms)} | Peak: {int(peak)}", end='\r')

print("🎤 Testing Microphone... (Speak loudly!)")
print("Press Ctrl+C to stop.")

try:
    # Explicitly use device 1 if available, otherwise default
    device_info = sd.query_devices(kind='input')
    print(f"Using device: {device_info['name']}")
    
    with sd.InputStream(callback=callback, channels=1, dtype='int16'):
        while True:
            sd.sleep(100)
except KeyboardInterrupt:
    print("\nStopped.")
except Exception as e:
    print(f"\nError: {e}")
