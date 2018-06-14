from django.utils.html import strip_tags
from django.conf import settings

from nlp.wit_extractor import WitExtractor
from geopy.geocoders import Nominatim
# from .models import StructuredAnswer
from .constants import *
from .helpers import *
import json
# import re

value = ''
unit = ''


class StructuredAnswerConverter(object):
    """
    Extracts structured data from the raw user_input.
    """

    def __init__(self):
        self.wit = WitExtractor()

    def convert_fetched_CTC(self, payload, qa_instance):
        value, unit = None, None
        if payload.get('medium') == 'webchat' or payload.get('channelId') == 'skype':
            value = self.wit.extract_wit_values(payload.get('text'), 'ctc_inr')
        else:
            value = self.wit.get_numbers(payload)

        if value:
            for ctc_format in CTC_FORMAT_INR:
                if ctc_format in qa_instance.answer:
                    unit = ctc_format
                    break
        if not value or not unit:
            ctc_extension = check_validation_extension(qa_instance.answer)
            if ctc_extension:
                value = 0.0
                unit = 'lac'
            else:
                try:
                    if settings.STORE_UNSTRUCTURED_ANSWER:
                        session = qa_instance.session_set.first()
                        value = float(session.temporary_validation.split()[0])
                    else:
                        value = float(qa_instance.answer.split()[0])
                    unit = 'lac'
                except (ValueError, IndexError):
                    value = None
                    unit = None

        if unit in ['lac', 'lpa', 'lakh']:
            value *= 100000
        if unit in ['crore', 'cpa']:
            value *= 10000000
        return str(value)

    def convert_fetched_duration(self, payload, qa_instance):
        if payload.get('medium') == 'webchat' or payload.get('channelId') == 'skype':
            value, unit = self.wit.extract_wit_values(
                            payload.get('text'), 'notice_period')
        else:
            value, unit = self.wit.get_duration(payload)

        if (check_validation_extension(qa_instance.answer) and
                value == False):
            value = 0.0
            unit = 'days'

        if settings.STORE_UNSTRUCTURED_ANSWER:
            session = qa_instance.session_set.first()
            if session.temporary_validation:
                try:
                    value = float(session.temporary_validation.split()[0])
                    unit = session.temporary_validation.split()[1]
                except ValueError:
                    value = session.temporary_validation.split()[0]
                    unit = 'datetime'
        if str(value) == 'False' or not unit:
            if not qa_instance.answer in ['yes', 'no']:
                if not len(qa_instance.answer) == 10:
                    try:
                        value = float(qa_instance.answer.split()[0])
                        unit = qa_instance.answer.split()[1]
                    except (ValueError, IndexError):
                        # if not str(value):
                        # value = qa_instance.answer
                        value = None
                        unit = None

        if unit in ['week', 'weeks']:
            value *= 7
        if unit in ['year', 'years']:
            value *= 365
        if unit in ['month', 'months']:
            value *= 30

        if len(str(value)) == 10:
            return str(value)
        return value

    def get_location(self, answer):
        geolocator = Nominatim()
        location = geolocator.geocode(answer, addressdetails=True, timeout=20)
        if location:
            geo_loc = location.raw.get('address').get('city')
            if not geo_loc:
                geo_loc = location.raw.get('address').get('state_district')
            return geo_loc
        else:
            return answer.split(',')[0]

    def convert_fetched_rating(self, qa_instance):
        sentence = qa_instance.answer.split()
        for word in sentence:
            if word in RATING.keys():
                return RATING[word]

    def get_structured_data(self, session, payload):
        qa_instance = session.question_answer_pair.last()
        question_instance = session.state.question
        if not type(payload) == dict:
            try:
                payload = json.loads(payload)
            except Exception as e:
                print(e)

        if not question_instance.validation_type:
            return {'entity': '', 'unit': '', 'value': ''}

        # There can be multiple numbers in the text.
        # Saving it according to the question instance right now.
        if question_instance.validation_type == 'ctc_inr':
            value = self.convert_fetched_CTC(payload, qa_instance)
            entity = 'current_ctc_inr'
            if not 'current' in question_instance.text:
                entity = 'expect_ctc_inr'
            if value == 'None':
                return None
            value = value
            if type(value) == str:
                value = value.lower()
            return {'entity': entity, 'unit': 'inr', 'value': value}

        if (question_instance.validation_type in
                ['notice_period', 'work_experience']):
            value = self.convert_fetched_duration(payload, qa_instance)
            if str(value) == 'None':
                return None
            if type(value) == str:
                entity = 'datetime'
                unit = 'date'
                value = value.split('T')[0].lower()
            else:
                if question_instance.validation_type == 'notice_period':
                    entity = 'notice_period'
                else:
                    entity = 'work_experience'
                unit = 'days'
                value = value
            return {'entity': entity, 'unit': unit, 'value': value}

        if question_instance.validation_type == 'rating':
            value = self.convert_fetched_rating(qa_instance)
            if type(value) == int:
                entity = 'rating'
                unit = 'int'
                value = value
                return {'entity': entity, 'unit': unit, 'value': value}

        if question_instance.validation_type == 'city':
            entity = 'location'
            unit = 'city'
            if session.medium == 'webchat':
                value = self.get_location(strip_tags(qa_instance.answer))
            else:
                value = qa_instance.answer
            if type(value) == str:
                value = value.lower()
            return {'entity': entity, 'unit': unit, 'value': value}
