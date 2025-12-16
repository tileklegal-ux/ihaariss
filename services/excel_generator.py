# services/excel_generator.py

from openpyxl import Workbook
from io import BytesIO


def generate_excel(headers: list[str], rows: list[list]) -> BytesIO:
    """
    Генерирует Excel-файл в памяти и возвращает BytesIO
    """

    wb = Workbook()
    ws = wb.active

    # Заголовки
    ws.append(headers)

    # Данные
    for row in rows:
        ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return buffer
