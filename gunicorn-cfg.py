#gunicorn -*- encoding: utf-8 -*-
import multiprocessing

wsgi_app = "core.wsgi:application"

workers = multiprocessing.cpu_count() * 2 + 1

bind = "0.0.0.0:8000"

reload = True

#accesslog = "/app/access.log"

#errorlog = "/app/error.log"

#capture_out = True

#daemon = True

loglevel = 'debug'

app_module = "core.settings"