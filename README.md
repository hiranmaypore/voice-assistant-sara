# Sara - Advanced AI Voice Assistant 🎙️

Sara is a powerful, terminal-based voice assistant built with Python. It uses **Google Speech Recognition API** for high-accuracy voice transcription and **pyttsx3** for offline text-to-speech responses.

## 🚀 Features

### 🗣️ Core Capabilities

- **Voice Activity Detection (VAD)**: Automatically starts/stops recording based on speech detection
- **High Accuracy Speech Recognition**: Powered by Google Speech Recognition API
- **Smart Noise Filtering**: Filters out background noise and speech recognition hallucinations
- **Compound Command Support**: Execute multiple commands at once ("Open Notepad and play music")
- **Continuous Listening Mode**: Always active until you say "Stop listening"

### 📱 WhatsApp Integration (Selenium-based)

- **Send Messages**: "Send a message to [Name] saying [Message]"
- **Voice Calls**: "Call [Name]" or "Call [Name] on WhatsApp"
- **Video Calls**: "Video call [Name]"
- **Persistent Session**: QR code scan only once - Chrome profile is saved for future use
- **Single Browser Instance**: All WhatsApp operations reuse the same browser window

### 🎵 Media & Entertainment

- **YouTube Playback**: "Play [Song Name]" - Instantly plays on YouTube
- **Social Media Posting**:
  - **Twitter/X**: "Post on Twitter saying [Message]" (Opens pre-filled tweet composer)
  - **LinkedIn**: "Post on LinkedIn saying [Message]" (Copies text, opens LinkedIn)
  - **Facebook**: "Post on Facebook saying [Message]" (Copies text, opens Facebook)
  - **Instagram**: "Post on Instagram saying [Message]" (Copies text, opens Instagram)
  - **YouTube**: "Post on YouTube" (Opens YouTube Studio)

### 💻 System Control & Automation

- **App Launcher**: "Open [App]", "Start [App]", "Launch [App]"
  - Supports: Notepad, Chrome, Calculator, Excel, Word, PowerPoint, Edge, Discord, VS Code, Spotify, WhatsApp, and more
- **Smart App Closing**:
  - Close active window: "Close this window"
  - Close specific app: "Close [App Name]"
  - Close all opened apps: "Close everything you opened"
- **Keyboard Automation**: "Type [Text]" - Types text automatically
- **Web Search**: "Search for [Topic]" - Opens Google search
- **Utilities**: 
  - Current time: "What time is it?"
  - Current date: "What's the date?"

---

## 🛠️ Installation & Setup

### 1. Prerequisites

- **Python 3.8+**
- **Microphone** (for voice input)
- **Internet Connection** (required for Google Speech Recognition API and WhatsApp Web)
- **Google Chrome** (for WhatsApp automation via Selenium)

### 2. Clone & Install Dependencies

```bash
git clone https://github.com/hiranmaypore/voice-assistant-sara.git
cd voice-assistant-sara

# Optional: Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment:
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# Install all required packages
pip install -r requirements.txt
```

### 3. Configure Contacts (Required for WhatsApp) 📞

WhatsApp features require a `contacts.json` file with your contacts.

1. Create a file named `contacts.json` in the project root directory
2. Add contacts in this format:
   ```json
   {
     "mom": "+919876543210",
     "dad": "+919876543211",
     "best friend": "+15551234567",
     "john": "+14155551234"
   }
   ```
   - Keys should be lowercase names (how you'll refer to them)
   - Values must be full phone numbers with country code (e.g., +91 for India, +1 for USA)

**Note**: `contacts.json` is gitignored for privacy protection.

### 4. WhatsApp Setup (First-Time Only)

1. Run the assistant for the first time
2. When you make your first WhatsApp call/message, Chrome will open WhatsApp Web
3. **Scan the QR code** with your phone (WhatsApp > Settings > Linked Devices)
4. The session is saved in `whatsapp_chrome_profile/` - you won't need to scan again!

---

## 🎮 Usage

### Starting Sara

```powershell
python main.py
```

Sara will greet you and start listening continuously. Speak naturally and she'll respond!

### Command Examples

#### Basic Commands
- **Greeting**: "Hello"
- **Stop Assistant**: "Stop listening" (exits the program)
- **Time**: "What time is it?"
- **Date**: "What's the date?"

#### System Control
- **Open Apps**: 
  - "Open Notepad"
  - "Launch Chrome"
  - "Start Spotify"
- **Close Apps**:
  - "Close Chrome"
  - "Close everything you opened"
  - "Close this window" (closes active window)

#### Automation
- **Type Text**: "Type Hello World"
- **Search Web**: "Search for Python tutorials"
- **Compound Commands**: "Open Notepad and type Hello World"

#### Media & Entertainment
- **Play Music**: "Play Blinding Lights"
- **Social Media**:
  - "Post on Twitter saying Just finished my AI project"
  - "Post on LinkedIn saying Excited to share my new project"

#### WhatsApp (requires `contacts.json` setup)
- **Send Message**: 
  - "Send a message to Mom saying I'll be late"
  - "Send message to John saying Meeting at 5"
- **Voice Call**: "Call Dad on WhatsApp"
- **Video Call**: "Video call Best Friend"

### Advanced: Compound Commands

Sara can handle multiple commands in one sentence using "and":

```
"Open Notepad and type Hello World"
"Play Lo-fi music and open Chrome"
"Close Chrome and open Spotify"
```

---

## 🧩 Project Structure

```
voice-assistant-sara/
│
├── main.py                    # Main entry point, command processing logic
├── full_pipeline.py           # VAD audio recording + Google Speech Recognition
├── tts_engine.py              # Text-to-speech engine (pyttsx3)
├── whatsapp_caller.py         # WhatsApp automation via Selenium
│
├── contacts.json              # Your contacts (created by user, gitignored)
├── requirements.txt           # Python dependencies
│
├── test_mic.py                # Test microphone recording
├── test_whisper.py            # Whisper model testing (experimental)
├── record_mic.py              # Standalone audio recording utility
│
├── whatsapp_chrome_profile/   # Persistent Chrome session data (gitignored)
└── __pycache__/               # Python cache
```

### Key Files

- **`main.py`**: Command router and business logic for all features
- **`full_pipeline.py`**: 
  - Voice Activity Detection (VAD) using sounddevice
  - Audio recording with automatic silence detection
  - Speech-to-text using Google Speech Recognition API
- **`tts_engine.py`**: Thread-safe text-to-speech responses
- **`whatsapp_caller.py`**: 
  - Selenium-based WhatsApp Web automation
  - Persistent Chrome session (scan QR code once)
  - Make voice/video calls and send messages
- **`contacts.json`**: User-defined contact mappings (name → phone number)

---

## 🔧 Technical Details

### Dependencies

- **speechrecognition**: Google Speech Recognition API integration
- **sounddevice + scipy**: Real-time audio recording with VAD
- **pyttsx3**: Offline text-to-speech engine
- **selenium + webdriver-manager**: Browser automation for WhatsApp
- **pywhatkit**: YouTube playback
- **pyautogui**: Keyboard/mouse automation
- **pyperclip**: Clipboard management (for social media posting)

### How Voice Activity Detection Works

Sara uses dynamic Voice Activity Detection to eliminate manual recording controls:

1. **Listening Phase**: Monitors microphone for sound above threshold (`0.015` RMS)
2. **Recording Phase**: Captures audio once speech is detected
3. **Silence Detection**: Stops after 2 seconds of silence
4. **Validation**: Rejects recordings shorter than 0.5 seconds

This creates a natural, hands-free experience without wake words.

### WhatsApp Automation Architecture

- Uses **Selenium WebDriver** with persistent Chrome profile
- First run: QR code scan required (one-time setup)
- Subsequent runs: Reuses existing session (no re-login)
- All operations (calls + messages) share the same browser instance
- Profile stored in `whatsapp_chrome_profile/`

---

## 🧪 Testing & Development

### Test Microphone
```bash
python test_mic.py
```

### Test Audio Recording Pipeline
```bash
python record_mic.py
```

### Test Whisper Model (Experimental)
```bash
python test_whisper.py
```

---

## 🐛 Troubleshooting

### "No module named 'full_pipeline'"
- Ensure you're running from the project root directory
- Check that all files are in the correct location

### Microphone not detected
- Check system microphone permissions
- Try `python test_mic.py` to diagnose

### WhatsApp scan required every time
- Chrome may be closing unexpectedly
- Check that `whatsapp_chrome_profile/` directory exists and has write permissions
- Don't manually close the Chrome window - let Sara manage it

### Google Speech Recognition errors
- Ensure stable internet connection
- API may have rate limits - wait a moment and try again

### TTS not working
- pyttsx3 uses system TTS engines
- Windows: Should work out of the box
- Linux: May need `espeak` (`sudo apt install espeak`)
- Mac: Should work with built-in voices

---

## 🛣️ Roadmap

- [ ] Local speech recognition (offline Whisper integration)
- [ ] Custom wake word detection
- [ ] Spotify integration for music control
- [ ] Email automation
- [ ] Calendar management
- [ ] Smart home device control
- [ ] Conversation context memory

---

## �️ Roadmap

- [ ] Local speech recognition (offline Whisper integration)
- [ ] Custom wake word detection
- [ ] Spotify integration for music control
- [ ] Email automation
- [ ] Calendar management
- [ ] Smart home device control
- [ ] Conversation context memory

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Contribution
- Additional command processors
- Integration with more services (Spotify, Gmail, Calendar)
- Better error handling and user feedback
- Cross-platform compatibility improvements
- Testing and bug fixes

---

## 📝 License

This project is licensed under the **MIT License** - see below for details:

```
MIT License

Copyright (c) 2026 Hiranmay Pore

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👤 Author

**Hiranmay Pore**
- GitHub: [@hiranmaypore](https://github.com/hiranmaypore)
- Repository: [voice-assistant-sara](https://github.com/hiranmaypore/voice-assistant-sara)

---

## 🙏 Acknowledgments

- **Google Speech Recognition API** - High-quality speech-to-text
- **pyttsx3** - Offline text-to-speech engine
- **Selenium** - Browser automation framework
- **PyWhatKit** - YouTube playback utility
- All open-source contributors whose libraries made this project possible

---

## ⭐ Show Your Support

If you found Sara helpful, give this project a ⭐ on GitHub!

---

**Built with ❤️ by Hiranmay Pore**
