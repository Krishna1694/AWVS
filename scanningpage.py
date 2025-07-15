import tkinter as tk
import threading
import time

class ScanningPage(tk.Frame):
    def __init__(self, master, switch_to_result_page, stop_scan_callback):
        super().__init__(master)
        self.master = master
        self.switch_to_result_page = switch_to_result_page
        self.stop_scan_callback = stop_scan_callback
        self.running = True

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Scanning...", font=("Helvetica", 18)).pack(pady=20)

        self.log_box = tk.Text(self, height=15, width=70, font=("Courier", 10))
        self.log_box.pack(padx=20, pady=10)
        self.log_box.config(state="disabled")

        self.stop_button = tk.Button(self, text="Stop Scan", font=("Helvetica", 12), command=self.stop_scan)
        self.stop_button.pack(pady=20, anchor="se", padx=30)

        # Start scanning in background
        threading.Thread(target=self.run_scan_simulation, daemon=True).start()

    def log_message(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")

    def run_scan_simulation(self):
        # Dummy scanning logic
        for i in range(1, 11):
            if not self.running:
                self.log_message("Scan stopped by user.")
                return
            self.log_message(f"Scanning step {i}/10... (checking vulnerability {i})")
            time.sleep(1)

        self.log_message("Scan completed successfully.")
        time.sleep(2)
        self.switch_to_result_page()  # Move to the next page

    def stop_scan(self):
        self.running = False
        self.stop_scan_callback()
