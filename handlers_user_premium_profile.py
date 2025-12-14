import os
import pandas as pd
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import ContextTypes

# Функция для генерации и отправки Excel-отчета
async def send_user_report(bot: Bot, chat_id: int, user_id: int):
    # Мокаем данные (позже заменим на реальные из базы)
    data = [
        {
            "Сценарий": f"Сценарий {i}",
            "Вердикт": "ОК" if i % 2 == 0 else "Проблема",
            "Риски": f"Риск {i}",
            "Сезонность": "Зима" if i % 2 == 0 else "Лето",
            "Ресурс": f"Команда {chr(65+i)}",
            "Дата": datetime(2025, 12, i % 28 + 1).strftime("%Y-%m-%d"),
        }
        for i in range(1, 6)
    ]

    df = pd.DataFrame(data)

    # Сохраняем в Excel
    os.makedirs("./tmp", exist_ok=True)
    file_path = f"./tmp/report_{user_id}.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")

    # Отправляем файл
    try:
        with open(file_path, "rb") as file:
            await bot.send_document(chat_id=chat_id, document=file)
    except Exception as e:
        print(f"Ошибка при отправке файла: {e}")
    finally:
        # Удаляем временный файл
        if os.path.exists(file_path):
            os.remove(file_path)
