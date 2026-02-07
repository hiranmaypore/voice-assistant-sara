# Sara - Advanced AI Voice Assistant 🎙️

Sara is a powerful, terminal-based voice assistant built with Python. It uses **Google Speech Recognition** for high accuracy and **pyttsx3** for offline text-to-speech.

## 🚀 Features

### 🗣️ Core Capabilities

- **Voice Activation**: Continuous listening with Voice Activity Detection (VAD).
- **High Accuracy**: Uses Google Speech Recognition API.
- **Smart Errors**: Handles silence and background noise gracefully.

### 📱 App Integrations

- **WhatsApp**:
  - "Send a message to [Name] saying [Message]"
  - "Call [Name] on WhatsApp" (Voice Call)
  - "Video call [Name] on WhatsApp"
- **Social Media Automation**:
  - **Twitter/X**: "Post on Twitter saying [Message]" (Opens pre-filled tweet)
  - **LinkedIn/Facebook/Instagram**: "Post on Facebook..." (Copies text to clipboard & opens site)
  - **YouTube**: "Post on YouTube" (Opens Studio)
- **YouTube Music**: "Play [Song Name]" (Plays instantly on YouTube)

### 💻 System Control

- **App Launcher**: "Open Notepad", "Open Chrome", "Start Spotify".
- **Smart Closing**: "Close Notepad", "Close everything you opened".
- **Type Mode**: "Type [Text]" (Types for you).
- **Search**: "Search for [Topic]" (Google Search).
- **Utilities**: Time, Date, Volume Control.

---

## 🛠️ Installation & Setup

### 1. Requirements

- Python 3.8+
- Microphone
- Active Internet Connection (for Google Speech & WhatsApp)

### 2. Install Dependencies

```bash
git clone https://github.com/hiranmaypore/voice-assistant-sara.git
cd voice-assistant-sara
python -m venv .venv
# Activate venv:
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Contacts (Important!) 📞

To use WhatsApp features, you must add your contacts to `contacts.json`.

1.  Create a file named `contacts.json` in the root folder (if not exists).
2.  Add your contacts in this format:
    ```json
    {
      "mom": "+919876543210",
      "best friend": "+15551234567"
    }
    ```
    _(Note: This file is ignored by Git for privacy)._

---

## 🎮 Usage

Run the assistant:

```powershell
python main.py
```

### Examples

> "Open Notepad and type Hello World"
> "Play Blinding Lights on YouTube"
> "Open WhatsApp and send a message to Mom saying I will be late"
> "Call Best Friend on WhatsApp"
> "Close everything you opened"
> "Stop listening"

---

## 🧩 Project Structure

- `main.py`: Main entry point and command processor.
- `full_pipeline.py`: Handles Audio Recording & Speech-to-Text (STT).
- `tts_engine.py`: Handles Text-to-Speech (TTS).
- `contacts.json`: User contacts (Local only).

## 📄 License

MIT License. Feel free to modify and use!
