# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir pygame

# Копируем файлы проекта
COPY main.py .
COPY sudoku.py .
COPY *.py ./

# Указываем команду для запуска
CMD ["python", "main.py"]
