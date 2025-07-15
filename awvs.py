import tkinter as tk
from homepage import WelcomePage
from scanpage import ScanPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AWVS")
        self.geometry("600x400")

        self.frames = {}

        self.frames["WelcomePage"] = WelcomePage(self, self.show_scan_page)
        self.frames["ScanPage"] = ScanPage(self, self.show_welcome_page)

        self.frames["WelcomePage"].pack(fill="both", expand=True)

    def show_scan_page(self):
        self.frames["WelcomePage"].pack_forget()
        self.frames["ScanPage"].pack(fill="both", expand=True)

    def show_welcome_page(self):
        self.frames["ScanPage"].pack_forget()
        self.frames["WelcomePage"].pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
