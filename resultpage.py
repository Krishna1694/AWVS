import tkinter as tk
from tkinter import filedialog
from fpdf import FPDF


class ResultPage(tk.Frame):
    def __init__(self, master, switch_to_welcome_page, scan_result):
        super().__init__(master)
        self.master = master
        self.switch_to_welcome_page = switch_to_welcome_page
        self.scan_result = scan_result
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Results", font=("Helvetica", 16)).pack(pady=10)

        self.result_box = tk.Text(self, width=70, height=15, font=("Consolas", 11))
        self.result_box.pack(pady=10)
        self.result_box.insert(tk.END, self.scan_result)
        self.result_box.config(state=tk.DISABLED)

        # Buttons at the bottom
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Download Report", command=self.download_report).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Export PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Finish", command=self.switch_to_welcome_page).pack(side=tk.LEFT, padx=10)

    def download_report(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            title="Save Report",
            filetypes=[("Text files", "*.txt")]
        )
        if file_path:
            with open(file_path, "w") as f:
                f.write(self.scan_result)

    def export_pdf(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            title="Export PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            lines = self.scan_result.split('\n')
            for line in lines:
                pdf.multi_cell(0, 10, txt=line)
            pdf.output(file_path)
