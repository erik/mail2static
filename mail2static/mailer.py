from smtplib import SMTP_SSL
from email.mime.text import MIMEText


def _smtp_client(config):
    # TODO: probably a bit more dispatching here.
    return SMTP_SSL(config['host'], config['port'])


def _smtp_login(config, client):
    client.login(config['email'], config['password'])


def send_text_email(config, to_addr, subject, body):
    msg = MIMEText(body)
    msg['From'] = config['email']
    msg['To'] = to_addr
    msg['Subject'] = subject

    with _smtp_client(config) as client:
        _smtp_login(config, client)
        client.send_message(msg)
        client.quit()
