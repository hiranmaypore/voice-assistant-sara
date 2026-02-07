import whisper

def test_whisper():
    print("Testing Whisper installation...")
    try:
        # Load the base model - this will download it if not present
        print("Loading 'base' model (this might take a while first time)...")
        model = whisper.load_model("base")
        print("✅ Whisper model loaded successfully!")
        
        # Test basic availability
        print("Whisper is ready to transcribe.")
        
    except Exception as e:
        print(f"❌ Error loading Whisper: {e}")

if __name__ == "__main__":
    test_whisper()
