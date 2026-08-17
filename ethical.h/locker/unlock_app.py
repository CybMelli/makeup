"""
unlock_app.py - Unlocker
Author: Melina Sunar

This is the small program the RECEIVER runs. It only needs locker_core.py
and the `cryptography` library (pip install cryptography) - no
customtkinter needed, so it's quick for someone else to set up just to
open one locked file.

Usage: pick the .locked file you were sent, type in the password you were
given, and it saves the original file back to your Desktop.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

from locker_core import unlock_file

OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "Unlocked_Files")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class UnlockerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Unlocker")
        self.geometry("380x300")
        self.resizable(False, False)
        self.configure(bg="#1e1e1e")
        self.file_path = None

        FG = "#e0e0e0"
        BG = "#1e1e1e"

        tk.Label(self, text="🔓 Unlocker", font=("Segoe UI", 18, "bold"), fg=FG, bg=BG).pack(pady=(20, 5))
        tk.Label(
            self, text="Open a .locked file with the password\nthe sender gave you.",
            font=("Segoe UI", 10), fg="#a0a0a0", bg=BG, justify="center",
        ).pack(pady=(0, 15))

        self.file_label = tk.Label(self, text="No file selected", fg="#a0a0a0", bg=BG)
        self.file_label.pack(pady=5)
        tk.Button(self, text="Choose .locked File", command=self.choose_file).pack(pady=5)

        self.pw_entry = tk.Entry(self, show="*", width=30, justify="center")
        self.pw_entry.pack(pady=(15, 5))
        self.pw_entry.insert(0, "")
        self.pw_entry.configure(fg=FG, bg="#2b2b2b", insertbackground=FG)

        self.show_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self, text="Show password", variable=self.show_var, command=self.toggle_show,
            fg=FG, bg=BG, selectcolor="#2b2b2b", activebackground=BG, activeforeground=FG,
        ).pack(pady=5)

        tk.Button(self, text="Unlock", command=self.do_unlock, width=15, height=1).pack(pady=15)

        self.status = tk.Label(self, text="", fg="#a0a0a0", bg=BG, wraplength=340)
        self.status.pack(pady=5)

    def toggle_show(self):
        self.pw_entry.configure(show="" if self.show_var.get() else "*")

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="Select Locked File", filetypes=[("Locked files", "*.locked"), ("All files", "*.*")]
        )
        if path:
            self.file_path = path
            self.file_label.configure(text=os.path.basename(path), fg="white")

    def do_unlock(self):
        if not self.file_path:
            messagebox.showwarning("No file", "Please choose a .locked file first.")
            return
        pw = self.pw_entry.get()
        if not pw:
            messagebox.showwarning("No password", "Please enter the password.")
            return

        try:
            output_path = unlock_file(self.file_path, pw, OUTPUT_DIR)
            self.status.configure(text=f"Saved: {os.path.basename(output_path)}", fg="#4caf50")
            messagebox.showinfo("Unlocked!", f"File saved to:\n{output_path}")
        except ValueError as e:
            self.status.configure(text=str(e), fg="#e53935")
            messagebox.showerror("Failed", str(e))
        except Exception as e:
            self.status.configure(text=f"Error: {e}", fg="#e53935")
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = UnlockerApp()
    app.mainloop()