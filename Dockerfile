FROM python:3.12-slim

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"]