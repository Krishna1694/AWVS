import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF
from collections import defaultdict


class ResultPage(tk.Frame):
    def __init__(self, master, app=None, results=None):
        super().__init__(master)
        self.app = app
        self.results = results or {}

        ttk.Label(self, text='Scan Results', font=(None, 18)).pack(pady=10)

        grouped = self.group_findings(self.results.get('findings', []))

        # Create scrollable frame for results
        container = ttk.Frame(self)
        container.pack(fill='both', expand=True, padx=5, pady=5)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Populate scrollable frame with grouped results
        for owasp_cat, vulns in grouped.items():
            ttk.Label(scrollable_frame, text=owasp_cat, font=(None, 14, 'bold')).pack(anchor='w', padx=10, pady=5)
            for title, data in vulns.items():
                ttk.Label(scrollable_frame, text=f"{title} ({data['severity']})", font=(None, 12)).pack(anchor='w', padx=20)
                for ep in data['endpoints']:
                    ttk.Label(scrollable_frame, text=f"- {ep}").pack(anchor='w', padx=40)

        # Buttons stay outside the scrollable area
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text='Export as TXT', command=lambda: self.export_txt(grouped)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Export as PDF', command=lambda: self.export_pdf(grouped)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Back', command=lambda: app.show_welcome()).pack(side='left', padx=5)

    def group_findings(self, findings):
        grouped = defaultdict(lambda: defaultdict(lambda: {'severity': None, 'endpoints': [], 'detail': None}))
        for f in findings:
            owasp_cat = f.get('owasp', 'Unmapped')
            title = f.get('title', 'Unknown')
            grouped[owasp_cat][title]['severity'] = f.get('severity', '')
            grouped[owasp_cat][title]['detail'] = f.get('detail', '')
            ep = f.get('url') or f.get('param') or ''
            if ep and ep not in grouped[owasp_cat][title]['endpoints']:
                grouped[owasp_cat][title]['endpoints'].append(ep)
        return grouped

    def export_txt(self, grouped):
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files', '*.txt')])
        if not path:
            return
        try:
            with open(path, 'w') as f:
                f.write('OWASP Scan Report\n')
                f.write(f"Target: {self.results.get('target')}\n\n")
                for owasp_cat, vulns in grouped.items():
                    f.write(f"{owasp_cat}\n")
                    for title, data in vulns.items():
                        f.write(f"  Finding: {title}\n")
                        f.write(f"  Severity: {data['severity']}\n")
                        f.write("  Endpoints:\n")
                        for ep in data['endpoints']:
                            f.write(f"    - {ep}\n")
                        f.write(f"  Description: {data['detail']}\n\n")
            messagebox.showinfo('Saved', f'Saved to {path}')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def export_pdf(self, grouped):
        path = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF files', '*.pdf')])
        if not path:
            return
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'OWASP Scan Report', ln=True)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f"Target: {self.results.get('target')}", ln=True)
            pdf.ln(5)
            for owasp_cat, vulns in grouped.items():
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 8, owasp_cat, ln=True)
                for title, data in vulns.items():
                    pdf.set_font('Arial', 'B', 12)
                    pdf.multi_cell(0, 6, f"Finding: {title} ({data['severity']})")
                    pdf.set_font('Arial', '', 11)
                    pdf.multi_cell(0, 6, "Endpoints:")
                    for ep in data['endpoints']:
                        pdf.multi_cell(0, 6, f"  - {ep}")
                    pdf.multi_cell(0, 6, f"Description: {data['detail']}\n")
                    pdf.ln(1)
            pdf.output(path)
            messagebox.showinfo('Saved', f'Saved to {path}')
        except Exception as e:
            messagebox.showerror('Error', str(e))
