from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from auth.models import Client
from chat.views import TreeViewSet, InitiateChat
from chat.bot import Bot
from chat.tasks import handle_facebook_callback
from chat.models import *
from medium.facebook import Facebook

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory

import json


class TreeViewSetTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='launchyard', password='password123',
            email='launchyard@gmail.com')
        self.client = Client.objects.first()


    def test_tree_without_providing_client_key_and_secret(self):
        request = self.factory.get('/chat/tree/')
        response = TreeViewSet.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        request = self.factory.get('/chat/tree',
                                    HTTP_CHATBOT_CLIENT_KEY=self.client.key,
                                    HTTP_CHATBOT_CLIENT_SECRET=self.client.secret)

        response = TreeViewSet.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_tree_without_providing_all_fields(self):
        request = self.factory.post('/chat/tree',
                                    HTTP_CHATBOT_CLIENT_KEY=self.client.key,
                                    HTTP_CHATBOT_CLIENT_SECRET=self.client.secret)
        response = TreeViewSet.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tree_with_all_valid_inputs(self):
        json_data = {
            "questions": [{
                "text": "hillary", "quick_replies": "yes, no"
            }, {
                "text":"billiard", "quick_replies": "1, 2"
            }],
            "answers": [{
                "name": "maddy", "type": "A", "text":"catty", "description":"physics"
            }, {
                "name": "patty", "type":"A", "text":"sreadily", "description":"open source"
            }],
            "transitions": [{
                "current_state": "hillary", "answer": "maddy", "next_state": "billiard"
            }, {
                "current_state": "billiard", "answer": "patty", "next_state": ""
            }],
            "tree": [{
                "trigger": "assscssary", "root_state": "hillary", "completion_text": "Thanks man ..!!"
            }]
            }
        request = self.factory.post('/chat/tree/',
                                    format='json',
                                    data = json_data,
                                    HTTP_CHATBOT_CLIENT_KEY=self.client.key,
                                    HTTP_CHATBOT_CLIENT_SECRET=self.client.secret)

        response = TreeViewSet.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_tree_has_loops(self):
        question_1 = Question.objects.create(text='hi there')
        question_2 = Question.objects.create(text='wassup?')

        tree_state_1 = TreeState.objects.create(question=question_1)
        tree_state_2 = TreeState.objects.create(question=question_2)

        answer_1 = Answer.objects.create(type='A', text='yes')
        answer_2 = Answer.objects.create(type='A', text='non', name='play')

        transition_1 = Transition.objects.create(current_state=tree_state_1,
                                                answer=answer_1, next_state=tree_state_2)

        transition_2 = Transition.objects.create(current_state=tree_state_2,
                                                answer=answer_2, next_state=tree_state_1)

        tree = Tree.objects.create(root_state=tree_state_1, completion_text='thank you')
        status = tree.has_loops_below()

        self.assertEqual(status, True)

    def test_tree_has_no_loops(self):
        question_1 = Question.objects.create(text='hi there')
        question_2 = Question.objects.create(text='wassup?')

        tree_state_1 = TreeState.objects.create(question=question_1)
        tree_state_2 = TreeState.objects.create(question=question_2)

        answer_1 = Answer.objects.create(type='A', text='yes')
        answer_2 = Answer.objects.create(type='A', text='non', name='play')

        transition_1 = Transition.objects.create(current_state=tree_state_1,
                                                answer=answer_1, next_state=tree_state_2)
        transition_2 = Transition.objects.create(current_state=tree_state_2,
                                                answer=answer_2, next_state=None)

        tree = Tree.objects.create(root_state=tree_state_1, completion_text='thank you')
        status = tree.has_loops_below()

        self.assertEqual(status, False)


class InitiateChatTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='launchyard', password='password123',
            email='launchyard@gmail.com')
        self.client = Client.objects.first()

    def test_for_request_without_providing_any_values(self):
        request = self.factory.post('/chat/initiate')
        response = InitiateChat.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # required fields are callback_url, tree_id, and recipient_email

    def test_by_providing_all_the_fields_but_invalid(self):
        
        data = {
        "callback_url": "http://blah.com",
        "tree": "1",
        "recipient_email":"seeme@gmail.com"
        }

        request = self.factory.post('/chat/initiate',
                                    format='json',
                                    data=data)
        response = InitiateChat.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['tree'], [u'Invalid pk "1" - object does not exist.'])

    def test_by_providing_valid_tree_id(self):
        json_data = {
            "questions": [{
                "text": "hillary", "quick_replies": "yes, no"
            }, {
                "text":"billiard", "quick_replies": "1, 2"
            }],
            "answers": [{
                "name": "maddy", "type": "A", "text":"catty", "description":"physics"
            }, {
                "name": "patty", "type":"A", "text":"sreadily", "description":"open source"
            }],
            "transitions": [{
                "current_state": "hillary", "answer": "maddy", "next_state": "billiard"
            }, {
                "current_state": "billiard", "answer": "patty", "next_state": ""
            }],
            "tree": [{
                "trigger": "assscssary", "root_state": "hillary", "completion_text": "Thanks man ..!!"
            }]
            }
        request = self.factory.post('/chat/tree/',
                                    format='json',
                                    data = json_data,
                                    HTTP_CHATBOT_CLIENT_KEY=self.client.key,
                                    HTTP_CHATBOT_CLIENT_SECRET=self.client.secret)

        response = TreeViewSet.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tree = Tree.objects.first()
        data = {
        "callback_url": "http://blah.com",
        "tree": tree.id,
        "recipient_email":"seeme@gmail.com",
        "recipient_phone": "7655666888"
        }
        request = self.factory.post('/chat/initiate',
                                    format='json',
                                    data=data,
                                    HTTP_CHATBOT_CLIENT_KEY=self.client.key,
                                    HTTP_CHATBOT_CLIENT_SECRET=self.client.secret)
        response = InitiateChat.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        session = Session.objects.first()

        self.assertEqual(session.status, 'L')

class BotTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.start_state = 'hillary'
        self.bot = Bot(self.start_state)
        self.user = User.objects.create_user(username='launchyard', password='password123',
            email='launchyard@gmail.com')
        self.client = Client.objects.first()

    def test_start_test(self):
        json_data = {
            "questions": [{
                "text": "hillary", "quick_replies": "yes, no"
            }, {
                "text":"billiard", "quick_replies": "1, 2"
            }],
            "answers": [{
                "name": "maddy", "type": "A", "text":"catty", "description":"physics"
            }, {
                "name": "patty", "type":"A", "text":"sreadily", "description":"open source"
            }],
            "transitions": [{
                "current_state": "hillary", "answer": "maddy", "next_state": "billiard"
            }, {
                "current_state": "billiard", "answer": "patty", "next_state": ""
            }],
            "tree": [{
                "trigger": "assscssary", "root_state": "hillary", "completion_text": "Thanks man ..!!"
            }]
            }
        request = self.factory.post('/chat/tree/',
                                    format='json',
                                    data = json_data,
                                    HTTP_CHATBOT_CLIENT_KEY=self.client.key,
                                    HTTP_CHATBOT_CLIENT_SECRET=self.client.secret)

        response = TreeViewSet.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        current_state = Tree.objects.first().root_state
        user_input = 'catty'
        state = self.bot.get_next_state(current_state, user_input)
        self.assertEqual(state.name, 'billiard')

class HandleFacebookCallback(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='launchyard', email='launchyard@gmail.com',
                    password='password123')
        self.client = Client.objects.first()
        self.facebook = Facebook(settings.FB_PAGE_ACCESS_TOKEN)
        self.payload = u'{"object":"page","entry":[{"id":"128922990987384","time":1501143941051,"messaging":[{"recipient":{"id":"128922990987384"},"timestamp":1501143941051,"sender":{"id":"969833033053167"},"postback":{"payload":"GET_STARTED_PAYLOAD","referral":{"ref":"YW51YmhhdnNAZ21haWwuY29tLTE=","source":"SHORTLINK","type":"OPEN_THREAD"},"title":"Get Started"}}]}]}'
        self.factory = APIRequestFactory()

    def test_get_referral(self):
        recipient_id, referral = self.facebook.get_referral(self.payload)

        self.assertEqual(recipient_id, '969833033053167')
        self.assertEqual(referral['source'], 'SHORTLINK')

    def test_handle_facebook_callback_with_referral(self):
        json_data = {
            "questions": [{
                "text": "hillary", "quick_replies": "yes, no"
            }, {
                "text":"billiard", "quick_replies": "1, 2"
            }],
            "answers": [{
                "name": "maddy", "type": "A", "text":"catty", "description":"physics"
            }, {
                "name": "patty", "type":"A", "text":"sreadily", "description":"open source"
            }],
            "transitions": [{
                "current_state": "hillary", "answer": "maddy", "next_state": "billiard"
            }, {
                "current_state": "billiard", "answer": "patty", "next_state": ""
            }],
            "tree": [{
                "trigger": "assscssary", "root_state": "hillary", "completion_text": "Thanks man ..!!"
            }]
            }
        request = self.factory.post('/chat/tree/',
                                    format='json',
                                    data = json_data,
                                    HTTP_CHATBOT_CLIENT_KEY=self.client.key,
                                    HTTP_CHATBOT_CLIENT_SECRET=self.client.secret)

        response = TreeViewSet.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tree = Tree.objects.first()
        session = Session.objects.create(tree=tree, recipient_email='anubhavs@gmail.com', tree_id='1')
        handle_facebook_callback(self.payload)

        session = Session.objects.first()

        self.assertEqual(session.recipient_id, '969833033053167')

    def test_handle_facebook_without_referral(self):
        json_data = {
            "questions": [{
                "text": "hillary", "quick_replies": "yes, no"
            }, {
                "text":"billiard", "quick_replies": "1, 2"
            }],
            "answers": [{
                "name": "maddy", "type": "A", "text":"catty", "description":"physics"
            }, {
                "name": "patty", "type":"A", "text":"sreadily", "description":"open source"
            }],
            "transitions": [{
                "current_state": "hillary", "answer": "maddy", "next_state": "billiard"
            }, {
                "current_state": "billiard", "answer": "patty", "next_state": ""
            }],
            "tree": [{
                "trigger": "assscssary", "root_state": "hillary", "completion_text": "Thanks man ..!!"
            }]
            }
        request = self.factory.post('/chat/tree/',
                                    format='json',
                                    data = json_data,
                                    HTTP_CHATBOT_CLIENT_KEY=self.client.key,
                                    HTTP_CHATBOT_CLIENT_SECRET=self.client.secret)

        response = TreeViewSet.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        payload = u'{"object":"page","entry":[{"id":"128922990987384","time":1501144011354,"messaging":[{"sender":{"id":"969833033053167"},"recipient":{"id":"128922990987384"},"timestamp":1501144011318,"message":{"mid":"mid.$cAAAvslv3zhdjtG0aNldgyfQL-AkK","seq":153102,"text":"hi there"}}]}]}'

        tree = Tree.objects.first()
        session = Session.objects.create(tree=tree, recipient_email='anubhavs@gmail.com',
                                        tree_id='1', recipient_id='969833033053167',
                                        callback_url='http://blah.com')

        handle_facebook_callback(payload)

        question_answer_pair_count = QuestionAnswerPair.objects.all().count()
        self.assertEqual(question_answer_pair_count, 1)

class QuestionTest(TestCase):

    def test_question_models_string_representation(self):
        question = Question.objects.create(text='hi there', quick_replies='where',
                                          error_response='blah')

        self.assertNotEqual(str(question), question.text)

class AnswerTest(TestCase):

    def test_answer_models_string_representation(self):
        answer = Answer.objects.create(name='blah', type='A', 
                                      text='3.5 lakhs', description='blank description')

        self.assertEqual(str(answer), answer.name)

    def test_answer_models_type_is_contains(self):
        answer = Answer.objects.create(name='blah', type='contains', 
                                      text='3.5 lakhs', description='blank description')

        self.assertEqual(answer.type, 'S')

class TreeStateTest(TestCase):

    def setUp(self):
        self.question = Question.objects.create(text='hi there', quick_replies='where?',
                                                error_response='blah')
        self.answer = Answer.objects.create(name='blah', type='A', 
                                      text='3.5 lakhs', description='blank description')

        self.question_second = Question.objects.create(text='this is text', quick_replies='yes',
                                                      error_response='nope')


    def test_tree_state_creation(self):
        tree_state = TreeState.objects.create(name='question', question=self.question, num_retries=5)
        self.assertEqual(str(tree_state), tree_state.question.text)

    def test_tree_state_has_loops(self):
        tree_state_1 = TreeState.objects.create(name='question', question=self.question, num_retries=5)
        bool_value = tree_state_1.has_loops_below()
        self.assertEqual(bool_value, False)

        tree_state_2 = TreeState.objects.create(name='question_second', question=self.question_second,
                                                num_retries=6)

        transition = Transition.objects.create(current_state=tree_state_1, answer=self.answer,
                                                next_state=tree_state_2)

        bool_value = tree_state_1.has_loops_below()

        self.assertEqual(bool_value, False)

class TransitionTest(TestCase):

    def setUp(self):
        self.question_one = Question.objects.create(text='hi there', quick_replies='where?',
                                                error_response='blah')

        self.question_two = Question.objects.create(text='this is text', quick_replies='yes',
                                                      error_response='nope')

        self.answer = Answer.objects.create(name='blah', type='A', 
                                      text='3.5 lakhs', description='blank description')

        self.tree_state_1 = TreeState.objects.create(name='question_one', question=self.question_one,
                                                num_retries=5)

        self.tree_state_2 = TreeState.objects.create(name='question_two', question=self.question_two,
                                                num_retries=6)


    def test_transtions_string_representation(self):
        transition = Transition.objects.create(current_state=self.tree_state_1,
                                                answer=self.answer,
                                                next_state=self.tree_state_2)

        self.assertEqual(str(transition), 'hi there: blah ---> this is text')


class TreeTest(TestCase):
    
    def setUp(self):
        self.question_one = Question.objects.create(text='hi there', quick_replies='where?',
                                                    error_response='blah')

        self.tree_state_1 = TreeState.objects.create(name='question_one', question=self.question_one,
                                                    num_retries=5)

    def test_tree_string_representation(self):
        tree = Tree.objects.create(trigger='blah', root_state=self.tree_state_1,
                                    completion_text='Thanks man..!', summary='new state')

        self.assertEqual(str(tree), 'T8: blah -> hi there')

# class SessionQuerysetTest(TestCase):

#     def setUp(self):

class QuestionAnswerPairTest(TestCase):

    def setUp(self):
        self.question = Question.objects.create(text='hi there', quick_replies='where?',
                                                    error_response='blah')
        self.answer = Answer.objects.create(name='blah', type='A', 
                                      text='3.5 lakhs', description='blank description')

    def test_question_answer_pair_string_representation(self):
        question_answer_pair = QuestionAnswerPair.objects.create(question=self.question.text,
                                                                answer=self.answer.text)

        self.assertEqual(str(question_answer_pair), 'hi there')

class SessionTest(TestCase):

    def setUp(self):
        self.question_one = Question.objects.create(text='hi there', quick_replies='where?',
                                                        error_response='blah')

        self.tree_state_1 = TreeState.objects.create(name='question_one', question=self.question_one,
                                                    num_retries=5)

        self.tree = Tree.objects.create(trigger='blah', root_state=self.tree_state_1,
                                        completion_text='Thanks man..!', summary='new state')

    def test_session_class_methods(self):
        session = Session.objects.create(recipient_id='121722', recipient_email='launchyard.com',
                                        tree=self.tree, state=self.tree_state_1)

        session.cancel()
        self.assertEqual(session.canceled, True)

        bool_value = session.is_open()
        self.assertEqual(bool_value, False)


class EntryTest(TestCase):

    def setUp(self):
        self.question_one = Question.objects.create(text='hi there', quick_replies='where?',
                                                        error_response='blah')

        self.tree_state_1 = TreeState.objects.create(name='question_one', question=self.question_one,
                                                    num_retries=5)

        self.tree = Tree.objects.create(trigger='blah', root_state=self.tree_state_1,
                                        completion_text='Thanks man..!', summary='new state')

        self.session = Session.objects.create(recipient_id='121722', recipient_email='launchyard.com',
                                        tree=self.tree, state=self.tree_state_1)

        self.question_two = Question.objects.create(text='this is text', quick_replies='yes',
                                                      error_response='nope')

        self.tree_state_2 = TreeState.objects.create(name='question_two', question=self.question_two,
                                                num_retries=6)

        self.answer = Answer.objects.create(name='blah', type='A', 
                                      text='3.5 lakhs', description='blank description')

        self.transition = Transition.objects.create(current_state=self.tree_state_1,
                                                answer=self.answer,
                                                next_state=self.tree_state_2)

    def test_entry_string_representation(self):
        entry = Entry.objects.create(session=self.session, sequence_id=23, transition=self.transition,
                                    text='hit here')
        self.assertEqual(str(entry), '2-23: Q5: hi there - hit here')

    def test_entry_class_methods(self):
        entry = Entry.objects.create(session=self.session, sequence_id=23, transition=self.transition,
                                    text='hit here')

        display_text = entry.display_text()
        self.assertEqual(display_text, 'hit here')

        meta_data = entry.meta_data()
        self.assertEqual(len(meta_data), 22)