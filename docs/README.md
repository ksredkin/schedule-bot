# 📅 Schedule Bot (ВМЛ)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Aiogram](https://img.shields.io/badge/Aiogram-2CA5E0?style=for-the-badge\&logo=telegram\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge\&logo=postgresql\&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge\&logo=sqlalchemy\&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-00A98F?style=for-the-badge\&logo=alembic\&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge\&logo=docker\&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4CAF50?style=for-the-badge)
![Poetry](https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge\&logo=poetry\&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-FCC21B?style=for-the-badge&logo=ruff&logoColor=black)
![Mypy](https://img.shields.io/badge/mypy-checked-1f425f?style=for-the-badge)
![Sentry](https://img.shields.io/badge/Sentry-362D59?style=for-the-badge&logo=sentry&logoColor=white)

## 📌 Описание

**Schedule Bot** — это Telegram-бот для удобного просмотра школьного расписания ВМЛ.

Бот позволяет быстро получить актуальную информацию о занятиях и заменах без необходимости заходить на сайт школы.

⚠️ Бот является неофициальным

## 📊 Статистика и качество

🚀 Ботом уже пользуется **27+ человек**

🧪 Покрытие кода тестами: **78%**

🛠 **Качество кода:** проект проходит проверку **Ruff** (линтинг) и **Mypy** (статическая типизация)

📡 **Мониторинг:** Интеграция с **Sentry** для отслеживания ошибок в реальном времени

🔄 **CI/CD:** Автоматическое тестирование и линтинг при каждом Push (GitHub Actions)

## 📋 Требования
- Python 3.14
- Docker & Docker Compose
- Telegram Bot Token (получить в [@BotFather](https://t.me/BotFather))
- Telegram ID для админ-доступа

## 🎯 Возможности
- 📅 Просмотр расписания (сегодня, завтра, на неделю)
- 📍 Определение кабинета текущего урока
- ⏳ Подсчёт времени до следующего звонка
- 🔔 Уведомления о заменах в расписании
- 💬 Отправка отзывов и предложений
- ⚙️ Установка класса по умолчанию
- ⚡ Кэширование для быстрого доступа

## 🛠 Администрирование и управление
Закрытая админ-панель вызывается командой /admin и скрыта из общего меню.

**Возможности:**
- 📈 Статистика: Количество пользователей и распределение по классам
- 📩 Управление отзывами: Просмотр, удаление и ответы пользователям
- 📢 Рассылка классу: Отправка сообщений определённому классу
- 📢 Рассылка всем: Отправка сообщений всем пользователям
- 🔐 Безопасность: Доступ защищен по Telegram ID

**Доступ:** Укажите свой ID в `.env`: `ADMIN_ID=ваш_id`

## 🧠 Архитектура
Бот самостоятельно парсит расписание со школьного сайта, кэширует данные в Redis для оптимизации, отслеживает изменения и уведомляет пользователей об актуальных заменах. Все ошибки логируются через Sentry.

## ⚙️ Переменные окружения
```env
# Telegram
TOKEN=your_telegram_bot_token
ADMIN_ID=your_telegram_id

# База данных
DB_HOST=schedule-postgres
DB_PORT=5432
DB_NAME=schedule_db
DB_USER=schedule_user
DB_PASSWORD=your_secure_password

# Мониторинг (опционально)
SENTRY_DSN=https://your_sentry_dsn

# Прокси (опционально)
PROXY=http://proxy_url
VLESS_PROXY=vless://...
```

## 🚀 Запуск проекта

```bash
git clone https://github.com/ksredkin/schedule-bot.git
cd schedule-bot
cp .env.example .env
docker-compose up --build
```

**Настройка:** Отредактируйте .env файл (укажите ADMIN_ID, токен Telegram и т.д.).

## 📌 Пример ответа бота

```
🗓️ Расписание на сегодня (среда):

1. 📊 Вероятность и статистика — 08:00-08:40 | каб. 226

2. 🚀 Физика — 08:50-09:30 | каб. 122

3. 🧮 Алгебра — 09:40-10:20 | каб. 226

4. 🌍 География — 10:40-11:20 | каб. 125

5. 🇷🇺 Русский язык — 11:30-12:10 | каб. 133

6. 📚 Литература — 12:20-13:00 | каб. 133

7. 🏛️ История — 13:10-13:50 | каб. 223
```

## ⭐ Примечание

Проект сделан в учебных целях и для личного использования.

Если проект оказался полезным — можно поставить ⭐ на GitHub! 🚀