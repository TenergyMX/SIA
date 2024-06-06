import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template.loader import render_to_string
from decouple import config

def enviar_correo(subject, to_emails, template, datos=None):
    """
    Envía un correo electrónico utilizando una plantilla HTML.
    """
    try:
        # Configurar el correo electrónico
        msg = MIMEMultipart()
        msg['From'] = config('EMAIL_HOST_USER')
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject

        # Adjuntar el contenido HTML del correo electrónico utilizando una plantilla Django
        context = {'RUTA_URL': 'http://192.168.100.221/', 'token': '1234'}
        if datos is not None:
            token = datos.get('token', '1234')
            context['token'] = token
            context["base_url"] = datos.get("base_url")
        message_html = render_to_string('mail/' + template, context)
        msg.attach(MIMEText(message_html, 'html'))

        # Establecer la conexión con el servidor SMTP y enviar el correo
        with smtplib.SMTP_SSL(config('EMAIL_HOST'), int(config('EMAIL_PORT'))) as server:
            server.login(config('EMAIL_HOST_USER'), config('EMAIL_HOST_PASSWORD'))
            server.sendmail(config('EMAIL_HOST_USER'), to_emails, msg.as_string())

        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}