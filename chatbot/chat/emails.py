from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage

from threading import Thread

from chatbot.settings.production import *

EMAIL_DICT = {
    'send_bot_link': {
        'subject': 'First level start off for interview',
        'message': 'Click this link to get started: ',
        # 'template': '',
        # 'subject_template': '',
    }
}


def threadify(func, *args, **kwargs):
    """
    start 'fuc' as thread with *args and **kwargs
    """
    thread = Thread(target=func, args=args, kwargs=kwargs)
    thread.start()
    return thread
    # func(*args, **kwargs)


def _send_mail(to, context, subject, from_mail, body):
    """
    Low level wrapper for sending emails
    """

    send_mail(
        subject,
        body,
        from_mail,
        to,
        fail_silently=False,
    )

    # body = render_to_string(template, context)
    # msg = EmailMultiAlternatives(subject, from_mail, to)
    # msg.attach_alternative(body, 'text/html')
    # msg.send()


def email_chatbot_link(to, context, from_email=settings.DEFAULT_FROM_EMAIL):
    """
    Email messenger bot link to the candidate
    """

    # Please embed bot link in the template itself
    # template = EMAIL_DICT['send_bot_link']['template'] + bot_link
    message = EMAIL_DICT['send_bot_link']['message'] + context['bot_link']
    subject = EMAIL_DICT['send_bot_link']['subject']
    return threadify(_send_mail, to, context, subject, from_email, message)


def email_admins(session, from_email=settings.DEFAULT_FROM_EMAIL):
    if session.status == 'F':
        message = "Session with email {} and session_id {} does not want to take the application forward".format(
                                session.recipient_email,
                                session.id)
    else:
        message = "Session with email {} and session_id {} was cancelled".format(
                                session.recipient_email,
                                session.id)
    context = 'Session Cancellation occured'
    subject = "Session Cancellation occured."
    return threadify(_send_mail,
                     AIRCTO_ADMINS, context, subject, from_email, message)


def email_datasets():
    from datetime import datetime
    from_email = settings.DEFAULT_FROM_EMAIL
    message = "List of the datasets as on {}".format(datetime.now())
    subject = "Datasets"
    BASE_DIR = settings.BASE_DIR.split('/')
    length = len(BASE_DIR)
    excel_file_path = "/".join(BASE_DIR[:(length-1)]) + '/dataset'
    email = EmailMessage(
        subject,
        message,
        from_email,
        AIRCTO_ADMINS,
        )
    email.attach_file(excel_file_path)
    email.send()
