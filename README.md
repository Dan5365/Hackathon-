# Mycar - MyTravel Automation Project
# 🌟 Inspiration

Тысячи зон отдыха, курортов, глэмпингов, санаториев и турбаз в Казахстане до сих пор не представлены онлайн.  
Они теряют клиентов, а туристы — возможности.

**Цель MyTravel** — оцифровать эти объекты, собрать единый каталог и подключать их к платформе через автоматизацию:  
парсинг + ИИ-анализ + рассылка WhatsApp.


## 💡 What It Does

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


