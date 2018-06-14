from django.utils.html import strip_tags

from chat.models import Session
from chat.helpers import *


class WebChat(object):
    """
    WebChat Messenger medium through which chatbot can interact with user.
    """

    def __init__(self):
        pass

    def get_status(self, obj):
        if obj == 'P':
            return 'In-Process'
        elif obj == 'C':
            return 'Completed'
        else:
            return 'Some Error Occured'

    def get_active_session(self, recipient_id):
        session = Session.objects.filter(recipient_id=recipient_id,
                                         medium='webchat',
                                         is_active=True).first()
        return session

    def get_recipient_email_and_tree(self, referral):
        return decode(referral)

    def get_new_session(self, recipient_email, tree, recipient_id):
        session = Session.objects.filter(recipient_id='', status='L',
                                         recipient_email=recipient_email,
                                         is_active=True).first()
        if session:
            session.recipient_id = recipient_id
            session.status = 'P'
            session.medium = 'webchat'
            session.save()
        return session

    def get_session(self, payload):
        if strip_tags(payload.get('text')) == 'Get Started':
            referral = payload.get('referral')
            applicant_id, tree, recipient_email = self.get_recipient_email_and_tree(referral)
            session = self.get_new_session(recipient_email,
                                           tree, payload.get('recipient_id'))
            return session

        if strip_tags(payload.get('text')) == 'Resume':
            session = self.get_active_session(payload.get('recipient_id'))
            return session

        if strip_tags(payload.get('type')) == 'message':
            session = self.get_active_session(payload.get('recipient_id'))
            return session

    def send_with_quick_reply(self, recipient_id, message, quick_replies,
                              status):
        replies = []
        for msg in quick_replies:
            replies.append({"content_type": "text", "text": msg})
        payload = {
            "recipient_id": recipient_id,
            "message": {
                "text": message,
                "quick_replies": replies
            },
            "status": self.get_status(status)
        }
        return payload

    def send_text(self, recipient_id, message, status):
        payload = {
            "recipient_id": recipient_id,
            "message": {
                "text": message
            },
            "status": self.get_status(status)
        }
        return payload

    def get_options(self, session):
        options = []
        transitions = Transition.objects.filter(current_state=session.state,
                                                tree=session.tree)
        for transition in transitions:
            options.append(transition.answer.text)
        return options

    def get_title_and_options(self, session):
        if session.state.question.question_type == 'checkboxes':
            options = self.get_options(session)
            title = "View Options"
            return title, options
        title = "Share your Location"
        return title, None

    def send_with_button(self, recipient_id, message, status):
        session = Session.objects.filter(recipient_id=recipient_id,
                                         is_active=True,
                                         medium='webchat').first()
        title, options = self.get_title_and_options(session)
        payload = {
            "status": self.get_status(status),
            "recipient_id": recipient_id,
            "message": {
                "text": message,
                "attachment": {
                    "type": "template",
                    "template_type": "button",
                    "buttons": [
                        {"type": "checkboxes",
                         "title": title,
                         "options": options}]}}}
        return payload

    def parse_message():
        pass
