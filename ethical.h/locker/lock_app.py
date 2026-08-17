"""
lock_app.py - Locker
Author: Melina Sunar

Run this to lock a PDF or image with a password before sending it (e.g. over
WhatsApp). It produces a .locked file. The receiver needs the Unlocker app
(unlock_app.py) plus the same password to get the original file back.
"""

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from locker_core import lock_file

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "Locker_Output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class LockerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Locker")
        self.geometry("420x520")
        self.resizable(False, False)
        self.file_path = None

        ctk.CTkLabel(self, text="🔒 Locker", font=("Segoe UI", 24, "bold")).pack(pady=(30, 5))
        ctk.CTkLabel(
            self,
            text="Lock a PDF or image with a password.\nSend the .locked file - the receiver\nneeds the Unlocker app + same password.",
            font=("Segoe UI", 12),
            text_color="gray70",
            justify="center",
        ).pack(pady=(0, 25))

        self.file_label = ctk.CTkLabel(self, text="No file selected", text_color="gray60")
        self.file_label.pack(pady=5)
        ctk.CTkButton(self, text="Choose File", command=self.choose_file, width=200).pack(pady=8)

        self.pw_entry = ctk.CTkEntry(self, placeholder_text="Set password", show="*", width=280)
        self.pw_entry.pack(pady=(25, 8))
        self.pw_confirm = ctk.CTkEntry(self, placeholder_text="Confirm password", show="*", width=280)
        self.pw_confirm.pack(pady=8)

        self.show_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self, text="Show password", variable=self.show_var, command=self.toggle_show
        ).pack(pady=8)

        self.lock_btn = ctk.CTkButton(
            self, text="Lock File", command=self.start_lock, fg_color="#1f6aa5", width=200, height=38
        )
        self.lock_btn.pack(pady=25)

        self.status = ctk.CTkLabel(self, text="", text_color="gray70", wraplength=360)
        self.status.pack(pady=5)

        ctk.CTkLabel(
            self, text=f"Saves to: {OUTPUT_DIR}", font=("Segoe UI", 9), text_color="gray50"
        ).pack(side="bottom", pady=10)

    def toggle_show(self):
        char = "" if self.show_var.get() else "*"
        self.pw_entry.configure(show=char)
        self.pw_confirm.configure(show=char)

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="Select PDF or Image",
            filetypes=[("Supported files", "*.pdf *.jpg *.jpeg *.png *.bmp *.gif *.webp")],
        )
        if path:
            self.file_path = path
            self.file_label.configure(text=os.path.basename(path), text_color="white")

    def start_lock(self):
        if not self.file_path:
            messagebox.showwarning("No file", "Please choose a PDF or image first.")
            return
        pw = self.pw_entry.get()
        pw2 = self.pw_confirm.get()
        if not pw:
            messagebox.showwarning("No password", "Please set a password.")
            return
        if pw != pw2:
            messagebox.showerror("Mismatch", "Passwords don't match.")
            return

        self.lock_btn.configure(state="disabled", text="Locking...")
        self.status.configure(text="Working...", text_color="gray70")
        threading.Thread(target=self._lock_worker, args=(pw,), daemon=True).start()

    def _lock_worker(self, pw):
        try:
            output_path = lock_file(self.file_path, pw, OUTPUT_DIR)
            self._finish(True, output_path)
        except Exception as e:
            self._finish(False, str(e))

    def _finish(self, success, message):
        def update():
            self.lock_btn.configure(state="normal", text="Lock File")
            if success:
                self.status.configure(text=f"Saved: {os.path.basename(message)}", text_color="#4caf50")
                messagebox.showinfo(
                    "Locked!",
                    f"File locked:\n{message}\n\n"
                    "Send this .locked file over WhatsApp as a DOCUMENT (not a photo), "
                    "so it isn't compressed or altered.\n\n"
                    "Tell the receiver the password separately, and have them run the "
                    "Unlocker app to open it.",
                )
            else:
                self.status.configure(text=f"Error: {message}", text_color="#e53935")
        self.after(0, update)


if __name__ == "__main__":
    app = LockerApp()
    app.mainloop()
