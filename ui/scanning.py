import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading

class ScanningPage(tk.Frame):
    def __init__(self, master, app=None, config=None):
        super().__init__(master)
        self.app = app
        self.config = config or {}
        ttk.Label(self, text=f"Scanning: {self.config.get('target')}", font=(None,16)).pack(pady=8)
        self.log = scrolledtext.ScrolledText(self, height=20)
        self.log.pack(fill='both', expand=True, padx=10, pady=10)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=6)
        ttk.Button(btn_frame, text='Stop', command=self.on_stop).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Back', command=lambda: app.show_scan()).pack(side='left', padx=5)
        # Start scan in a thread
        self._stop_flag = False
        t = threading.Thread(target=self.run_scan, daemon=True)
        t.start()

    def write(self, msg):
        self.log.insert('end', msg + '\n')
        self.log.see('end')

    def on_stop(self):
        self._stop_flag = True
        self.write('Stop requested. Attempting to stop scanning...')

    def run_scan(self):
        scanner = self.app.scanner
        self.write('Preparing scan...')
        try:
            results = scanner.run_scan(self.config, write_callback=self.write, stop_flag=lambda: self._stop_flag)
            self.write('Scan complete.')
            self.app.show_results(results)
        except Exception as e:
            self.write('Scan failed: ' + str(e))
            messagebox.showerror('Scan error', str(e))
