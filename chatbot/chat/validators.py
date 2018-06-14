from django.conf import settings
from django.utils.html import strip_tags

from .constants import *
from .models import *
from medium.facebook import Facebook
from nlp.wit_extractor import WitExtractor
from .helpers import *
from nlp.text_analysis import AnalyzeText

import json

from geopy.geocoders import Nominatim


class ValidateMessage(object):
    """
    Validates free text and accepts messages only in a certain desired format.
    """

    def __init__(self):
        self.wit = WitExtractor()
        self.analyzer = AnalyzeText()
        self.CTC_FORMAT_INR = CTC_FORMAT_INR
        self.WORK_EXPERIENCE_FORMAT = WORK_EXPERIENCE_FORMAT
        self.WIT_EXTRACTION_VALIDATION_TYPES = WIT_EXTRACTION_VALIDATION_TYPES
        self.facebook = Facebook(settings.FB_PAGE_ACCESS_TOKEN)
        self.validation_response = VALIDATION_RESPONSES

    def fetch_quick_replies_for_question(self, session):
        transitions = Transition.objects.filter(current_state=session.state,
                                                tree=session.tree)
        quick_replies = []
        for transition in transitions:
            if transition.answer:
                quick_replies.append(transition.answer.text)
        return quick_replies

    def handle_quick_replies(self, reply, session):
        if reply.lower() == "yes":
            return True
        elif reply.lower() == "no":
            session.temporary_validation = ''
            session.save()
            return
        return

    def validate_notice_period(self, payload, user_info, session):
        if session.medium in ['webchat', 'skype']:
            text = payload
            if session.medium == 'webchat':
                text = strip_tags(payload.get('text'))
            value, unit = self.wit.extract_wit_values(text,
                                                      session.state.question.validation_type)
        else:
            value, unit = self.wit.get_duration(payload)
        if type(value) == int or type(value) == float:
            if unit in ['week', 'month', 'year', 'day']:
                return True, None
            self.save_temp_validation(session, (str(value) + " week"))
            return (self.validation_response.get('notice_period')[0].format(
                    user_info['first_name'], value), ['yes', 'no'])
        if unit in ['datetime', 'interval']:
            value = str(value.split('T')[0])
            self.save_temp_validation(session, value)
            return (self.validation_response.get('notice_period')[2].format(
                    value), ['yes', 'no'])
        return self.validation_response.get('notice_period')[1].format(
                user_info['first_name']), None

    def save_temp_validation(self, session, temporary_validation):
        session.temporary_validation = temporary_validation
        session.save()

    def validate_city(self, user_input, user_info, session):
        if session.medium == 'webchat':
            geolocator = Nominatim()
            geo_location = geolocator.geocode(user_input,
                                              addressdetails=True, timeout=20)
            if geo_location:
                geo_loc = geo_location.raw.get('address').get('city')
                return True, None
            return (self.validation_response.get('city')[0].format(
                        user_info['first_name']), None)
        return (self.validation_response.get('city')[0].format(
                        user_info['first_name']), None)

    def validate_CTC_INR(self, user_input, user_info, session):
        if session.medium in ['webchat', 'skype']:
            text = user_input
            if session.medium == 'webchat':
                text = strip_tags(user_input.get('text'))
            number = self.wit.extract_wit_values(text,
                        session.state.question.validation_type)
        else:
            number = self.wit.get_numbers(user_input)
            text = user_input['entry'][0]['messaging'][0]['message']['text']
        if type(number) == int or type(number) == float:
            for ctc in self.CTC_FORMAT_INR:
                if ctc in text:
                    return True, None
            self.save_temp_validation(session, str(number) + " lakh")
            return (self.validation_response.get('ctc_inr')[0].format(
                    user_info['first_name'], number), ['yes', 'no'])

        ctc_extension = check_validation_extension(text)
        if ctc_extension:
            return True, None
        return self.validation_response.get('ctc_inr')[1].format(
                user_info['first_name']), None

    def validate_work_experience(self, user_input, user_info, session):
        if session.medium in ['webchat', 'skype']:
            text = user_input
            if session.medium == 'webchat':
                text = user_input.get('text')
            value, years = self.wit.extract_wit_values(text,
                            session.state.question.validation_type)
        else:
            text = user_input
            value, years = self.wit.get_duration(user_input)
        if years in self.WORK_EXPERIENCE_FORMAT:
            if value > 30:
                return self.validation_response.get(
                        'work_experience')[2].format(
                        user_info['first_name'], value), None
            return True, None
        if type(value) == int or type(value) == float:
            self.save_temp_validation(session, str(value)+" year")
            return self.validation_response.get('work_experience')[0].format(
                    user_info['first_name'], value), ['yes', 'no']

        ctc_extension = check_validation_extension(text)
        if ctc_extension:
            return True, None
        return self.validation_response.get('work_experience')[1].format(
                user_info['first_name']), None

    def validate_rating(self, user_input, user_info, session):
        user_input = user_input.strip().split()
        for word in user_input:
            if word in RATING.keys():
                return True, None
        return self.validation_response.get('rating')[0].format(
            user_info['first_name']), RATING.keys()

    def validate_first_reply_as_free_text(self, session):
        if session.num_tries == 2 and session.state == session.tree.root_state:
            session.num_tries += 1
            session.save()
            return True
        return False

    def validate(self, validation_type, user_input, session):
        # user_info = self.facebook.get_facebook_user_info(session.recipient_id)
        user_info = {"first_name": "there"}
        if not validation_type or validation_type == 'none' or validation_type == 'None':
            if self.validate_first_reply_as_free_text(session):
                if session.state.question.question_type == 'radio_buttons':
                    quick_replies = self.fetch_quick_replies_for_question(
                                        session)
                    return session.state.question.text, quick_replies
                return session.state.question.text, None
            if session.state.question.question_type == 'radio_buttons':
                quick_replies = self.fetch_quick_replies_for_question(session)
                return True, quick_replies
            return True, None

        if not session.medium in ['webchat', 'skype']:
            try:
                user_input = json.loads(user_input)
            except Exception as e:
                print(e)

        if validation_type == 'city':
            if self.validate_first_reply_as_free_text(session):
                return session.state.question.text, None
            return self.validate_city(user_input, user_info, session)

        if validation_type == 'ctc_inr':
            if self.validate_first_reply_as_free_text(session):
                return session.state.question.text, None
            return self.validate_CTC_INR(user_input, user_info, session)

        if validation_type == 'notice_period':
            if self.validate_first_reply_as_free_text(session):
                return session.state.question.text, None
            return self.validate_notice_period(user_input, user_info, session)

        if validation_type == 'work_experience':
            if self.validate_first_reply_as_free_text(session):
                return session.state.question.text, None
            return self.validate_work_experience(user_input,
                                                 user_info, session)

        if validation_type == 'rating':
            if self.validate_first_reply_as_free_text(session):
                return session.state.question.text, RATING.keys()
            return self.validate_rating(user_input, user_info, session)

    def validate_free_text(self, user_input, session):
        self.analyzer.sentence = user_input
        response, word = self.analyzer.spellcheck()
        if response == True:
            return True
        if word:
            return self.validation_response.get(
                    'analyzers')[1].format(word) + session.state.question.text
        return self.validation_response.get(
                    'analyzers')[0] + session.state.question.text
