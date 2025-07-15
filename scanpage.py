import tkinter as tk
from tkinter import filedialog, simpledialog

class ScanPage(tk.Frame):
    def __init__(self, master, switch_to_welcome_page):
        super().__init__(master)
        self.master = master
        self.switch_to_welcome_page = switch_to_welcome_page

        self.payload_selected = {
            'SQLi': False,
            'XSS': False,
            'CMD': False,
            'HTML': False
        }

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Enter your target URL", font=("Helvetica", 16)).pack(pady=20)

        self.url_entry = tk.Entry(self, width=40, font=("Helvetica", 12))
        self.url_entry.insert(0, "https://example.com")
        self.url_entry.pack(pady=10)

        tk.Label(self, text="Payloads", font=("Helvetica", 12)).pack(pady=10)

        payload_frame = tk.Frame(self)
        payload_frame.pack(pady=5)

        tk.Button(payload_frame, text="Default", width=12).pack(side="left", padx=10)
        tk.Button(payload_frame, text="Custom", width=12, command=self.open_custom_payload_popup).pack(side="right", padx=10)

        # Bottom buttons
        action_frame = tk.Frame(self)
        action_frame.pack(side="bottom", fill="x", pady=20)

        tk.Button(action_frame, text="Back", width=12, font=("Helvetica", 15), command=self.switch_to_welcome_page)\
            .pack(side="left", padx=30, anchor="sw")
        tk.Button(action_frame, text="Start Scan", width=12, font=("Helvetica", 15), command=self.start_scan)\
            .pack(side="right", padx=30, anchor="se")

    def start_scan(self):
        url = self.url_entry.get()
        print(f"Scan started for: {url}")

    def open_custom_payload_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Custom Payloads")
        popup.geometry("400x350")
        popup.grab_set()  # modal window

        tk.Label(popup, text="Payloads", font=("Helvetica", 14)).pack(pady=10)

        categories = ["SQLi", "XSS", "CMD", "HTML"]
        for cat in categories:
            row = tk.Frame(popup)
            row.pack(pady=5)
            tk.Label(row, text=cat, width=10, anchor='w').pack(side="left")

            tk.Button(row, text="Upload", command=lambda c=cat: self.handle_upload(c)).pack(side="left", padx=5)
            tk.Label(row, text="or").pack(side="left")
            tk.Button(row, text="Paste", command=lambda c=cat: self.handle_paste(c)).pack(side="left", padx=5)

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=20)

        cancel_btn = tk.Button(btn_frame, text="Cancel", command=popup.destroy)
        cancel_btn.pack(side="left", padx=10)

        self.done_btn = tk.Button(btn_frame, text="Done", state="disabled", command=lambda: self.done_and_close(popup))
        self.done_btn.pack(side="right", padx=10)

    def handle_upload(self, cat):
        file_path = filedialog.askopenfilename(title=f"Upload {cat} Payload")
        if file_path:
            self.payload_selected[cat] = True
            print(f"{cat} Payload uploaded from: {file_path}")
            self.check_done_button()

    def handle_paste(self, cat):
        data = simpledialog.askstring("Paste Payload", f"Paste your {cat} payload below:")
        if data:
            self.payload_selected[cat] = True
            print(f"{cat} Payload pasted: {data}")
            self.check_done_button()

    def check_done_button(self):
        if any(self.payload_selected.values()):
            self.done_btn.config(state="normal")

    def done_and_close(self, popup):
        print("Custom payloads confirmed.")
        popup.destroy()
