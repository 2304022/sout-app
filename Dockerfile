FROM python:3.12-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
RUN mkdir -p /data
ENV DATABASE_URL=sqlite:////data/sout.db
# Порт приложения и флаг демо-данных параметризуются (переопределяются в compose)
ENV APP_PORT=5680
ENV SEED_DEMO_DATA=false
EXPOSE 5680 5681
# shell-форма CMD нужна для подстановки ${APP_PORT}
CMD uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-5680}
