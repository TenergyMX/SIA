FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
&&  apt-get install -y tzdata \
&&  ln -fs /usr/share/zoneinfo/America/Mexico_City /etc/localtime \
&&  dpkg-reconfigure --frontend noninteractive tzdata

WORKDIR /app

COPY . .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py collectstatic --no-input

CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]