# Stage 1: Устанавливаем зависимости
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем нужный часовой пояс
RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime && echo "Europe/Moscow" > /etc/timezone

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВСЕ файлы проекта
COPY . .

# Команда для запуска приложения
CMD ["sh", "-c", "sleep 5 && python main.py"]
