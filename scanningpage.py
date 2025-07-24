import tkinter as tk
import threading
import time

from backend.crawler import get_all_links, extract_forms_from_url
from backend.injector import inject_get_params_from_file, inject_form_payloads


class ScanningPage(tk.Frame):
    def __init__(self, master, switch_to_result_page, stop_scan_callback, target_url, selected_payloads, demo_mode=False):
        super().__init__(master)
        self.master = master
        self.switch_to_result_page = switch_to_result_page
        self.stop_scan_callback = stop_scan_callback
        self.target_url = target_url
        self.selected_payloads = selected_payloads
        self.demo_mode = demo_mode
        self.running = True

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Scanning...", font=("Helvetica", 18)).pack(pady=20)

        self.log_box = tk.Text(self, height=15, width=70, font=("Courier", 10))
        self.log_box.pack(padx=20, pady=10)
        self.log_box.config(state="disabled")

        self.stop_button = tk.Button(self, text="Stop Scan", font=("Helvetica", 12), command=self.stop_scan)
        self.stop_button.pack(pady=20, anchor="se", padx=30)

        threading.Thread(target=self.run_scan_simulation, daemon=True).start()

    def log_message(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.update_idletasks()
        self.log_box.config(state="disabled")

    def run_scan_simulation(self):
        self.log_message(f"[*] Starting scan: {'DEMO MODE' if self.demo_mode else self.target_url}")
        try:
            # Step 1: Get links
            if self.demo_mode:
                links = [
                    "http://testphp.vulnweb.com/listproducts.php?cat=1",
                    "http://testphp.vulnweb.com/artists.php?artist=2"
                ]
                self.log_message(f"[✔] Demo mode: {len(links)} URLs loaded.")
            else:
                links = list(get_all_links(self.target_url))
                self.log_message(f"[✔] Crawl complete. {len(links)} internal links found.")

            # Step 2: Save to temp file
            temp_file = "./backend/_awvs_temp_urls.txt"
            with open(temp_file, "w") as f:
                for link in links:
                    f.write(link + "\n")
            self.log_message("[*] URLs saved for scanning.")

            # Step 3: Extract forms
            all_forms = []
            for link in links:
                if not self.running:
                    self.log_message("[!] Scan stopped during form extraction.")
                    return
                forms = extract_forms_from_url(link)
                if forms:
                    all_forms.extend(forms)
                    self.log_message(f"[+] Found {len(forms)} form(s) in: {link}")
                time.sleep(0.05)

            self.log_message(f"[✔] Form extraction done. {len(all_forms)} forms collected.\n")

            # Step 4: Inject payloads
            full_results = []

            for category, payloads in self.selected_payloads.items():
                if not self.running:
                    self.log_message(f"[!] Scan stopped before {category} test.")
                    return

                # --- GET Injection ---
                self.log_message(f"[*] Testing GET URLs for {category}...")
                get_results = inject_get_params_from_file(temp_file, category)
                seen_keys = set()
                for url, param, payload, result in get_results:
                    if not self.running:
                        self.log_message("[!] Scan stopped during GET injection.")
                        return

                    key = f"{url}::{param}"
                    if key in seen_keys:
                        continue  # skip duplicate
                    seen_keys.add(key)

                    self.log_message(f"[{category}] {param} → {payload} → {result}")
                    full_results.append((category, f"{param} = {payload}", result))

                    if result == "Potential Vulnerability":
                        continue  # Stop testing more payloads on same param

                    time.sleep(0.05)

                # --- Form Injection ---
                self.log_message(f"[*] Testing Forms for {category}...")
                form_results = inject_form_payloads(all_forms, category)
                seen_forms = set()
                for url, method, data, result in form_results:
                    if not self.running:
                        self.log_message("[!] Scan stopped during form injection.")
                        return

                    key = f"{url}::{method}"
                    if key in seen_forms:
                        continue
                    seen_forms.add(key)

                    self.log_message(f"[{category}] {method} → {url}")
                    self.log_message(f"    Payload: {data}")
                    self.log_message(f"    Result : {result}\n")

                    payload_summary = ", ".join([f"{k}={v}" for k, v in data.items()])
                    full_results.append((category, f"{url} ({method}) | Payload: {payload_summary}", result))

                    if result == "Potential Vulnerability":
                        continue  # Skip further payloads for same form

                    time.sleep(0.05)

            # Step 5: Final summary
            self.log_message("\n[✔] Full scan completed.")

            summary = ""
            for category in self.selected_payloads:
                summary += f"\n[{category} Results]\n"
                for cat, src, res in full_results:
                    if cat == category:
                        summary += f"  {src} → {res}\n"

            self.master.scan_result = summary
            time.sleep(1)
            self.switch_to_result_page()

        except Exception as e:
            self.log_message(f"[!] Error during scan: {e}")

    def stop_scan(self):
        self.running = False
        self.stop_scan_callback()
