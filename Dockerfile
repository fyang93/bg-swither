FROM python:3.9-slim AS run-stage

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]