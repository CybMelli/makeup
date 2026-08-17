"""
File Locker - a simple app that locks and unlocks files using a password.

Works on any file type: PDF, images, videos, Word docs, zip files, etc.

------------------------------------------------------------------
HOW THE ENCRYPTION WORKS (in plain English):
------------------------------------------------------------------
1. The user types a password. A password is just text, so we can't use
   it directly as an encryption key - it needs to be turned into a
   proper key first.

2. We use something called PBKDF2 to stretch the password into a
   32-byte key. PBKDF2 also uses a random "salt" (extra random bytes)
   so that even if two people use the same password, their keys are
   different. This makes the encryption much harder to crack.

3. We use Fernet (which is AES encryption under the hood) to actually
   scramble the file's bytes using that key.

4. The salt is saved at the very start of the locked file, so when we
   unlock it later, we can read the salt back out and rebuild the
   exact same key from the password.

5. If the password is wrong, the key will be wrong too, and Fernet
   will refuse to decrypt the file (it fails safely, no crash/corrupted
   output).
------------------------------------------------------------------
HOW THE PASSWORD ARCHIVE TAB WORKS (in plain English):
------------------------------------------------------------------
Unlike the Lock/Unlock tabs above, which use "generic" AES that only
this app understands, this tab creates a REAL password-protected .zip
file using the AES-256 encryption standard built into the zip format
itself. That means:

  - Any file type can go in (image, PDF, video, docs, anything)
  - Windows' built-in "Extract All", and most archive tools
    (7-Zip, WinRAR, etc.) will natively prompt for the password -
    no special app needed to open it, at least on Windows/iPhone.
  - We use pyzipper, a library that adds real AES-256 zip encryption
    on top of Python's built-in zipfile module (which only supports
    weaker, outdated ZipCrypto encryption).
------------------------------------------------------------------
"""

import os
import base64
import customtkinter as ctk
from tkinter import filedialog, messagebox

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import pyzipper
import pikepdf

SALT_SIZE = 16          # bytes of randomness added to every password
PBKDF2_ITERATIONS = 200_000


# ------------------------------------------------------------------
# ENCRYPTION LOGIC (kept separate from the GUI on purpose - this makes
# it easy to explain / test on its own, without touching the interface)
# ------------------------------------------------------------------

def derive_key(password: str, salt: bytes) -> bytes:
    """Turn a plain text password + salt into a key Fernet can use."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key)


def lock_file(filepath: str, password: str) -> str:
    """Encrypts a file and saves it with a .locked extension."""
    salt = os.urandom(SALT_SIZE)          # fresh random salt every time
    key = derive_key(password, salt)
    fernet = Fernet(key)

    with open(filepath, "rb") as f:
        original_data = f.read()

    encrypted_data = fernet.encrypt(original_data)

    locked_path = filepath + ".locked"
    with open(locked_path, "wb") as f:
        f.write(salt + encrypted_data)     # salt goes first, then the data

    return locked_path


def unlock_file(filepath: str, password: str) -> str:
    """Decrypts a .locked file back to its original form."""
    with open(filepath, "rb") as f:
        file_bytes = f.read()

    salt = file_bytes[:SALT_SIZE]           # first 16 bytes = the salt
    encrypted_data = file_bytes[SALT_SIZE:]  # everything after = the file

    key = derive_key(password, salt)
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)  # raises InvalidToken if wrong

    if filepath.endswith(".locked"):
        unlocked_path = filepath[:-len(".locked")]
    else:
        unlocked_path = filepath + ".unlocked"

    with open(unlocked_path, "wb") as f:
        f.write(decrypted_data)

    return unlocked_path


def create_password_archive(filepaths: list, password: str, output_path: str) -> str:
    """
    Bundles one or more files into a real AES-256 password-protected .zip.
    Unlike lock_file(), this produces a standard zip that Windows,
    7-Zip, WinRAR, etc. can open with their own native password prompt.
    """
    with pyzipper.AESZipFile(
        output_path,
        "w",
        compression=pyzipper.ZIP_LZMA,
        encryption=pyzipper.WZ_AES,
    ) as zf:
        zf.setpassword(password.encode())
        for path in filepaths:
            zf.write(path, arcname=os.path.basename(path))

    return output_path


def extract_password_archive(archive_path: str, password: str, extract_to: str) -> list:
    """Extracts a password-protected zip created by create_password_archive()."""
    extracted = []
    with pyzipper.AESZipFile(archive_path, "r") as zf:
        zf.setpassword(password.encode())
        zf.extractall(path=extract_to)
        extracted = zf.namelist()
    return extracted


def protect_pdf(filepath: str, password: str, output_path: str) -> str:
    """
    Adds a REAL password to a PDF using the PDF spec's own encryption -
    the same mechanism Adobe/Chrome/every PDF reader already knows how
    to prompt for. The file stays a normal .pdf the whole time, so it
    keeps the PDF icon and opens with a native password box.
    """
    with pikepdf.open(filepath) as pdf:
        pdf.save(
            output_path,
            encryption=pikepdf.Encryption(owner=password, user=password),
        )
    return output_path


# ------------------------------------------------------------------
# GUI
# ------------------------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT = "#3b82f6"
ACCENT_HOVER = "#2563eb"
SUCCESS = "#22c55e"
ERROR = "#ef4444"
MUTED = "#8b8b93"


class FileLockerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("File Locker")
        self.geometry("460x720")
        self.resizable(False, False)

        # keeps track of which file(s) the user picked, per tab
        self.selected_path = {"lock": None, "unlock": None, "archive_extract": None, "pdf_protect": None}
        self.selected_archive_files = []  # list, since archive tab supports multiple files

        self._build_header()
        self._build_tabs()

    # ---------------- header ----------------

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(28, 10))

        ctk.CTkLabel(
            header, text="🔐 File Locker",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            header, text="Password-protect any file with AES encryption",
            font=ctk.CTkFont(size=13), text_color=MUTED,
        ).pack(anchor="w", pady=(2, 0))

    # ---------------- tabs ----------------

    def _build_tabs(self):
        self.tabs = ctk.CTkTabview(
            self, width=412, height=600,
            segmented_button_selected_color=ACCENT,
            segmented_button_selected_hover_color=ACCENT_HOVER,
        )
        self.tabs.pack(padx=24, pady=10)

        lock_tab = self.tabs.add("🔒 Lock")
        unlock_tab = self.tabs.add("🔓 Unlock")
        archive_tab = self.tabs.add("📦 Archive")
        pdf_tab = self.tabs.add("📕 PDF")

        self._build_lock_tab(lock_tab)
        self._build_unlock_tab(unlock_tab)
        self._build_archive_tab(archive_tab)
        self._build_pdf_tab(pdf_tab)

    # ---------------- lock tab ----------------

    def _build_lock_tab(self, tab):
        self.lock_file_label = self._file_picker_section(
            tab, mode="lock",
            hint="Choose the file you want to protect",
        )

        self.lock_pw_entry, self.lock_pw_toggle = self._password_field(
            tab, placeholder="Enter a password",
        )
        self.lock_pw_confirm, self.lock_pw_confirm_toggle = self._password_field(
            tab, placeholder="Confirm password",
        )

        self.lock_status = ctk.CTkLabel(tab, text="", font=ctk.CTkFont(size=12))
        self.lock_status.pack(pady=(6, 4))

        ctk.CTkButton(
            tab, text="Lock File", height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            command=self.handle_lock,
        ).pack(fill="x", padx=30, pady=(10, 0))

    # ---------------- unlock tab ----------------

    def _build_unlock_tab(self, tab):
        self.unlock_file_label = self._file_picker_section(
            tab, mode="unlock",
            hint="Choose a .locked file to restore",
            filetypes=[("Locked files", "*.locked"), ("All files", "*.*")],
        )

        self.unlock_pw_entry, self.unlock_pw_toggle = self._password_field(
            tab, placeholder="Enter the password",
        )

        self.unlock_status = ctk.CTkLabel(tab, text="", font=ctk.CTkFont(size=12))
        self.unlock_status.pack(pady=(6, 4))

        ctk.CTkButton(
            tab, text="Unlock File", height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            command=self.handle_unlock,
        ).pack(fill="x", padx=30, pady=(10, 0))

    # ---------------- password archive tab ----------------

    def _build_archive_tab(self, tab):
        info = ctk.CTkLabel(
            tab,
            text="Creates a real password-protected .zip.\n"
                 "Works with images, PDFs, videos - anything.\n"
                 "Opens with a native password prompt in Windows.",
            font=ctk.CTkFont(size=12), text_color=MUTED,
            justify="left",
        )
        info.pack(anchor="w", padx=20, pady=(16, 10))

        # --- create section ---
        create_card = ctk.CTkFrame(tab, corner_radius=12)
        create_card.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkLabel(
            create_card, text="Create protected archive",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(14, 4))

        self.archive_files_label = ctk.CTkLabel(
            create_card, text="No files selected", font=ctk.CTkFont(size=13),
            anchor="w", justify="left", wraplength=330,
        )
        self.archive_files_label.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkButton(
            create_card, text="Browse Files (multi-select)", height=34, width=220,
            fg_color="#3a3a3f", hover_color="#4a4a50",
            command=self._browse_archive_files,
        ).pack(padx=16, pady=(0, 14), anchor="w")

        self.archive_pw_entry, _ = self._password_field(
            create_card, placeholder="Enter a password",
        )
        self.archive_pw_confirm, _ = self._password_field(
            create_card, placeholder="Confirm password",
        )

        self.archive_status = ctk.CTkLabel(create_card, text="", font=ctk.CTkFont(size=12))
        self.archive_status.pack(pady=(6, 4))

        ctk.CTkButton(
            create_card, text="Create Password-Protected Archive", height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            command=self.handle_create_archive,
        ).pack(fill="x", padx=16, pady=(6, 16))

    # ---------------- pdf password tab ----------------

    def _build_pdf_tab(self, tab):
        info = ctk.CTkLabel(
            tab,
            text="Adds a REAL password to a PDF.\n"
                 "Stays a .pdf file - keeps the PDF icon,\n"
                 "opens with a native password box in\n"
                 "Adobe, Chrome, WhatsApp's viewer, etc.",
            font=ctk.CTkFont(size=12), text_color=MUTED,
            justify="left",
        )
        info.pack(anchor="w", padx=20, pady=(16, 10))

        self.pdf_file_label = self._file_picker_section(
            tab, mode="pdf_protect",
            hint="Choose the PDF you want to protect",
            filetypes=[("PDF files", "*.pdf")],
        )

        self.pdf_pw_entry, _ = self._password_field(
            tab, placeholder="Enter a password",
        )
        self.pdf_pw_confirm, _ = self._password_field(
            tab, placeholder="Confirm password",
        )

        self.pdf_status = ctk.CTkLabel(tab, text="", font=ctk.CTkFont(size=12))
        self.pdf_status.pack(pady=(6, 4))

        ctk.CTkButton(
            tab, text="Protect PDF", height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            command=self.handle_protect_pdf,
        ).pack(fill="x", padx=30, pady=(10, 0))

    # ---------------- reusable pieces ----------------

    def _file_picker_section(self, parent, mode, hint, filetypes=None):
        """A card with a 'Browse' button and a label showing the chosen file."""
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(fill="x", padx=20, pady=(20, 16))

        ctk.CTkLabel(
            card, text=hint, font=ctk.CTkFont(size=12), text_color=MUTED,
        ).pack(anchor="w", padx=16, pady=(14, 4))

        file_label = ctk.CTkLabel(
            card, text="No file selected", font=ctk.CTkFont(size=13),
            anchor="w", justify="left", wraplength=330,
        )
        file_label.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkButton(
            card, text="Browse Files", height=34, width=140,
            fg_color="#3a3a3f", hover_color="#4a4a50",
            command=lambda: self._browse_file(mode, file_label, filetypes),
        ).pack(padx=16, pady=(0, 14), anchor="w")

        return file_label

    def _browse_file(self, mode, label, filetypes):
        kwargs = {"title": "Select a file"}
        if filetypes:
            kwargs["filetypes"] = filetypes

        path = filedialog.askopenfilename(**kwargs)
        if path:
            self.selected_path[mode] = path
            label.configure(text=f"📄 {os.path.basename(path)}", text_color="white")

    def _browse_archive_files(self):
        paths = filedialog.askopenfilenames(title="Select file(s) to protect")
        if paths:
            self.selected_archive_files = list(paths)
            if len(paths) == 1:
                text = f"📄 {os.path.basename(paths[0])}"
            else:
                names = ", ".join(os.path.basename(p) for p in paths[:3])
                more = f" (+{len(paths) - 3} more)" if len(paths) > 3 else ""
                text = f"📄 {names}{more}"
            self.archive_files_label.configure(text=text, text_color="white")

    def _password_field(self, parent, placeholder):
        """A password entry with a show/hide (👁) toggle button next to it."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=6)

        entry = ctk.CTkEntry(
            row, placeholder_text=placeholder, show="•", height=38,
        )
        entry.pack(side="left", fill="x", expand=True)

        toggle_btn = ctk.CTkButton(
            row, text="👁", width=38, height=38,
            fg_color="#3a3a3f", hover_color="#4a4a50",
            command=lambda: self._toggle_password(entry, toggle_btn),
        )
        toggle_btn.pack(side="left", padx=(6, 0))

        return entry, toggle_btn

    def _toggle_password(self, entry, button):
        if entry.cget("show") == "•":
            entry.configure(show="")
            button.configure(text="🙈")
        else:
            entry.configure(show="•")
            button.configure(text="👁")

    def _set_status(self, label, message, kind="error"):
        color = SUCCESS if kind == "success" else ERROR
        label.configure(text=message, text_color=color)

    # ---------------- button actions ----------------

    def handle_lock(self):
        path = self.selected_path["lock"]
        password = self.lock_pw_entry.get()
        confirm = self.lock_pw_confirm.get()

        if not path:
            self._set_status(self.lock_status, "Please choose a file first.")
            return
        if not password:
            self._set_status(self.lock_status, "Please enter a password.")
            return
        if password != confirm:
            self._set_status(self.lock_status, "Passwords don't match.")
            return

        try:
            locked_path = lock_file(path, password)
            self._set_status(
                self.lock_status,
                f"Locked successfully → {os.path.basename(locked_path)}",
                kind="success",
            )
            messagebox.showinfo("Success", f"File locked:\n{locked_path}")
        except Exception as e:
            self._set_status(self.lock_status, "Something went wrong.")
            messagebox.showerror("Error", f"Could not lock file:\n{e}")

    def handle_unlock(self):
        path = self.selected_path["unlock"]
        password = self.unlock_pw_entry.get()

        if not path:
            self._set_status(self.unlock_status, "Please choose a .locked file.")
            return
        if not password:
            self._set_status(self.unlock_status, "Please enter the password.")
            return

        try:
            unlocked_path = unlock_file(path, password)
            self._set_status(
                self.unlock_status,
                f"Unlocked successfully → {os.path.basename(unlocked_path)}",
                kind="success",
            )
            messagebox.showinfo("Success", f"File unlocked:\n{unlocked_path}")
        except InvalidToken:
            self._set_status(self.unlock_status, "Wrong password. Try again.")
        except Exception as e:
            self._set_status(self.unlock_status, "Something went wrong.")
            messagebox.showerror("Error", f"Could not unlock file:\n{e}")

    def handle_create_archive(self):
        files = self.selected_archive_files
        password = self.archive_pw_entry.get()
        confirm = self.archive_pw_confirm.get()

        if not files:
            self._set_status(self.archive_status, "Please choose at least one file.")
            return
        if not password:
            self._set_status(self.archive_status, "Please enter a password.")
            return
        if password != confirm:
            self._set_status(self.archive_status, "Passwords don't match.")
            return

        # ask where to save the resulting zip
        default_name = (
            os.path.splitext(os.path.basename(files[0]))[0] + "_protected.zip"
            if len(files) == 1 else "protected_archive.zip"
        )
        save_path = filedialog.asksaveasfilename(
            title="Save Password-Protected Archive",
            defaultextension=".zip",
            initialfile=default_name,
            filetypes=[("Zip archive", "*.zip")],
        )
        if not save_path:
            return

        try:
            archive_path = create_password_archive(files, password, save_path)
            self._set_status(
                self.archive_status,
                f"Archive created → {os.path.basename(archive_path)}",
                kind="success",
            )
            messagebox.showinfo(
                "Success",
                f"Password-protected archive created:\n{archive_path}\n\n"
                "Opens with a native password prompt in Windows Explorer "
                "or 7-Zip/WinRAR.",
            )
        except Exception as e:
            self._set_status(self.archive_status, "Something went wrong.")
            messagebox.showerror("Error", f"Could not create archive:\n{e}")

    def handle_protect_pdf(self):
        path = self.selected_path["pdf_protect"]
        password = self.pdf_pw_entry.get()
        confirm = self.pdf_pw_confirm.get()

        if not path:
            self._set_status(self.pdf_status, "Please choose a PDF first.")
            return
        if not password:
            self._set_status(self.pdf_status, "Please enter a password.")
            return
        if password != confirm:
            self._set_status(self.pdf_status, "Passwords don't match.")
            return

        # keeps it a .pdf - e.g. "book.pdf" -> "locked_book.pdf"
        folder = os.path.dirname(path)
        base_name = os.path.basename(path)
        default_name = f"locked_{base_name}"
        save_path = filedialog.asksaveasfilename(
            title="Save Protected PDF",
            defaultextension=".pdf",
            initialfile=default_name,
            initialdir=folder,
            filetypes=[("PDF files", "*.pdf")],
        )
        if not save_path:
            return

        try:
            protected_path = protect_pdf(path, password, save_path)
            self._set_status(
                self.pdf_status,
                f"Protected → {os.path.basename(protected_path)}",
                kind="success",
            )
            messagebox.showinfo(
                "Success",
                f"Password-protected PDF created:\n{protected_path}\n\n"
                "Opens with a native password prompt in any PDF reader.",
            )
        except pikepdf.PasswordError:
            self._set_status(self.pdf_status, "This PDF is already password protected.")
        except Exception as e:
            self._set_status(self.pdf_status, "Something went wrong.")
            messagebox.showerror("Error", f"Could not protect PDF:\n{e}")


if __name__ == "__main__":
    app = FileLockerApp()
    app.mainloop()