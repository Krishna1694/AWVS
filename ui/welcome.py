import tkinter as tk
from tkinter import ttk

class WelcomePage(tk.Frame):
    def __init__(self, master, app=None):
        super().__init__(master)
        self.app = app
        label = ttk.Label(self, text='MiniVulnScanner', font=(None, 24))
        label.pack(pady=20)
        desc = ttk.Label(self, text='Minimal scanner with OWASP Top 10 checks. Use only on authorized targets.')
        desc.pack(pady=10)
        start_btn = ttk.Button(self, text='Start Scan', command=lambda: app.show_scan())
        start_btn.pack(pady=10)
