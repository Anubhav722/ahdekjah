import requests

from django.conf import settings
from django.urls import reverse

from .medium import BaseMedium

from pymessenger.bot import Bot
from chat.models import Session
import json

from geopy.geocoders import Nominatim


class Facebook(BaseMedium):
    """
    Facebook Messenger medium through which chatbot can interact with user
    """

    MESSENGER_PATH = 'http://m.me/'
    GRAPH_FACEBOOK_PATH = 'https://graph.facebook.com/'
    API_VERSION = 'v2.6'
    MESSENGER_PROFILE_PATH = '/me/messenger_profile?'
    SEND_MESSAGE_URL = "/me/messages/"

    def __init__(self, access_token):
        self.access_token = access_token
        self.bot = Bot(self.access_token)

    def generate_messenger_share_link(self):
        bot_link = self.MESSENGER_PATH + settings.CHATBOT_FB_PAGE_ID
        return bot_link

    # FIXME: Please store the user info one-time and don't use me again
    def get_facebook_user_info(self, fbid):
        try:
            facebook_user_info = self.bot.get_user_info(fbid)
            return facebook_user_info
        except Exception as e:
            print('Failed to fetch FB user info %s' % e)
            return {"first_name": "there"}

    def send(self, recipient_id, message):
        response = ''
        while response == '':
            try:
                response = self.bot.send_text_message(recipient_id, message)
            except:
                from time import sleep
                print('Sleep time')
                sleep(5)
                print('Slept enough')
                continue

    def get_message_url(self):
        return self.GRAPH_FACEBOOK_PATH + "/" + self.API_VERSION + self.SEND_MESSAGE_URL + "?access_token="+ self.access_token

    def send_typing_on(self, recipient_id):
        """
        This will send payload to facebook api to mimic that bot is typing.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/sender-actions
        """
        self._do_post(self.get_message_url(), {'recipient':
                      {"id": recipient_id}, "sender_action": "typing_on"})

    def send_typing_off(self, recipient_id):
        self._do_post(self.get_message_url(), {'recipient':
                      {"id": recipient_id}, "sender_action": "typing_off"})

    def get_webview_url(self, session):
        if session.state.question.question_type == 'checkboxes':
            url = settings.API_HOST + reverse('chat:webview',
                                              kwargs={
                                               'recipient_id':
                                               session.recipient_id})
            # url = 'https://07ca4643.ngrok.io' + reverse('chat:webview', kwargs={
            #                                     'recipient_id': session.recipient_id})
            title = "View Options"
            return url, title
        url = settings.API_HOST + reverse('chat:maps', kwargs={
                                          'recipient_id':
                                          session.recipient_id})
        # url = 'https://07ca4643.ngrok.io' + reverse('chat:maps', kwargs={
        #                                         'recipient_id': session.recipient_id})
        title = "Share your Location"
        return url, title

    def send_with_button(self, recipient_id, message):
        """
        Send a button along with message. Clicking on the button opens up a webview.
        Users can select their preferences from there.
        """
        session = Session.objects.filter(recipient_id=recipient_id,
                                         is_active=True).first()
        url, title = self.get_webview_url(session)

        headers = {'Content-Type': 'application/json',
                   'X-Frame-Options': 'ALLOW-FROM https://www.messenger.com/'}

        message = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": message,
                    "buttons": [
                        {
                          "type": "web_url",
                          "title": title,
                          "url": url,
                          "webview_height_ratio": "tall",
                          "messenger_extensions": True
                        }]
                }}}
        response_msg = {"recipient": {"id": recipient_id}, "message": message}
        url = self.get_message_url()
        return self._do_post(url, response_msg, headers=headers)

    def send_with_quick_reply(self, recipient_id, message, quick_replies):
        """
        Behaves exactly like send. except it accept quick replies as list of strings.
        """
        url = self.get_message_url()
        replies = []

        # here we are adding both title and payload as user input for simplicity.
        for msg in quick_replies:
            replies.append({"content_type": "text",
                            "title": msg, "payload": msg})
        payload = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message,
                "quick_replies": replies,
            }
        }
        return self._do_post(url, payload)

    def send_location_with_quick_reply(self, recipient_id, message,
                                       quick_replies):
        """
        Share location on google maps
        """
        url = self.get_message_url()

        payload = {
            "recipient":{
            "id":recipient_id
            },
        "message":{
        "text": message,
        "quick_replies":[
            {
            "content_type":"location",
            }]}
        }
        return self._do_post(url, payload)

    def _do_post(self, url, body, headers=None):
        res = ''
        while res == '':
            try:
                res = requests.post(url, json=body, headers=headers)
                return res
            except:
                from time import sleep
                sleep(5)
                continue

    def get_referral(self, payload):
        payload = json.loads(payload)
        entry = payload.get('entry', [])
        if not entry:
            return None, None

        # standby = entry[0].get('standby', [])
        # if standby:
        #     referral = standby[0].get('postback').get('referral', [])
        #     recipient_id = standby[0].get('sender', []).get('id', [])
        #     return recipient_id, referral

        message = entry[0].get('messaging', [])
        if not message:
            return None, None

        message = message[0]
        recipient_id = message['sender']['id']

        if 'referral' in message:
            return recipient_id, message['referral']

        if ('postback' in message) and ('referral' in message['postback']):
            return recipient_id, message['postback']['referral']

        return None, None

    def extract_location_from_coordinates(self, coordinates):
        coordinate = str(coordinates['lat']) + ", " + str(coordinates['long'])
        geolocator = Nominatim()
        location = geolocator.reverse(coordinate)
        location_address = location.address
        return location_address

    def parse_message(self, incoming_message):
        try:
            incoming_message = json.loads(incoming_message)
            for entry in incoming_message.get('entry', []):
                if not entry.get('messaging'):
                    return None, None
                for message in entry.get('messaging', []):
                    if 'message' in message and not message['message'].get(
                            'text') == None:
                        return (message['sender']['id'],
                                message['message']['text'])
                    elif 'postback' in message:
                        return (message['sender']['id'],
                                message['postback']['payload'])
                    elif 'message' in message and message['message'].get(
                            'text') == None:
                        return None, None
                        # location = self.extract_location_from_coordinates(message['message']['attachments'][0]['payload']['coordinates'])
                        # return (message['sender']['id'], location)
                    else:
                        return None, None
        except Exception as e:
            print (e)
