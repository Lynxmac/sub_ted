FROM python:2.7

RUN apt-get update

ENV PYTHONPATH /usr/src/app/
ENV DJANGO_SETTINGS_MODULE subted.setting
ENV DEBUG True

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app/
ADD requirements.txt /usr/src/app/
RUN pip2 install -r requirements.txt

CMD python manage.py runserver 0.0.0.0:8000