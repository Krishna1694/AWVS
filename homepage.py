import tkinter as tk

class WelcomePage(tk.Frame):
    def __init__(self, master, switch_to_scan_page):
        super().__init__(master)
        tk.Label(self, text="Welcome to AWVS", font=("Helvetica", 16)).pack(pady=20)
        tk.Label(self, text="Scan websites for SQLi, XSS, CMDi, etc.", font=("Helvetica", 12)).pack(pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", pady=30)

        tk.Button(button_frame, text="Project Info", width=15, font=("Helvetica", 14),
                  command=self.show_info).pack(side="left", padx=20)

        tk.Button(button_frame, text="New Scan", width=15, font=("Helvetica", 14),
                  command=switch_to_scan_page).pack(side="right", padx=20)

    def show_info(self):
        print("Project Info Clicked")
