import tkinter as tk
from homepage import WelcomePage
from scanpage import ScanPage
from scanningpage import ScanningPage
from resultpage import ResultPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AWVS")
        self.geometry("700x500")

        self.frames = {}

        # Initialize WelcomePage
        self.frames["WelcomePage"] = WelcomePage(self, self.show_scan_page)
        self.frames["WelcomePage"].pack(fill="both", expand=True)

    def clear_frames(self):
        for frame in self.frames.values():
            if frame:
                frame.pack_forget()

    def show_welcome_page(self):
        self.clear_frames()
        self.frames["WelcomePage"] = WelcomePage(self, self.show_scan_page)
        self.frames["WelcomePage"].pack(fill="both", expand=True)

    def show_scan_page(self):
        self.clear_frames()

        def start_scan_and_go_to_scanning_page():
            url = self.frames["ScanPage"].url_entry.get()
            print(f"Scan started for: {url}")
            self.scan_result = (
                f"Scan report for {url}:\n"
                "- SQL Injection: Not Found\n"
                "- XSS: Found\n"
                "- CMD Injection: Not Found"
            )
            self.show_scanning_page()

        self.frames["ScanPage"] = ScanPage(
            self,
            switch_to_welcome_page=self.show_welcome_page,
            start_scan_callback=start_scan_and_go_to_scanning_page
        )
        self.frames["ScanPage"].pack(fill="both", expand=True)

    def show_scanning_page(self):
        self.clear_frames()
        self.frames["ScanningPage"] = ScanningPage(
            self,
            switch_to_result_page=self.show_result_page,
            stop_scan_callback=self.handle_scan_stop
        )
        self.frames["ScanningPage"].pack(fill="both", expand=True)

    def handle_scan_stop(self):
        print("Scan was stopped by user.")
        self.scan_result = (
            "Scan was manually stopped.\nPartial results:\n"
            "- SQL Injection: Skipped\n- XSS: Skipped"
        )
        self.show_result_page()

    def show_result_page(self):
        self.clear_frames()
        self.frames["ResultPage"] = ResultPage(
            self,
            self.show_welcome_page,
            self.scan_result
        )
        self.frames["ResultPage"].pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
