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

## 📌 Описание

Schedule Bot — это Telegram-бот для удобного просмотра школьного расписания ВМЛ.

Бот позволяет быстро получить актуальную информацию о занятиях и заменах без необходимости заходить на сайт школы.

⚠️ Бот является неофициальным

## 📊 Статистика и качество

🚀 Ботом уже пользуется **27+ человек**

🧪 Покрытие кода тестами: **63%**

📈 Проект находится в активной разработке и продолжает расти

## 🎯 Возможности
- 📅 Просмотр расписания на сегодня
- 🗓 Просмотр расписания на неделю
- 📆 Просмотр расписания на завтра
- 📍 Определение кабинета текущего урока
- ⏳ Подсчёт времени до следующего звонка
- 🔔 Уведомления о заменах
- ⚙️ Установка класса по умолчанию
- ⚡ Кэширование расписания для ускорения работы
- 🛠 Панель администратора (мониторинг пользователей и статистики)

## 🧠 Как работает
1. Бот отправляет запрос к сайту школы
2. Получает HTML-страницу с расписанием или CSV с заменами
3. Парсит данные с помощью BeautifulSoup
4. Преобразует их в структурированный формат
5. Кэширует данные в Redis для ускорения работы и снижения нагрузки
6. Сравнивает изменения и отправляет обновления пользователям
7. Отправляет пользователю готовый ответ

## 🚀 Запуск проекта
### 1. Клонирование
```bash
git clone https://github.com/ksredkin/schedule-bot.git
cd schedule-bot
```

### 2. Настройка окружения
```bash
cp .env.example .env
nano .env
```

### 3. Запуск тестов
Для проверки стабильности системы перед запуском:

```bash
pytest
```

### 4. Запуск через Docker
```bash
docker-compose up --build
```

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