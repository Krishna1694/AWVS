import tkinter as tk
from homepage import WelcomePage
from scanpage import ScanPage
# from resultspage import ResultsPage  # Example of how you’d add more

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AWVS")
        self.geometry("600x400")

        self.frames = {}

        # Register all pages here
        self.frames["WelcomePage"] = WelcomePage(self, lambda: self.show_frame("ScanPage"))
        self.frames["ScanPage"] = ScanPage(self, lambda: self.show_frame("WelcomePage"))
        # self.frames["ResultsPage"] = ResultsPage(self, ...)  # Example

        # Show the first page
        self.show_frame("WelcomePage")

    def show_frame(self, page_name):
        # Hide all pages
        for frame in self.frames.values():
            frame.pack_forget()
        # Show selected page
        self.frames[page_name].pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
