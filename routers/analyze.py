# логика ML анализа

from fastapi import APIRouter
import pandas as pd
import os

router = APIRouter(prefix="/api/analyze", tags=["Analyze"])

# 🔹 Функция для вычисления рейтинга
def calc_rating(row):
    name = str(row.get("name") or "").lower()
    category = str(row.get("category") or "").lower()
    score = 5

    # Тематические слова, повышающие рейтинг
    if any(k in name for k in ["глэмпинг", "camp", "glamp", "кемпинг", "турбаза"]):
        score += 3
    if any(k in name for k in ["eco", "эко"]):
        score += 1
    if any(k in name for k in ["mountain", "гора", "altai", "shymbulak"]):
        score += 1
    if any(k in name for k in ["lux", "люкс", "премиум"]):
        score += 2
    if any(k in category for k in ["resort", "отель", "гостиница"]):
        score += 1

    return min(score, 10)


# 🔹 Определение типа категории
def detect_category(cat):
    cat = str(cat or "").lower()
    if any(k in cat for k in ["эко", "eco"]):
        return "Эко"
    elif any(k in cat for k in ["юрта", "этно"]):
        return "Этно"
    elif any(k in cat for k in ["глэмпинг", "lux", "люкс", "премиум"]):
        return "Люкс"
    elif any(k in cat for k in ["гостевой", "семейный"]):
        return "Семейный"
    elif any(k in cat for k in ["гора", "mountain"]):
        return "Горный"
    else:
        return "Стандарт"


@router.get("/")
def analyze_data():
    input_file = "data/raw/places.csv"
    output_file = "data/processed/analyzed.csv"
    query_file = "data/meta/last_query.txt"

    if not os.path.exists(input_file):
        return {"error": f"Файл {input_file} не найден. Сначала запусти /api/places."}

    df = pd.read_csv(input_file)
    if df.empty:
        return {"warning": "Файл пуст, нет данных для анализа."}

    # 🔹 Загружаем последний запрос из /api/places
    current_query = ""
    if os.path.exists(query_file):
        with open(query_file, "r", encoding="utf-8") as f:
            current_query = f.read().strip().lower()

    # 🔹 Фильтруем по последнему запросу (например, 'глэмпинг')
    if "query" in df.columns and current_query:
        df = df[df["query"].str.lower() == current_query]

    # 🔹 Дополнительная тематическая фильтрация
    theme_keywords = [
        "глэмпинг", "кемпинг", "турбаза", "отдых", "camp", "glamp", "resort"
    ]
    if current_query:
        theme_keywords.append(current_query)
    df = df[df["name"].str.lower().apply(lambda x: any(k in x for k in theme_keywords))]

    # 🔹 Расчёт рейтинга и категории
    df["rating"] = df.apply(calc_rating, axis=1)
    df["category_type"] = df["category"].apply(detect_category)

    # 🔹 Очистка данных
    df = df.drop_duplicates(subset=["name", "address"])
    df = df.dropna(subset=["name"])
    df = df[df["name"].str.strip() != ""]

    # 🔹 Фильтр по городу (если есть колонка city)
    if "city" in df.columns:
        df = df[df["city"].str.lower() == "алматы"]

    # 🔹 Топ-5 по рейтингу
    df = df.sort_values(by="rating", ascending=False).head(5)

    df = df.fillna("")
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(output_file, index=False)

    print(f"📊 Анализ завершён: {len(df)} объектов сохранено в {output_file}")
    print(f"🗂 Тема анализа: {current_query or 'не указана'}")

    return {
        "status": "done",
        "query": current_query,
        "count": len(df),
        "output": output_file,
        "sample": df.head(3).to_dict(orient="records")
    }
