# работа с 2GIS API
# routers/places.py
from fastapi import APIRouter
import requests
import os
import pandas as pd
import json
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(prefix="/api/places", tags=["Places"])

# API-ключ 2GIS
API_KEY = "401b0774-dbe8-4f70-91c9-697adac3e650"

DATA_DIR = "data/raw"
META_DIR = "data/meta"
FILE_PATH = os.path.join(DATA_DIR, "places.csv")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)

# --- 🔧 Вспомогательные функции ---
def safe_float(value):
    """Безопасное преобразование в float"""
    try:
        v = float(value)
        if v == float("inf") or v == float("-inf"):
            return None
        return v
    except Exception:
        return None

def extract_contacts(contact_groups):
    """Извлекает телефоны"""
    if not contact_groups:
        return ""
    phones = []
    for group in contact_groups:
        for contact in group.get("contacts", []):
            if contact.get("type") == "phone":
                phones.append(contact.get("value"))
    return ", ".join(phones)

def extract_coords(point):
    """Извлекает координаты"""
    if not point:
        return "", None, None
    lat = safe_float(point.get("lat"))
    lon = safe_float(point.get("lon"))
    coords = f"{lat}, {lon}" if lat and lon else ""
    return coords, lat, lon

def extract_schedule(item):
    """Форматирует расписание в JSON"""
    schedule = item.get("schedule")
    if not schedule:
        return ""
    try:
        return json.dumps(schedule, ensure_ascii=False)
    except Exception:
        return str(schedule)

# --- 🚀 Основной эндпоинт ---
@router.get("/")
def get_places(query: str = "глэмпинг", city: str = "Алматы", region_id: int = 12):
    """
    Получает данные из 2GIS и сохраняет их в data/raw/places.csv.
    Также записывает последний запрос (query, city) в data/meta/.
    """
    url = "https://catalog.api.2gis.com/3.0/items"
    params = {"q": query, "region_id": region_id, "key": API_KEY, "page_size": 50}
    resp = requests.get(url, params=params).json()

    if resp.get("meta", {}).get("code") != 200:
        return {"error": "Ошибка при обращении к 2GIS API", "details": resp.get("meta")}

    items = resp.get("result", {}).get("items", [])
    if not items:
        return {"status": "no_results", "query": query, "city": city}

    results = []
    for item in items:
        coords, lat, lon = extract_coords(item.get("point"))
        results.append({
            "name": item.get("name", ""),
            "address": item.get("address_name", ""),
            "contacts": extract_contacts(item.get("contact_groups")),
            "coords": coords,
            "category": item.get("rubrics")[0]["name"] if item.get("rubrics") else "",
            "lat": lat,
            "lon": lon,
            "schedule": extract_schedule(item),
            "query": query,
            "city": city
        })

    # --- 📦 Чтение старых данных ---
    if os.path.exists(FILE_PATH) and os.path.getsize(FILE_PATH) > 0:
        try:
            old_df = pd.read_csv(FILE_PATH)
        except Exception:
            old_df = pd.DataFrame(columns=results[0].keys())
    else:
        old_df = pd.DataFrame(columns=results[0].keys())

    # --- 🔄 Объединение и очистка ---
    new_df = pd.DataFrame(results)
    combined_df = pd.concat([old_df, new_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["name", "address"], keep="last")
    combined_df = combined_df.fillna("")

    # --- 💾 Сохранение данных ---
    combined_df.to_csv(FILE_PATH, index=False, encoding="utf-8")

    # --- 💾 Сохраняем последние параметры для анализа ---
    with open(os.path.join(META_DIR, "last_query.txt"), "w", encoding="utf-8") as f:
        f.write(query.strip())
    with open(os.path.join(META_DIR, "last_city.txt"), "w", encoding="utf-8") as f:
        f.write(city.strip())

    print(f"✅ Добавлено новых объектов: {len(new_df)} (запрос: {query}, город: {city})")
    print(f"📁 Всего сохранено: {len(combined_df)} записей")

    return {
        "status": "success",
        "query": query,
        "city": city,
        "count_new": len(new_df),
        "total_saved": len(combined_df),
        "file": FILE_PATH,
        "sample": combined_df.tail(3).to_dict(orient="records")
    }
