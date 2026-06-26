FROM python:3.12-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
RUN mkdir -p /data
ENV DATABASE_URL=sqlite:////data/sout.db
EXPOSE 5680
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5680"]
