FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=7860

CMD ["python", "app.py"]
