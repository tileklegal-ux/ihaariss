# -*- coding: utf-8 -*-
from fpdf import FPDF
from io import BytesIO
from datetime import datetime


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Artbazar AI — Аналитический отчёт", ln=True)
        self.ln(4)


def build_pdf_report(history: list) -> BytesIO:
    """
    Генерирует PDF-отчёт по истории пользователя.
    Никакой FSM, только рендер.
    """
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    if not history:
        pdf.multi_cell(0, 8, "Нет данных для отчёта.")
    else:
        for item in history:
            pdf.ln(3)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"{item.get('type', '').upper()} — {item.get('date', '')}", ln=True)

            pdf.set_font("Arial", size=11)
            summary = item.get("summary", "")
            pdf.multi_cell(0, 7, f"Сводка: {summary}")

            ai_text = item.get("ai_comment", "")
            if ai_text:
                pdf.ln(1)
                pdf.set_font("Arial", "I", 10)
                pdf.multi_cell(0, 6, ai_text)

    stream = BytesIO(pdf.output(dest="S").encode("latin-1"))
    stream.seek(0)
    return stream
