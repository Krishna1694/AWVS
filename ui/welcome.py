import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

# Path to assets folder (change if needed)
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
# ↑ Goes one level up from ui/ to project root, then looks for assets/

class WelcomePage(tk.Frame):
    def __init__(self, master, app=None):
        super().__init__(master)
        self.app = app

        # Load and display logo if available
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img = img.resize((120, 120), Image.Resampling.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            logo_label = ttk.Label(self, image=logo_img)
            logo_label.image = logo_img
            logo_label.pack(pady=10)
        else:
            print(f"[INFO] Logo not found at: {logo_path}")

        # Project title
        label = ttk.Label(self, text='Advanced Web Vulnerability Scanner', font=("Helvetica", 20, "bold"))
        label.pack(pady=10)

        # Tagline
        desc = ttk.Label(
            self,
            text='Scan websites for OWASP Top 10 vulnerabilities with advanced payload testing.',
            wraplength=600,
            justify="center"
        )
        desc.pack(pady=5)

        # Buttons
        start_btn = ttk.Button(self, text='Start Scan', command=lambda: app.show_scan())
        start_btn.pack(pady=5)

        info_btn = ttk.Button(self, text='Project Info', command=self.show_project_info)
        info_btn.pack(pady=5)

    def show_project_info(self):
        win = tk.Toplevel(self)
        win.title("Project Information")
        win.geometry("500x500")
        win.resizable(False, False)

        # Optional logo
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            logo_label = ttk.Label(win, image=logo_img)
            logo_label.image = logo_img
            logo_label.pack(pady=10)

        # Project name
        ttk.Label(win, text="Advanced Web Vulnerability Scanner", font=("Helvetica", 16, "bold")).pack(pady=5)

        # Description
        desc_text = (
            "A desktop-based web vulnerability scanner with a Tkinter GUI "
            "that detects common OWASP Top 10 vulnerabilities using custom payload testing, "
            "SQLMap integration, and optional ZAP deep scans."
        )
        ttk.Label(win, text=desc_text, wraplength=450, justify="center").pack(pady=10)

        # Team members
        ttk.Label(win, text="Team Members:", font=("Helvetica", 12, "bold")).pack(pady=5)
        members = [
            "P Vinaya Baswaraj\t\t23EO9 – ST#IS#7515",
            "K Abhinav Krishna\t23EO9 – ST#IS#7516",
            "K Indu Reddy\t\t23EO9 – ST#IS#7549"
        ]
        for member in members:
            ttk.Label(win, text=member).pack(anchor="center")

        # Internship note
        ttk.Label(
            win,
            text="\nThis project is part of the internship conducted by Supraja Technologies.",
            wraplength=450,
            justify="center",
            foreground="blue"
        ).pack(pady=15)

        ttk.Button(win, text="Close", command=win.destroy).pack(pady=10)
