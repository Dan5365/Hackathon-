
# routers/generate.py
from fastapi import APIRouter
import os, asyncio, time
from dotenv import load_dotenv
import pandas as pd
import google.generativeai as genai
from datetime import datetime

load_dotenv()
router = APIRouter(prefix="/api/generate", tags=["AI Descriptions"])

# 🔑 Настройка Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyDT7vLvYPpM_qJ6U3fEskxmIMKizl3uwDk"))

# 📁 Пути к файлам
INPUT_FILE = "data/processed/analyzed.csv"
OUTPUT_FILE = "data/processed/final.csv"

# --- 🧠 Асинхронная функция генерации одного описания ---
async def generate_single(model, name, category, address, index, total):
    prompt = (
        f"Напиши привлекательное описание туристического объекта '{name}' в Казахстане.\n"
        f"Тип: {category}. Адрес: {address}.\n"
        f"Сделай текст 150–200 слов, дружелюбный, живой, интересный и подходящий для сайта mytravel.kz.\n"
        f"Не используй повторов, сделай текст уникальным и лёгким для чтения."
    )

    for attempt in range(3):
        try:
            print(f"🔹 [{index}/{total}] Генерация: {name} — попытка {attempt+1}")
            # Асинхронный вызов блокирующей функции
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config={"max_output_tokens": 400}
            )
            if response and hasattr(response, "text"):
                return response.text.strip()
            return "Описание не удалось сгенерировать."
        except Exception as e:
            err = str(e)
            print(f"⚠️ Ошибка у {name}: {err}")
            if "429" in err or "rate" in err.lower():
                await asyncio.sleep(2 * (attempt + 1))
                continue
            return f"Ошибка при генерации: {e}"

    return "Ошибка: превышено количество попыток."


# --- 🚀 Основной эндпоинт ---
@router.get("/")
async def generate_descriptions(limit: int = 5):
    """
    Асинхронно генерирует описания для туристических объектов.
    Поддерживает параллельное выполнение для ускорения.
    """
    if not os.path.exists(INPUT_FILE):
        return {"error": f"Файл {INPUT_FILE} не найден. Сначала запусти /api/analyze."}

    print("\n🚀 [START] Асинхронная генерация через Gemini...")
    start_time = time.time()

    # --- Загружаем данные ---
    df = pd.read_csv(INPUT_FILE).head(limit)
    if df.empty:
        return {"warning": "Файл пуст, нет данных для генерации."}

    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    # --- Асинхронные задачи ---
    tasks = [
        generate_single(
            model,
            row.get("name", "Туристический объект"),
            row.get("category_type", "Объект размещения"),
            row.get("address", "Казахстан"),
            i + 1, len(df)
        )
        for i, row in df.iterrows()
    ]

    # --- Запускаем все запросы одновременно ---
    results = await asyncio.gather(*tasks)

    # --- Обработка результатов ---
    df["description"] = results

    success_count = sum(1 for r in results if "Ошибка" not in r)
    fail_count = len(results) - success_count

    # --- Сохраняем ---
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    elapsed = round(time.time() - start_time, 2)
    timestamp = datetime.now().strftime("%H:%M:%S")

    print("\n🏁 [FINISH] Генерация завершена!")
    print(f"✅ Успешно: {success_count} | ❌ Ошибок: {fail_count}")
    print(f"💾 Файл сохранён: {OUTPUT_FILE}")
    print(f"🕓 Время выполнения: {elapsed} секунд\n")

    # --- Возврат JSON ---
    return {
        "status": "done",
        "count": len(df),
        "success": success_count,
        "failed": fail_count,
        "output": OUTPUT_FILE,
        "time_sec": elapsed,
        "finished_at": timestamp,
        "sample": df[["name", "description"]].head(2).to_dict(orient="records"),
    }
