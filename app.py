import tkinter as tk
from ui.welcome import WelcomePage
from ui.scan import ScanPage
from ui.scanning import ScanningPage
from ui.results import ResultPage
from backend.scanner_core import ScannerCore

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MiniVulnScanner")
        self.geometry("800x600")
        self.scanner = ScannerCore()
        self._frame = None
        self.show_welcome()

    def switch_frame(self, frame_class, **kwargs):
        new_frame = frame_class(self, **kwargs)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill='both', expand=True)

    def show_welcome(self):
        self.switch_frame(WelcomePage, app=self)

    def show_scan(self):
        self.switch_frame(ScanPage, app=self)

    def show_scanning(self, config):
        self.switch_frame(ScanningPage, app=self, config=config)

    def show_results(self, results):
        self.switch_frame(ResultPage, app=self, results=results)

if __name__ == '__main__':
    app = App()
    app.mainloop()
