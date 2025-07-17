import tkinter as tk
import threading
import time
from backend.scanner import scan_for_vulnerabilities

class ScanningPage(tk.Frame):
    def __init__(self, master, switch_to_result_page, stop_scan_callback, target_url, selected_payloads):
        super().__init__(master)
        self.master = master
        self.switch_to_result_page = switch_to_result_page
        self.stop_scan_callback = stop_scan_callback
        self.target_url = target_url
        self.selected_payloads = selected_payloads
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
        self.log_message(f"Starting scan on: {self.target_url}")
        try:
            results = scan_for_vulnerabilities(self.target_url, self.selected_payloads)

            for category, payload_results in results.items():
                self.log_message(f"\n[{category} Scan Results]")
                for payload, result in payload_results:
                    if not self.running:
                        self.log_message("Scan stopped by user.")
                        return
                    self.log_message(f"Payload: {payload} --> Result: {result}")
                    time.sleep(0.5)

            self.log_message("\nScan completed successfully.")
            
            # ✅ Store summary for ResultPage
            summary = "\n".join([
                f"[{cat}]\n" + "\n".join(
                    [f"  {p} → {r}" for p, r in payload_results]
                )
                for cat, payload_results in results.items()
            ])
            self.master.scan_result = summary  # <-- This makes it available to ResultPage

            time.sleep(2)
            self.switch_to_result_page()
        except Exception as e:
            self.log_message(f"Error during scan: {e}")

    def stop_scan(self):
        self.running = False
        self.stop_scan_callback()
