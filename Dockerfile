FROM python:3.8

ENV PYTHONUNBUFFERED 1
RUN mkdir /code

WORKDIR /code
COPY . /code/

RUN python -m pip install -r src/requirements.txt
RUN python src/manage.py makemigrations
RUN python src/manage.py migrate
RUN python src/manage.py collectstatic --noinput

CMD ["gunicorn", "-c", "config/gunicorn/conf.py", "--bind", "0.0.0.0:8000", "--chdir", "src", "net_sync.wsgi:application"]