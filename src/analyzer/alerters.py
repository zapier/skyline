from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import requests
from smtplib import SMTP

import alerters
import settings


"""
Create any alerter you want here. The function will be invoked from trigger_alert.
Two arguments will be passed, both of them tuples: alert and metric.

alert: the tuple specified in your settings:
    alert[0]: The matched substring of the anomalous metric
    alert[1]: the name of the strategy being used to alert
    alert[2]: The timeout of the alert that was triggered
metric: information about the anomaly itself
    metric[0]: the anomalous value
    metric[1]: The full name of the anomalous metric
"""


def alert_smtp(alert, metric):

    # For backwards compatibility
    if '@' in alert[1]:
        sender = settings.ALERT_SENDER
        recipient = alert[1]
    else:
        sender = settings.SMTP_OPTS['sender']
        recipients = settings.SMTP_OPTS['recipients'][alert[0]]

    # Backwards compatibility
    if type(recipients) is str:
        recipients = [recipients]

    for recipient in recipients:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '[skyline alert] ' + metric[1]
        msg['From'] = sender
        msg['To'] = recipient
        link = settings.GRAPH_URL % (metric[1])
        body = 'Anomalous value: %s <br> Next alert in: %s seconds <a href="%s"><img src="%s"/></a>' % (metric[0], alert[2], link, link)
        msg.attach(MIMEText(body, 'html'))
        s = SMTP('127.0.0.1')
        s.sendmail(sender, recipient, msg.as_string())
        s.quit()

def alert_webhook(alert, metric):
    url = settings.WEBHOOK_OPTS.get('url')
    if url:
        requests.post(
            url,
            data={
                'metric': metric[1],
                'value': metric[0],
                'graph': settings.GRAPH_URL.format(metric[1]),
            },
        )


def trigger_alert(alert, metric):

    if '@' in alert[1]:
        strategy = 'alert_smtp'
    else:
        strategy = 'alert_' + alert[1]

    getattr(alerters, strategy)(alert, metric)
