import os
import sys
import threading
import time
import pyautogui
import webbrowser
import pywhatkit
from datetime import datetime

import json

# --- CONFIGURATION ---
def load_contacts():
    try:
        with open("contacts.json", "r") as f:
            data = json.load(f)
            # Normalize keys to lowercase for easier matching
            return {k.lower(): v for k, v in data.items()}
    except FileNotFoundError:
        print("⚠️ contacts.json not found. Creating empty one.")
        with open("contacts.json", "w") as f:
            json.dump({}, f)
        return {}

CONTACTS = load_contacts()
if CONTACTS:
    print(f"✅ Loaded {len(CONTACTS)} contacts: {', '.join(CONTACTS.keys())}")
else:
    print("⚠️ No contacts found in contacts.json")

# Track opened apps to close them later
OPENED_APPS = []

APP_PROCESS_MAP = {
    "notepad": "notepad.exe",
    "chrome": "chrome.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "excel": "excel.exe",
    "word": "winword.exe",
    "powerpoint": "powerpnt.exe",
    "edge": "msedge.exe",
    "discord": "Agent.exe", # Discord often runs as Agent.exe or discord.exe
    "code": "Code.exe",
    "vscode": "Code.exe",
    "spotify": "Spotify.exe",
    "whatsapp": "WhatsApp.exe"
}

# Ensure we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from full_pipeline import record_audio, transcribe_audio
    from tts_engine import tts
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import modules: {e}")
    sys.exit(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def process_command(text):
    """
    Process a single command text. 
    Handles compound commands by splitting on 'and'.
    """
    if not text:
        return

    # Compound Command Support
    # "Open Notepad and Play Music" -> ["Open Notepad", "Play Music"]
    if " and " in text.lower():
        parts = text.lower().split(" and ")
        for part in parts:
            print(f"[CHAIN] Processing: {part}")
            process_command(part.strip())
        return

    txt_lower = text.lower().strip()
    response_text = ""

    # --- COMMANDS ---

    # STOP COMMAND
    if "stop" in txt_lower and ("listening" in txt_lower or "command" in txt_lower or "program" in txt_lower):
        global IS_LISTENING
        response_text = "Stopping assistant. Goodbye."
        print(f"[AGENT] {response_text}")
        tts.speak(response_text)
        IS_LISTENING = False
        return

    # PLAY COMMAND (YouTube)
    elif "play" in txt_lower:
        song = txt_lower.replace("play", "").strip()
        if song:
            response_text = f"Playing {song} on YouTube"
            print(f"[AGENT] {response_text}")
            tts.speak(response_text)
            pywhatkit.playonyt(song)
        else:
            response_text = "What should I play?"
            tts.speak(response_text)

    # UNIVERSAL OPEN COMMAND
    elif "open" in txt_lower or "start" in txt_lower or "launch" in txt_lower:
        app_name = txt_lower.replace("open", "").replace("start", "").replace("launch", "").strip()
        if app_name:
            response_text = f"Opening {app_name}"
            print(f"[AGENT] {response_text}")
            tts.speak(response_text)
            
            try:
                # Track the app
                # We guess the process name for tracking purposes
                proc_guess = APP_PROCESS_MAP.get(app_name, f"{app_name}.exe")
                if proc_guess not in OPENED_APPS:
                    OPENED_APPS.append(proc_guess)

                pyautogui.press('win')
                time.sleep(0.5)
                pyautogui.write(app_name)
                time.sleep(0.5)
                pyautogui.press('enter')
            except Exception as e:
                    print(f"Error opening app: {e}")
                    tts.speak("I couldn't open that.")
        else:
            response_text = "What should I open?"
            tts.speak(response_text)

    # CLOSE COMMAND
    elif "close" in txt_lower or "exit" in txt_lower or "kill" in txt_lower:
        # 1. Close Active Window
        if "this" in txt_lower or "that" in txt_lower or "current" in txt_lower or "window" in txt_lower:
            response_text = "Closing current window"
            print(f"[AGENT] {response_text}")
            tts.speak(response_text)
            pyautogui.hotkey('alt', 'f4')
            
        # 2. Close All Opened Apps (Cleanup)
        elif "everything" in txt_lower or "all" in txt_lower:
             if OPENED_APPS:
                 response_text = f"Closing {len(OPENED_APPS)} apps I opened."
                 print(f"[AGENT] {response_text}")
                 tts.speak(response_text)
                 for proc in OPENED_APPS:
                     print(f"Killing {proc}")
                     os.system(f"taskkill /f /im {proc}")
                 OPENED_APPS.clear()
             else:
                 tts.speak("I haven't opened any apps to close.")

        else:
            # 3. Close Specific App by Name
            app_name = txt_lower.replace("close", "").replace("exit", "").replace("kill", "").replace("the", "").strip()
            
            if app_name:
                proc_name = APP_PROCESS_MAP.get(app_name, f"{app_name}.exe")
                
                response_text = f"Closing {app_name}"
                print(f"[AGENT] {response_text} (Process: {proc_name})")
                tts.speak(response_text)
                
                os.system(f"taskkill /f /im {proc_name}")
                
            else:
                response_text = "What should I close?"
                print(f"[AGENT] {response_text}")
                tts.speak(response_text)

    # TYPE COMMAND
    elif "type" in txt_lower:
        if len(text) > 5:
            content_to_type = text[4:].strip()
            if content_to_type:
                response_text = f"Typing: {content_to_type}"
                print(f"[AGENT] {response_text}")
                tts.speak("Typing")
                pyautogui.write(content_to_type, interval=0.05)

    # SEARCH COMMAND
    elif "search" in txt_lower or "google" in txt_lower:
        query = text.replace("search", "").replace("google", "").replace("for", "").strip()
        if query:
            response_text = f"Searching for {query}"
            print(f"[AGENT] {response_text}")
            tts.speak(response_text)
            webbrowser.open(f"https://www.google.com/search?q={query}")

    # TIME/DATE
    elif "time" in txt_lower:
        current_time = datetime.now().strftime("%I:%M %p")
        response_text = f"The time is {current_time}"
        print(f"[AGENT] {response_text}")
        tts.speak(response_text)

    elif "date" in txt_lower:
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        response_text = f"Today is {current_date}"
        print(f"[AGENT] {response_text}")
        tts.speak(response_text)
    
    # GREETING/CHAT
    elif "hello" in txt_lower:
        response_text = "Hello! I am ready."
        print(f"[AGENT] {response_text}")
        tts.speak(response_text)
    
        # Echo valid sentences
        if len(text.split()) > 2:
                print(f"[AGENT] Heard: {text}")
                tts.speak(text)

    # WHATSAPP CALLING
    elif "call" in txt_lower:
        # "Call mom"  /  "Call mom on whatsapp"  /  "Video call dad"
        try:
             import re
             from whatsapp_caller import make_call
             match = re.search(r"call (\w+)", txt_lower)
             if match:
                 name = match.group(1).lower()
                 if name in CONTACTS:
                     phone_no = CONTACTS[name]
                     
                     if not phone_no:
                         tts.speak(f"I have {name} in contacts but no phone number saved.")
                         return
                     
                     mode = "voice"
                     if "video" in txt_lower:
                         mode = "video"
                         
                     response_text = f"Starting WhatsApp {mode} call with {name}..."
                     print(f"[AGENT] {response_text}")
                     tts.speak(response_text)
                     
                     # Use Selenium-based WhatsApp Web caller
                     success = make_call(phone_no, mode)
                     
                     if success:
                         tts.speak(f"{mode.capitalize()} call started with {name}.")
                     else:
                         tts.speak(f"Could not start the call. Please check the browser window.")
                     
                 else:
                     tts.speak(f"I don't have a number for {name}.")
             else:
                 tts.speak("Who should I call?")
        except Exception as e:
            print(f"Error calling: {e}")
            tts.speak("I couldn't start the call.")

    # WHATSAPP MESSAGE
    elif "send" in txt_lower and ("message" in txt_lower or "to" in txt_lower):
        # "Send a message to mom saying hello"
        # "Send message to mom saying I'll be late"
        try:
            import re
            match = re.search(r"to (\w+)", txt_lower)
            if match:
                name = match.group(1).lower()
                
                if name in CONTACTS:
                    phone_no = CONTACTS[name]
                    
                    if not phone_no:
                        tts.speak(f"I have {name} in contacts but no phone number saved.")
                        return
                    
                    # Extract Message
                    msg_match = re.search(r"(saying|message|that) (.+)", txt_lower)
                    if msg_match:
                        message = msg_match.group(2).strip()
                        
                        response_text = f"Sending message to {name}: {message}"
                        print(f"[AGENT] {response_text}")
                        tts.speak(response_text)
                        
                        # Use same Selenium session as calls (no re-login)
                        from whatsapp_caller import send_message
                        success = send_message(phone_no, message)
                        if success:
                            tts.speak("Message sent!")
                        else:
                            tts.speak("Could not send the message. Check the browser.")
                        
                    else:
                        response_text = "What should I say?"
                        print(f"[AGENT] {response_text}")
                        tts.speak(response_text)
                else:
                    response_text = f"I don't have a number for {name}. Please add them to my contacts."
                    print(f"[AGENT] {response_text}")
                    tts.speak(response_text)
            else:
                response_text = "To whom should I send the message?"
                print(f"[AGENT] {response_text}")
                tts.speak(response_text)

        except Exception as e:
            print(f"Error sending WhatsApp: {e}")
            tts.speak("I couldn't send the message.")

    # SOCIAL MEDIA POSTING (Web Automation)
    elif "post" in txt_lower:
        # "Post on Twitter saying Hello World"
        # "Tweet saying I am learning AI"
        
        platform = None
        if "twitter" in txt_lower or "tweet" in txt_lower or "x" in txt_lower:
            platform = "twitter"
        elif "linkedin" in txt_lower:
            platform = "linkedin"
        elif "facebook" in txt_lower:
            platform = "facebook"
        elif "instagram" in txt_lower or "insta" in txt_lower:
            platform = "instagram"
        elif "youtube" in txt_lower:
            platform = "youtube"

        if platform:
            # Extract content
            import re
            msg_match = re.search(r"(saying|that|content) (.+)", txt_lower)
            if msg_match:
                content = msg_match.group(2).strip()
                
                if platform == "twitter":
                    response_text = f"Drafting Tweet: {content}"
                    print(f"[AGENT] {response_text}")
                    tts.speak(response_text)
                    # Open Compose Window
                    webbrowser.open(f"https://twitter.com/intent/tweet?text={content}")
                    # We leave it to the user to click "Post" to be safe
                    
                elif platform == "linkedin":
                    response_text = f"Opening LinkedIn to post: {content}"
                    print(f"[AGENT] {response_text}")
                    tts.speak(response_text)
                    # Open Feed
                    import pyperclip
                    pyperclip.copy(content)
                    webbrowser.open("https://www.linkedin.com/feed/")
                    tts.speak("I copied the text. Paste it to post.")

                elif platform == "facebook":
                    response_text = f"Opening Facebook to post: {content}"
                    print(f"[AGENT] {response_text}")
                    tts.speak(response_text)
                    import pyperclip
                    pyperclip.copy(content)
                    webbrowser.open("https://www.facebook.com/")
                    tts.speak("I copied the text. Paste it to post.")

                elif platform == "instagram":
                    response_text = f"Opening Instagram to post: {content}"
                    print(f"[AGENT] {response_text}")
                    tts.speak(response_text)
                    import pyperclip
                    pyperclip.copy(content)
                    webbrowser.open("https://www.instagram.com/")
                    tts.speak("I copied the text. Paste it to post.")

                elif platform == "youtube":
                    response_text = "Opening YouTube Studio"
                    tts.speak(response_text)
                    webbrowser.open("https://studio.youtube.com/")
            else:
                response_text = f"What should I post on {platform}?"
                tts.speak(response_text)
        else:
             response_text = "Which platform? Twitter, LinkedIn, or YouTube?"
             tts.speak(response_text)


IS_LISTENING = True

def main():
    clear_screen()
    print("=================================================")
    print("   AI Voice Assistant - Terminal Mode (VAD)")
    print("=================================================")
    print("Initializing...")
    tts.speak("Hi Hiranmay, I'm Sara, your personal assistant. I'm ready for commands.")
    
    global IS_LISTENING
    
    while IS_LISTENING:
        print("\n[LISTENING] Waiting for speech...")
        
        # 1. Record (Dynamic VAD)
        # Using float32 aware record_audio from full_pipeline
        WAVE_OUTPUT_FILENAME = "temp_command.wav"
        success = record_audio(WAVE_OUTPUT_FILENAME)
        
        if success:
            print("[PROCESSING] Transcribing...")
            
            # 2. Transcribe
            result = transcribe_audio(WAVE_OUTPUT_FILENAME)
            text = result.get("text", "").strip()
            error = result.get("error", None)

            # Filter hallucinations
            cleanup_text = text.lower().strip()
            if not text or len(text) < 2 or cleanup_text in ["you", "thank you", "stop", "mb", "you."]:
                if cleanup_text not in ["stop", "time", "date", "help"]:
                    print(f"[IGNORED] Hallucination/Noise: '{text}'")
                    continue

            if error:
                print(f"[ERROR] {error}")
            else:
                print(f"[USER] {text}")
                # 3. Process Command (Recursive for compound)
                process_command(text)
                
        else:
             # Silence
             pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Exiting...")
        sys.exit(0)
