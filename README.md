# 🤖 SugarCheckBot

SugarCheckBot — это Telegram-бот, который помогает пользователям не забыть сделать забор крови после еды.  
Бот запрашивает время приема пищи и отправляет напоминание через указанное время.

## 📌 Основные возможности

- Запрос времени последнего приема пищи.
- Установка напоминания о необходимости сделать забор крови.
- Возможность остановки напоминаний.
- Поддержка работы в Docker.

---

## 🛠️ Технологии

- **Язык**: Python 3.11
- **Библиотеки**:
  - [aiogram](https://docs.aiogram.dev/en/latest/) (работа с Telegram API)
  - [APScheduler](https://apscheduler.readthedocs.io/en/latest/) (планировщик задач)
  - [dotenv](https://pypi.org/project/python-dotenv/) (загрузка переменных окружения)
  - [asyncio](https://docs.python.org/3/library/asyncio.html) (асинхронное выполнение)

---

## 🚀 Установка и запуск

### 1️⃣ **Локальный запуск (без Docker)**

#### **Требования**:
- Python 3.11+
- Установленный `pip`

#### **Шаги установки**:

```bash
# 1. Клонируем репозиторий
git clone https://github.com/ВАШ_НИК/sugarcheckbot.git
cd sugarcheckbot

# 2. Создаем виртуальное окружение и активируем его
python -m venv venv
source venv/bin/activate  # Для Linux/Mac
venv\Scripts\activate  # Для Windows

# 3. Устанавливаем зависимости
pip install -r requirements.txt

# 4. Создаем .env файл с токеном бота (см. раздел ниже)

# 5. Запускаем бота
python main.py


2️⃣ Запуск через Docker
Требования:
Установленный Docker и Docker Compose
Шаги:
Создаем .env файл (см. ниже).
Собираем образ и запускаем контейнер:
bash

docker-compose up -d --build
Бот запустится в фоновом режиме. Проверить логи можно командой:
bash

docker logs -f shugarcheckbot_backend_1
Остановить контейнер:
bash

docker-compose down

🔧 Настройка переменных окружения (.env)
Перед запуском бота создайте файл .env в корневой папке и добавьте туда токен бота:
TELEGRAM_TOKEN=ВАШ_ТОКЕН_БОТА
Вы можете получить токен, создав бота через BotFather в Telegram.


📄 Файлы и структура проекта
bash

/shugarcheckbot
│── /app/                    # Основной код бота
│   ├── keyboards.py         # Клавиатуры для Telegram
│   ├── commands.py          # Команды бота
│   ├── main.py              # Точка входа (запуск бота)
│── /logs/                   # Логи работы
│── .env                     # Переменные окружения
│── Dockerfile               # Файл для создания Docker-образа
│── docker-compose.yml       # Конфигурация для Docker Compose
│── requirements.txt         # Список зависимостей
│── README.md                # Описание проекта



🛠 Полезные команды Docker
Пересобрать образ и перезапустить контейнер:

bash

docker-compose up -d --build
Остановить и удалить контейнеры:

bash

docker-compose down
Посмотреть логи контейнера в реальном времени:

bash

docker logs -f shugarcheckbot_backend_1
Зайти в контейнер для отладки:

bash

docker exec -it shugarcheckbot_backend_1 bash
