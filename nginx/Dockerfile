FROM public.ecr.aws/docker/library/python:3.10
FROM public.ecr.aws/docker/library/nginx

#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED=1

WORKDIR /

COPY ./certbot /var/www/certbot
COPY ./certbot/letsencrypt /etc/letsencrypt

RUN apt-get update \
&&  apt-get install -y tzdata \
&&  ln -fs /usr/share/zoneinfo/America/Mexico_City /etc/localtime \
&&  dpkg-reconfigure --frontend noninteractive tzdata

COPY ./default.conf /etc/nginx/conf.d/default.conf

RUN apt-get install -y certbot
RUN apt-get install -y python3-certbot-nginx
