FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
&&  apt-get install -y tzdata \
&&  ln -fs /usr/share/zoneinfo/America/Mexico_City /etc/localtime \
&&  dpkg-reconfigure --frontend noninteractive tzdata

RUN apt-get install libssl-dev

#RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

#COPY id_ed25519 /root/.ssh/id_ed25519

#RUN chmod 600 /root/.ssh/id_ed25519

#RUN echo "Host github.com\n\tStrictHostKeyChecking no\n" >> /root/.ssh/config

WORKDIR /app

#COPY . .

#RUN git clone --depth 1  git@github.com:TenergyMX/SIA.git .

#RUN pip install --upgrade pip

#RUN git pull

COPY . .

#RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py collectstatic --no-input

#ENV DATABASE_ADDRESS=

CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]