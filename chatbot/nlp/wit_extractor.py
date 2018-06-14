from django.utils.html import strip_tags
from django.conf import settings

import json

from wit import Wit


class WitExtractor(object):

    def __init__(self):
        self.client = Wit(settings.WIT_SERVER_ACCESS_TOKEN)

    def get_datetime(self, payload):
        """
        Fetch datetime from the payload.
        """
        if not type(payload) == dict:
            payload = json.loads(payload)
        datetime = payload['entry'][0]['messaging'][0].get(
                    'message')['nlp']['entities'].get(
                    'datetime', False)
        if datetime:
            datetime_value = datetime[0].get('value', False)
            datetime_type = 'datetime'
            if not datetime_value:
                datetime_value = datetime[0].get('from').get('value', False)
                datetime_type = datetime[0].get('type', False)
                if datetime_value:
                    return datetime_value, datetime_type
            else:
                return datetime_value, datetime_type
        return False, None

    def get_duration(self, payload):
        """
        Fetch datetime, time duration in hours, days, months, years, etc.
        """
        if not type(payload) == dict:
            payload = json.loads(payload)
        duration = payload['entry'][0]['messaging'][0].get(
                    'message')['nlp']['entities'].get(
                    'duration', False)

        if not duration:
            datetime_value, datetime_type = self.get_datetime(payload)
            if not datetime_value:
                number = self.get_numbers(payload)
                if type(number) == int or type(number) == float:
                    return number, None
            return datetime_value, datetime_type

        notice_period_value = payload['entry'][0]['messaging'][0].get(
                                'message')['nlp']['entities'].get(
                                'duration', False)[0].get(
                                'value', False)
        notice_period_unit = payload['entry'][0]['messaging'][0].get(
                                'message')['nlp']['entities'].get(
                                'duration', False)[0].get(
                                'unit', False)
        return notice_period_value, notice_period_unit

    def get_numbers(self, payload):
        """
        Fetches numbers as in 1, 1k, 1 million, etc
        """
        if not type(payload) == dict:
            payload = json.loads(payload)
        number = payload['entry'][0]['messaging'][0].get(
                    'message')['nlp']['entities'].get(
                    'number', False)
        if not number:
            return False
        return number[0].get('value', False)

    def extract_wit_values(self, message, validation_type):
        """
        extract wit values from the text.
        """
        message = strip_tags(message)
        extracted_info = self.client.message(message)
        if validation_type == 'ctc_inr':
            return self.extract_numbers(extracted_info)
        if (validation_type == 'notice_period' or
                validation_type == 'work_experience'):
            return self.extract_duration(extracted_info)

    def extract_datetime(self, message):
        """
        extracts datetime by making a call to wit.ai externally.
        """
        if not message['entities'].get('datetime'):
            return False, None
        datetime = message['entities'].get('datetime')
        datetime_value = datetime[0].get('value', False)
        datetime_type = 'datetime'
        if not datetime_value:
            datetime_value = datetime[0].get('from').get('value', False)
            datetime_type = datetime[0].get('type', False)
            if datetime_value:
                return datetime_value, datetime_type
        else:
            return datetime_value, datetime_type
        return False, None

    def extract_duration(self, message):
        """
        extracts duration by making a call to wit.ai externally.
        """
        if not message['entities'].get('duration'):
            datetime_value, datetime_type = self.extract_datetime(message)
            if not datetime_value:
                number = self.extract_numbers(message)
                if type(number) == int or type(number) == float:
                    return number, None
            return datetime_value, datetime_type

        duration_period_value = message['entities'].get(
                                 'duration')[0].get('value')
        duration_period_unit = message['entities'].get(
                                 'duration')[0].get('unit')
        return duration_period_value, duration_period_unit

    def extract_numbers(self, message):
        """
        extracts numbers from the text by making a call to wit.ai externally.
        """
        if not message.get('entities'):
            return False
        try:
            return message.get('entities')['number'][0]['value']
        except KeyError:
            # NOTE
            # This case arises when people enter salary range as 10-12
            # which wit.ai renders as datetime
            # We will be taking the lower range.
            try:
                number_range = message.get('entities').get(
                                'datetime')[0]['value'].split('-')
                lower_range = int(number_range[1])
                # higher_range = number_range[2][:2]
                return lower_range
            except TypeError:
                try:
                    number = message.get('entities').get('duration')[0]['value']
                    return number
                except Exception as e:
                    print("WHAT THE FUDGE")
                    print(e)
                    return False
