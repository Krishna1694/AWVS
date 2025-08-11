import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class ScanPage(tk.Frame):
    def __init__(self, master, app=None):
        super().__init__(master)
        self.app = app
        ttk.Label(self, text='Scan Configuration', font=(None,18)).pack(pady=10)
        frm = ttk.Frame(self)
        frm.pack(padx=10, pady=10, fill='x')
        ttk.Label(frm, text='Target URL:').grid(row=0, column=0, sticky='w')
        self.url = ttk.Entry(frm, width=60)
        self.url.grid(row=0, column=1, sticky='w')
        ttk.Label(frm, text='Depth (crawl):').grid(row=1, column=0, sticky='w')
        self.depth = ttk.Spinbox(frm, from_=0, to=3, width=5)
        self.depth.grid(row=1, column=1, sticky='w')
        self.zap_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text='Enable ZAP deep scan (requires ZAP running)', variable=self.zap_var).grid(row=2, column=1, sticky='w')
        ttk.Label(self, text='Notes: Deep scans are intrusive and should only run against authorized targets.').pack(pady=5)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text='Run Scan', command=self.on_run).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Back', command=lambda: app.show_welcome()).pack(side='left', padx=5)

    def on_run(self):
        target = self.url.get().strip()
        if not target:
            messagebox.showerror('Error', 'Please enter a target URL')
            return
        config = {
            'target': target,
            'depth': int(self.depth.get()),
            'zap': bool(self.zap_var.get())
        }
        self.app.show_scanning(config)
