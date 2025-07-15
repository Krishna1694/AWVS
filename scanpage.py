import tkinter as tk
from tkinter import filedialog, messagebox
import re

class ScanPage(tk.Frame):
    def __init__(self, master, switch_to_welcome_page, start_scan_callback):
        super().__init__(master)
        self.master = master
        self.switch_to_welcome_page = switch_to_welcome_page
        self.start_scan_callback = start_scan_callback

        self.payload_selected = {cat: False for cat in ['SQLi', 'XSS', 'CMD', 'HTML']}
        self.uploaded_files = {cat: None for cat in ['SQLi', 'XSS', 'CMD', 'HTML']}
        self.file_widgets = {}

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Enter your target URL", font=("Helvetica", 16)).pack(pady=20)

        self.url_entry = tk.Entry(self, width=40, font=("Helvetica", 12), fg="gray")
        self.url_entry.insert(0, "e.g., https://example.com")
        self.url_entry.pack(pady=10)

        self.url_entry.bind("<FocusIn>", self.clear_placeholder)
        self.url_entry.bind("<FocusOut>", self.restore_placeholder)
        self.url_entry.bind("<KeyRelease>", self.validate_url)

        tk.Label(self, text="Payloads", font=("Helvetica", 12)).pack(pady=10)

        payload_frame = tk.Frame(self)
        payload_frame.pack(pady=5)

        tk.Button(payload_frame, text="Default", width=12).pack(side="left", padx=10)
        tk.Button(payload_frame, text="Custom", width=12, command=self.open_custom_payload_popup).pack(side="right", padx=10)

        action_frame = tk.Frame(self)
        action_frame.pack(side="bottom", fill="x", pady=20)

        tk.Button(action_frame, text="Back", width=12, font=("Helvetica", 15),
                  command=self.switch_to_welcome_page).pack(side="left", padx=30, anchor="sw")

        self.start_btn = tk.Button(action_frame, text="Start Scan", width=12, font=("Helvetica", 15),
                                   command=self.start_scan, state="disabled")
        self.start_btn.pack(side="right", padx=30, anchor="se")

    def validate_url(self, event=None):
        url = self.url_entry.get().strip()
        pattern = r'^https?://[\w.-]+(?:\.[\w.-]+)+.*$'
        if re.match(pattern, url):
            self.start_btn.config(state="normal")
        else:
            self.start_btn.config(state="disabled")

    def start_scan(self):
        url = self.url_entry.get().strip()
        if self.start_btn['state'] == 'normal':
            print(f"Scan started for: {url}")
            self.start_scan_callback()  
        else:
            messagebox.showwarning("Invalid URL", "Please enter a valid URL before starting the scan.")

    def open_custom_payload_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Custom Payloads")
        popup.geometry("500x400")
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(popup, text="Payloads", font=("Helvetica", 14)).pack(pady=10)

        categories = ["SQLi", "XSS", "CMD", "HTML"]
        for cat in categories:
            row = tk.Frame(popup)
            row.pack(fill="x", pady=5)

            tk.Label(row, text=cat, width=10, anchor='w').pack(side="left", padx=5)

            upload_btn = tk.Button(row, text="Upload", command=lambda c=cat: self.handle_upload(c))
            upload_btn.pack(side="left", padx=5)

            or_label = tk.Label(row, text="or")
            or_label.pack(side="left")

            paste_btn = tk.Button(row, text="Paste", command=lambda c=cat: self.handle_paste(c))
            paste_btn.pack(side="left", padx=5)

            file_display = tk.Frame(row)
            file_display.pack(side="left", padx=10)

            file_label = tk.Label(file_display, text="", font=("Helvetica", 9), fg="gray")
            file_label.pack(side="left")

            remove_btn = tk.Button(file_display, text="❌", font=("Helvetica", 9), relief="flat",
                                   command=lambda c=cat: self.remove_file(c))
            remove_btn.pack(side="left", padx=5)
            remove_btn.pack_forget()

            self.file_widgets[cat] = {
                "label": file_label,
                "remove": remove_btn,
                "upload": upload_btn,
                "paste": paste_btn,
                "or": or_label
            }

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=20)

        cancel_btn = tk.Button(btn_frame, text="Cancel", command=popup.destroy)
        cancel_btn.pack(side="left", padx=10)

        self.done_btn = tk.Button(btn_frame, text="Done", state="disabled", command=lambda: self.done_and_close(popup))
        self.done_btn.pack(side="right", padx=10)

    def handle_upload(self, cat):
        file_path = filedialog.askopenfilename(title=f"Upload {cat} Payload")
        if file_path:
            self.uploaded_files[cat] = file_path
            self.payload_selected[cat] = True
            short_name = file_path.split("/")[-1] if "/" in file_path else file_path.split("\\")[-1]

            w = self.file_widgets[cat]
            w["label"].config(text=short_name)
            w["remove"].pack(side="left", padx=5)
            w["upload"].pack_forget()
            w["paste"].pack_forget()
            w["or"].pack_forget()

            print(f"{cat} Payload uploaded from: {file_path}")
            self.check_done_button()

    def handle_paste(self, cat):
        popup = tk.Toplevel(self)
        popup.title(f"Paste {cat} Payloads")
        popup.geometry("450x300")
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(popup, text=f"Paste your {cat} payloads below (one per line):", font=("Helvetica", 12)).pack(pady=10)

        text_box = tk.Text(popup, height=10, wrap="word", font=("Helvetica", 11))
        text_box.pack(expand=True, fill="both", padx=10, pady=5)

        def save_payloads():
            data = text_box.get("1.0", tk.END).strip().splitlines()
            cleaned = [line.strip() for line in data if line.strip()]
            if cleaned:
                self.payload_selected[cat] = True
                print(f"{cat} Payloads pasted: {cleaned}")
                self.check_done_button()

                w = self.file_widgets[cat]
                w["label"].config(text="Pasted")
                w["remove"].pack(side="left", padx=5)
                w["upload"].pack_forget()
                w["paste"].pack_forget()
                w["or"].pack_forget()

                popup.destroy()
            else:
                messagebox.showwarning("Empty", "No valid payloads entered.")

        tk.Button(popup, text="Save", command=save_payloads).pack(pady=10)

    def remove_file(self, cat):
        self.uploaded_files[cat] = None
        self.payload_selected[cat] = False

        w = self.file_widgets[cat]
        w["label"].config(text="")
        w["remove"].pack_forget()
        w["upload"].pack(side="left", padx=5)
        w["or"].pack(side="left")
        w["paste"].pack(side="left", padx=5)

        print(f"{cat} Payload removed")
        self.check_done_button()

    def check_done_button(self):
        if hasattr(self, "done_btn") and any(self.payload_selected.values()):
            self.done_btn.config(state="normal")
        elif hasattr(self, "done_btn"):
            self.done_btn.config(state="disabled")

    def done_and_close(self, popup):
        print("Custom payloads confirmed.")
        popup.destroy()

    def clear_placeholder(self, event):
        if self.url_entry.get() == "e.g., https://example.com":
            self.url_entry.delete(0, tk.END)
            self.url_entry.config(fg="black")

    def restore_placeholder(self, event):
        if not self.url_entry.get():
            self.url_entry.insert(0, "e.g., https://example.com")
            self.url_entry.config(fg="gray")

