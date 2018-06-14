from django.conf import settings

from chat.helpers import *
from .medium import BaseMedium
import requests
import json
from django.urls import reverse
from chat.models import *


class Skype(object):
    """
    Skype medium through which chatbot can interact with user.
    """

    ACCESS_TOKEN_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    SKYPE_SCOPE = 'https://api.botframework.com/.default'
    # SKYPE_API_HOST = settings.SKYPE_API_HOST
    CONVERSATION_PATH = 'v3/conversations/'
    ACTIVITIES_PATH = '/activities/'
    OPTION_IMAGE_URL = 'http://www.commandpostgames.com/wp-content/uploads/2016/04/options.jpg'
    MAP_IMAGE_URL = 'https://www.google.com/permissions/images/maps-att.png'

    def _do_post(self, url, body, headers=None):
        response = requests.post(url, json=body, headers=headers)
        return response

    def parse_message(self, incoming_message):
        try:
            if incoming_message['type'] == 'message':
                return (incoming_message['conversation']['id'],
                        incoming_message['text'])
        except Exception as e:
            print(e)
            return None, None

    # TODO: (Anubhav)
    # Use me after every 1 hour. I expire after every one hour.
    def get_access_token(self):
        url = self.ACCESS_TOKEN_URL
        data = [
            ('grant_type', 'client_credentials'),
            ('client_id', settings.MICROSOFT_APP_ID),
            ('client_secret', settings.MICROSOFT_APP_SECRET),
            ('scope', 'https://api.botframework.com/.default'),
                ]
        response = requests.post(url, data=data, verify=False)
        return response.json()

    def get_message_url(self, incoming_message):
      if incoming_message.get('conversation_id'):
        service_url = settings.DEFAULT_MICROSOFT_SERVICE_URL
        postback_url = (service_url
                        + self.CONVERSATION_PATH
                        + incoming_message.get('conversation_id')
                        + self.ACTIVITIES_PATH)
      else:
        service_url = incoming_message.get('serviceUrl')
        postback_url = (service_url
                       + self.CONVERSATION_PATH
                       + incoming_message['conversation']['id']
                       + self.ACTIVITIES_PATH
                       + incoming_message.get('id'))
      return postback_url

    def create_text_message(self, incoming_message, message):
        if incoming_message.get('conversation_id'):
            reply_content = {"type": "message",
                             "from": {"id": "coding@MHJ65v_xIco"},
                             "text": message}
            return reply_content
        reply_content = {"type": "message",
                         "from": incoming_message.get('recipient'),
                         "recipient": incoming_message.get('from'),
                         "text": message,
                         "conversation": incoming_message.get('conversation'),
                         "replyToId": incoming_message.get('id')}
        return reply_content

    def send(self, incoming_message, message):
        """
        fetches access_token, creates access_token etc
        and posts to the postback_url.
        """
        postback_url = self.get_message_url(incoming_message)
        # For testing purposes headers have been omitted.
        token = SkypeToken.objects.filter(id=1).first().access_token
        headers = {"Authorization": "Bearer {}".format(token)}
        reply = self.create_text_message(incoming_message, message)
        response = self._do_post(postback_url, reply, headers=headers)

    def create_suggestion_message(self, incoming_message,
                                  message, suggestions):
        """
        Here suggestion is a list of values
        just like messenger's quick_replies.
        """
        suggestion_list = []
        for suggestion in suggestions:
            suggestion_action = {"type": "imBack",
                                 "value": suggestion,
                                 "title": suggestion}
            suggestion_list.append(suggestion_action)
        if incoming_message.get('conversation_id'):
            return suggestion_list

        reply_content = {"type": "message",
                         "from": incoming_message.get('recipient'),
                         "recipient": incoming_message.get('from'),
                         "text": message,
                         "inputHint": "expectingInput",
                         "conversation": incoming_message.get('conversation'),
                         "suggestedActions": {
                                "actions": suggestion_list},
                         "replyToId": incoming_message.get('id')}
        return reply_content

    def send_with_suggestion(self, incoming_message, message, suggestions):
        """
        Same as quick_replies in messenger platformself.
        """
        token = SkypeToken.objects.filter(id=1).first().access_token
        headers = {"Authorization": "Bearer {}".format(token)}
        reply = self.create_suggestion_message(incoming_message,
                                               message, suggestions)
        if incoming_message.get('conversation_id'):
            content = {"type": "message",
                       "from": {"id": "coding@MHJ65v_xIco"},
                       "text": message,
                       "suggestedActions": {
                            "actions": reply},
                       "inputHint": "expectingInput"}
            reply = content
        postback_url = self.get_message_url(incoming_message)
        response = self._do_post(postback_url, reply, headers)

    def create_attachment_message(self, incoming_message,
                                  message, attachments):
        reply_content = {
                "type": "message",
                "from": incoming_message.get('recipient'),
                "recipient": incoming_message.get('from'),
                "text": message,
                "attachments": attachments,
                "replyToId": incoming_message.get('id')
        }
        return reply_content

    def send_with_attachment(self, incoming_message, message, attachments):
        """
        Send messages with attachments. accepts a list of attachments.
        format of attachments.
        "attachments": [
        {
            "contentType": "image/png",
            "contentUrl": "http://aka.ms/Fo983c",
            "name": "duck-on-a-rock.jpg"
        }
        """
        token = SkypeToken.objects.first().access_token
        headers = {"Authorization": "Bearer {}".format(token)}
        postback_url = self.get_message_url(incoming_message)
        reply = self.create_attachment_message(incoming_message,
                                               message, attachments)
        response = self._do_post(postback_url, reply, headers)

    def create_speech_message(self, incoming_message, message):
        reply_content = {"type": "message",
                         "from": incoming_message.get('recipient'),
                         "recipient": incoming_message.get('from'),
                         "conversation": incoming_message.get('conversation'),
                         "text": message,
                         # "speak": "<emphasis level='moderate'>{}</emphasis>".format(message),
                         "speak": "Hi there",
                         "inputHint": "expectingHint",
                         "replyToId": incoming_message.get('id')}
        return reply_content

    def send_with_speech(self, incoming_message, message):
        token = SkypeToken.objects.first().access_token
        headers = {"Authorization": "Bearer {}".format(token)}
        postback_url = self.get_message_url(incoming_message)
        reply = self.create_speech_message(incoming_message, message)
        response = self._do_post(postback_url, reply, headers=headers)

    def create_button_message(self, incoming_message, message, buttons):
        button_list = []
        for button in buttons:
            button_list.append({"type": "imBack",
                                "title": button,
                                "value": button})

        reply_content = {"type": "message",
                         "from": incoming_message.get('recipient'),
                         "recipient": incoming_message.get('from'),
                         "conversation": incoming_message.get('conversation'),
                         "text": message,
                         "replyToId": incoming_message.get('id'),
                         "attachmentLayout": "list",
                         "attachments": [
                            {"contentType": "application/vnd.microsoft.card.thumbnail",
                             "content": {
                                "buttons": button_list
                             }}
                         ]}
        return reply_content

    def send_with_button(self, incoming_message, message, buttons):
        """
        accepts buttons as list and sends them e.g. buttons = ['Hi', 'Bye']
        """
        token = SkypeToken.objects.first().access_token
        headers = {"Authorization": "Bearer {}".format(token)}

        postback_url = self.get_message_url(incoming_message)
        reply = self.create_button_message(incoming_message, message, buttons)
        response = self._do_post(postback_url, reply, headers)

    def create_conversation_message(self, topic_name, members):
        message_content = {
            "bot": {
                "id": settings.BOT_ID,
                "name": settings.BOT_NAME
            },
            "isGroup": false,
            "members": members,
            "topicName": topic_name
        }
        return message_content

    def start_conversation(self, topic_name, members):
        """
        Here members is a list of members having dict specifying the `id`
        and the `name` of the recipient
        """
        token = SkypeToken.objects.first().access_token
        headers = {"Authorization": "Bearer {}".format(token)}
        # The one specified for the webhook in the bot framework.
        conversation_url = settings.MICROSOFT_API_HOST + self.CONVERSATION_PATH
        message = self.create_conversation_message(topic_name, members)
        response = self._do_post(conversation_url, message, headers=headers)

    def get_webview_url(self, session):
        if session.state.question.question_type == 'checkboxes':
            url = settings.API_HOST + reverse('chat:webview', kwargs={
                                     'recipient_id': session.recipient_id})
            # url = "https://e3ccc59a.ngrok.io/chat/webview/{}".format(
                    # session.recipient_id)
            title = 'View Options'
            return url, title, self.OPTION_IMAGE_URL
        url = settings.API_HOST + reverse('chat:maps', kwargs={
                                     'recipient_id': session.recipient_id})
        # url = "https://e3ccc59a.ngrok.io/chat/maps/{}".format(
        #             session.recipient_id)
        title = "Share your Location"
        return url, title, self.MAP_IMAGE_URL

    def create_hero_card_message(self, incoming_message, message):
        attachment_list = []
        # attachment list contains items like title, subtitle, description, url etc.
        conversation_id = incoming_message.get('conversation_id')
        if not conversation_id:
            conversation_id = incoming_message.get('conversation')['id']
        session = Session.objects.filter(recipient_id=conversation_id,
                                         is_active=True).first()
        post_url, title, image_url = self.get_webview_url(session)
        content = {"contentType": "application/vnd.microsoft.card.hero",
                   "contentUrl": post_url,
                   "thumbnailUrl": post_url,
                   "content": {
                        "title": title,
                        "subtitle": "subtitle goes here",
                        "text": "Descriptive text goes here",
                        "images": [
                            {
                                "url": image_url,
                                "alt": "Hero Card",
                                "tap": {
                                    "type": "openUrl",
                                    "value": post_url
                                }}],
                        "buttons": [
                            {
                                "type": "openUrl",
                                "title": title,
                                "value": post_url
                            }]}}
        attachment_list.append(content)
        if incoming_message.get('conversation_id'):
            return attachment_list
        message_content = {"type": "message",
                           "from": incoming_message.get('recipient'),
                           "conversation": incoming_message.get(
                                                'conversation'),
                           "recipient": incoming_message.get('from'),
                           "attachments": attachment_list,
                           "replyToId": incoming_message.get('id'),
                           "text": message
                           }
        return message_content

    def send_with_hero_card(self, incoming_message, message):
        """
        Sends hero cards which contain image attachment and
        buttons which are linked to certain in app urls
        """
        token = SkypeToken.objects.filter(id=1).first().access_token
        headers = {"Authorization": "Bearer {}".format(token)}
        reply = self.create_hero_card_message(incoming_message, message)
        if incoming_message.get('conversation_id'):
            content = {"type": "message",
                       "from": {"id": "coding@MHJ65v_xIco"},
                       "text": message,
                       "attachments": reply}
            reply = content
            service_url = 'https://webchat.botframework.com/'
        postback_url = self.get_message_url(incoming_message)
        response = self._do_post(postback_url, reply, headers)

    def send_contact_add_message(self, incoming_message, message):
      """
      Sends a text message to the user when the bot
      has been added to the contacts.
      Asking for verification code
      """
      postback_url = self.get_message_url(incoming_message)
      token = SkypeToken.objects.first().access_token
      headers = {"Authorization": "Bearer {}".format(token)}
      reply = self.create_text_message(incoming_message, message)
      response = self._do_post(postback_url, reply, headers=headers)

    def verify_skype_code(self, recipient_id, user_input):
      """
      Verifies the code sent by the user via messages.
      Greeting text for skype is sent from here.
      """
      if Session.objects.filter(recipient_id=recipient_id,
                                is_active=True, status='P').exists():
        return True
      else:
        try:
          # IMPROVEMENTS MIGHT BE REQUIRED HERE.
          applicant_id, tree_id, email = decode(user_input)
          session = Session.objects.filter(tree=tree_id,
                      recipient_email=email, is_active=True).first()
          session.recipient_id = recipient_id
          session.status = 'P'
          session.medium = 'skype'
          session.save()
          return True
        except (TypeError, NameError,
                UnicodeDecodeError, ValueError):
          return False
