"""
WhatsApp Automation via Selenium + WhatsApp Web.

Uses a SINGLE persistent Chrome session:
- First time: scan QR code once
- After that: reuses the same browser window for all calls and messages
- Chrome profile is saved so even after app restart, session persists

Usage:
    from whatsapp_caller import make_call, send_message
    make_call("+919876543210", "voice")
    send_message("+919876543210", "Hello!")
"""

import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Persistent Chrome profile so QR code is scanned only once
CHROME_PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_chrome_profile")


def _kill_orphan_chromes():
    """Kill any Chrome processes using our profile dir (prevents lock conflicts)."""
    try:
        # Only kill chromedriver processes, not user's regular Chrome
        subprocess.run(
            'taskkill /F /IM chromedriver.exe /T',
            shell=True, capture_output=True, timeout=5
        )
    except Exception:
        pass


class WhatsAppBot:
    """Singleton WhatsApp Web controller. Reuses one Chrome session."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.driver = None
        return cls._instance

    def _is_alive(self):
        """Check if the browser session is still alive."""
        if not self.driver:
            return False
        try:
            _ = self.driver.title
            return True
        except Exception:
            return False

    def _ensure_driver(self):
        """Start Chrome if not already running, or reuse existing session."""
        if self._is_alive():
            print("[WHATSAPP] Reusing existing browser session.")
            return

        # Clean up any dead driver reference
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

        # Kill orphaned chromedriver processes that might hold the profile lock
        _kill_orphan_chromes()
        time.sleep(1)

        print("[WHATSAPP] Starting Chrome with persistent profile...")
        options = Options()
        options.add_argument(f"--user-data-dir={CHROME_PROFILE_DIR}")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")
        options.add_experimental_option("detach", True)
        # Prevent "Chrome is controlled by automated software" bar
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def _open_chat(self, phone_no):
        """Navigate to a contact's chat. Waits for WhatsApp Web to load."""
        self._ensure_driver()

        clean_number = phone_no.replace("+", "").replace(" ", "").replace("-", "")
        url = f"https://web.whatsapp.com/send?phone={clean_number}"

        current_url = ""
        try:
            current_url = self.driver.current_url or ""
        except Exception:
            pass

        if "web.whatsapp.com" in current_url:
            print("[WHATSAPP] Switching to chat (already logged in)...")
        else:
            print("[WHATSAPP] Opening WhatsApp Web...")
            print("[WHATSAPP] (First time? Scan the QR code in the browser)")

        self.driver.get(url)

        # Wait for the chat to fully load (up to 90s for first-time QR scan)
        wait = WebDriverWait(self.driver, 90)
        chat_input_selectors = [
            (By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]'),
            (By.CSS_SELECTOR, 'footer div[contenteditable="true"]'),
            (By.CSS_SELECTOR, 'div[title="Type a message"]'),
            (By.CSS_SELECTOR, '[data-testid="conversation-compose-box-input"]'),
        ]

        for by, selector in chat_input_selectors:
            try:
                wait.until(EC.presence_of_element_located((by, selector)))
                print("[WHATSAPP] ✅ Chat loaded!")
                return True
            except Exception:
                continue

        print("[WHATSAPP] ⚠️ Could not confirm chat loaded. Trying anyway...")
        return True

    def make_call(self, phone_no, mode="voice"):
        """
        Make a WhatsApp voice or video call.

        Returns True if call was initiated, False otherwise.
        """
        try:
            print(f"[WHATSAPP] Opening chat for {phone_no}...")
            self._open_chat(phone_no)

            # Wait for all header icons to render
            time.sleep(5)

            # Build comprehensive selector list
            if mode == "video":
                print("[WHATSAPP] Looking for video call button...")
                call_selectors = [
                    # data-testid variants
                    '[data-testid="mi-video-call"]',
                    '[data-testid="video-call"]',
                    '[data-testid="video-call-btn"]',
                    '[data-testid="btn-video-call"]',
                    # data-icon variants
                    'span[data-icon="video-call"]',
                    'span[data-icon="video"]',
                    'span[data-icon="videoCall"]',
                    'span[data-icon="video-camera"]',
                    # aria-label
                    '[aria-label="Video call"]',
                    'button[aria-label="Video call"]',
                    # title
                    '[title="Video call"]',
                    'div[title="Video call"]',
                ]
            else:
                print("[WHATSAPP] Looking for voice call button...")
                call_selectors = [
                    # data-testid variants
                    '[data-testid="mi-audio-call"]',
                    '[data-testid="audio-call"]',
                    '[data-testid="audio-call-btn"]',
                    '[data-testid="btn-audio-call"]',
                    # data-icon variants
                    'span[data-icon="audio-call"]',
                    'span[data-icon="phone"]',
                    'span[data-icon="call"]',
                    'span[data-icon="audioCall"]',
                    # aria-label
                    '[aria-label="Voice call"]',
                    'button[aria-label="Voice call"]',
                    '[aria-label="Audio call"]',
                    # title
                    '[title="Voice call"]',
                    'div[title="Voice call"]',
                ]

            # Try each CSS selector
            for selector in call_selectors:
                try:
                    print(f"[WHATSAPP]   Trying: {selector}")
                    el = self.driver.find_element(By.CSS_SELECTOR, selector)
                    # Try direct click, then parent click
                    try:
                        el.click()
                    except Exception:
                        el.find_element(By.XPATH, "./..").click()

                    print(f"[WHATSAPP] ✅ {mode.capitalize()} call clicked! (via: {selector})")
                    time.sleep(2)
                    self._confirm_dialog()
                    return True
                except Exception:
                    continue

            # Also try XPath-based selectors
            xpath_selectors = [
                f'//*[contains(@aria-label, "{"ideo" if mode == "video" else "oice"}")]',
                f'//*[contains(@data-testid, "{"video" if mode == "video" else "audio"}")]',
                f'//*[contains(@title, "{"Video" if mode == "video" else "Voice"}")]',
            ]
            for xpath in xpath_selectors:
                try:
                    print(f"[WHATSAPP]   Trying XPath: {xpath}")
                    el = self.driver.find_element(By.XPATH, xpath)
                    try:
                        el.click()
                    except Exception:
                        el.find_element(By.XPATH, "./..").click()
                    print(f"[WHATSAPP] ✅ {mode.capitalize()} call clicked! (via XPath)")
                    time.sleep(2)
                    self._confirm_dialog()
                    return True
                except Exception:
                    continue

            # FAILED — dump all elements for debugging
            print(f"\n[WHATSAPP] ❌ Could not find {mode} call button with any selector.")
            self._dump_elements()
            print("[WHATSAPP] Chat is open — please click the call button manually.\n")
            return False

        except Exception as e:
            print(f"[WHATSAPP] Error: {e}")
            return False

    def send_message(self, phone_no, message):
        """Send a WhatsApp message via the same browser session."""
        try:
            print(f"[WHATSAPP] Opening chat for {phone_no}...")
            self._open_chat(phone_no)
            time.sleep(2)

            # Find the message input box
            input_selectors = [
                'div[contenteditable="true"][data-tab="10"]',
                'footer div[contenteditable="true"]',
                '[data-testid="conversation-compose-box-input"]',
            ]

            msg_box = None
            for selector in input_selectors:
                try:
                    msg_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except Exception:
                    continue

            if not msg_box:
                print("[WHATSAPP] ❌ Could not find message input box.")
                return False

            # Type the message
            msg_box.click()
            msg_box.send_keys(message)
            time.sleep(1)

            # Click send button
            send_selectors = [
                'span[data-icon="send"]',
                '[data-testid="send"]',
                'button[aria-label="Send"]',
                '[aria-label="Send"]',
            ]

            for selector in send_selectors:
                try:
                    send_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    send_btn.click()
                    print("[WHATSAPP] ✅ Message sent!")
                    return True
                except Exception:
                    continue

            print("[WHATSAPP] ❌ Could not find send button.")
            return False

        except Exception as e:
            print(f"[WHATSAPP] Error sending: {e}")
            return False

    def _confirm_dialog(self):
        """Try to confirm any call dialog that appears."""
        confirm_selectors = [
            'div[data-animate-modal-popup="true"] button',
            'div[role="dialog"] button',
        ]
        for selector in confirm_selectors:
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                btn.click()
                print("[WHATSAPP] ✅ Call confirmed!")
                return
            except Exception:
                continue
        # Also try XPath
        try:
            btn = self.driver.find_element(By.XPATH, '//button[contains(text(), "Call")]')
            btn.click()
            print("[WHATSAPP] ✅ Call confirmed!")
        except Exception:
            pass

    def _dump_elements(self):
        """Dump all interactive elements for debugging."""
        print("[WHATSAPP] ========== DEBUG: Page Elements ==========")
        try:
            icons = self.driver.execute_script("""
                var results = [];
                document.querySelectorAll('[data-icon], [data-testid], [aria-label], [title]').forEach(function(el) {
                    var obj = {
                        tag: el.tagName,
                        dataIcon: el.getAttribute('data-icon'),
                        dataTestId: el.getAttribute('data-testid'),
                        ariaLabel: el.getAttribute('aria-label'),
                        title: el.getAttribute('title')
                    };
                    // Only include elements with at least one useful attribute
                    if (obj.dataIcon || obj.dataTestId || obj.ariaLabel) {
                        results.push(obj);
                    }
                });
                return results;
            """)
            for icon in icons:
                print(f"  {icon}")
            print(f"[WHATSAPP] Total elements found: {len(icons)}")
        except Exception as e:
            print(f"[WHATSAPP] Could not dump elements: {e}")
        print("[WHATSAPP] ========== END DEBUG ==========")


# Global singleton
bot = WhatsAppBot()


def make_call(phone_no, mode="voice"):
    """Convenience function."""
    return bot.make_call(phone_no, mode)


def send_message(phone_no, message):
    """Convenience function."""
    return bot.send_message(phone_no, message)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        test_phone = sys.argv[1]
        if len(sys.argv) >= 3 and sys.argv[2] in ("voice", "video"):
            print(f"Testing {sys.argv[2]} call to {test_phone}...")
            make_call(test_phone, sys.argv[2])
        elif len(sys.argv) >= 3:
            msg = " ".join(sys.argv[2:])
            print(f"Testing message to {test_phone}: {msg}")
            send_message(test_phone, msg)
        else:
            print(f"Testing voice call to {test_phone}...")
            make_call(test_phone)
    else:
        print("Usage:")
        print("  Call:    python whatsapp_caller.py +919876543210 voice")
        print("  Message: python whatsapp_caller.py +919876543210 Hello there!")
