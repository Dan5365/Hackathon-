# Mycar - MyTravel Automation Project
# Вдохновение

Тысячи зон отдыха, курортов, глэмпингов, санаториев и турбаз в Казахстане до сих пор не представлены онлайн.  
Они теряют клиентов, а туристы — возможности.

**Цель MyTravel** — оцифровать эти объекты, собрать единый каталог и подключать их к платформе через автоматизацию:  
парсинг + ИИ-анализ + рассылка WhatsApp.


## Что оно делает?

Проект состоит из 3 основных модулей:

### ✅ 1. Google Maps Scraper (`scarper.py`)
Собирает данные по поисковым запросам:
- Название
- Адрес
- Рейтинг
- Телефон
- Координаты
- Ссылки и отзывы
- Сохранение в CSV / XLSX

### ✅ 2. Instagram Parser (`inst_parser_hack3.py`)
Работает по списку аккаунтов:
- Количество подписчиков
- Активность
- Описание
- Ссылки
- Фото (по желанию)
- Выгрузка в CSV и JSON

### ✅ 3. WhatsApp Outreach Bot (`whatsapp_send.py`)
Автоматически:
- Определяет тип объекта через OpenAI (глэмпинг / база отдыха / отель и т.д.)
- Генерирует персонализированное сообщение
- Отправляет его через WhatsApp Business API / pywhatkit
- Форматирует номера телефонов
- Логирует отправки

---

## ⚙️ Tech Stack

**Языки и библиотеки:**
- Python 3.x
- Playwright / Selenium (если нужно)
- Pandas
- PyWhatKit
- Requests
- OpenAI API
- dotenv

**Интеграции:**
- Google Maps
- Instagram public data
- WhatsApp Web (Desktop automation)
- CSV/JSON/XLSX экспорт


**Этап Запуска:**
1. Клонируем репозиторий
```
git clone https://github.com/Dan5365/Hackathon-.git
cd https://github.com/Dan5365/Hackathon-.git
```
2. Установка зависимостей

Создате виртуальное окружение и установи зависимости:
```
pip install -r requirements.txt
```
или
```
pip install fastapi uvicorn pandas requests
```

3.Запуск проекта
3.1 Для 2gis
```
uvicorn main:app --reload
```

3.2 Для google maps
```
python scripts/scarper.py -s "Астана Зона отдыха" -t 50 --timeout 120 --headless False
```

3.3 Для инстаграм
```
python scripts/inst_parser_hack4.py
```

После запуска приложение будет доступно по адресу:
 http://127.0.0.1:8000

 **Структура проекта**

 main.py                 # основной файл приложения
routers/                # маршруты API
utils/                  # вспомогательные функции
scripts/                # скрипты и парсеры
data/                   # данные (raw, processed, meta)
output/                 # результаты анализа
