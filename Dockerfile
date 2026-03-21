FROM python:3.11
WORKDIR /app
RUN pip install --no-cache-dir pygame
COPY sudoku.py .
CMD ["python", "sudoku.py"]