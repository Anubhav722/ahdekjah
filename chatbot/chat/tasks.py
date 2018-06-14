# async and background tasks related to chat goes here
import requests
from celery.task import task
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.conf import settings
from django.utils.timezone import now
from django.utils.html import strip_tags

from medium.facebook import Facebook
from medium.webchat import WebChat
from medium.skype import Skype

from .converters import *
from .models import Tree, Session, QuestionAnswerPair
from .bot import Bot
from .helpers import get_session, obtain_session
from .serializers import SessionSerializer, SessionMediumSerializer
from .validators import *
from .constants import *
from .emails import email_admins
from datetime import datetime, timedelta

facebook = Facebook(settings.FB_PAGE_ACCESS_TOKEN)
webchat = WebChat()
skype = Skype()
validators = ValidateMessage()

countdown = settings.FB_USER_REMINDER_TIME*3600


def post_data_to_url(data, url):
    requests.post(url, json=data)


def post_medium_to_callback(session_id):
    session = Session.objects.get(id=session_id)
    if session:
        ser = SessionMediumSerializer(instance=session)
        callback_url = settings.CHATBOT_MEDIUM_URL
        post_data_to_url(ser.data, callback_url)


def post_session_to_callback(session_id):
    session = Session.objects.filter(id=session_id).first()
    if session:
        ser = SessionSerializer(instance=session)
        callback_url = settings.CHATBOT_CALLBACK_URL
        post_data_to_url(ser.data, callback_url)


def save_structured_data(session, data, qapair):
    if data:
        sapair = StructuredAnswer()
        sapair.entity = data.get('entity')
        sapair.unit = data.get('unit')
        sapair.value = data.get('value')
        sapair.save()
        QuestionAnswerPair.objects.filter(
            id=qapair.id).update(structured_answer=sapair)


def store_question_pair(session, message):
    if not session.state:
        return

    qapair = QuestionAnswerPair()
    qapair.question = message
    qapair.save(session, '')


def store_answer_pair(session, message, payload):
    qapair = session.question_answer_pair.last()

    if not qapair:
        return

    if type(message) == list:
        answer = ", ".join(user_input)
    else:
        answer = message
    QuestionAnswerPair.objects.filter(id=qapair.id).update(answer=answer)
    converter = StructuredAnswerConverter()
    structured_data = converter.get_structured_data(session, payload)
    save_structured_data(session, structured_data, qapair)


def fetch_quick_replies_for_question(session):
    transitions = Transition.objects.filter(current_state=session.state,
                                            tree=session.tree)
    quick_replies = []
    for transition in transitions:
        if transition.answer:
            quick_replies.append(transition.answer.text)
    return quick_replies


def update_session_state(session, msg, payload):
    bot = Bot(start_state=session.state)
    next_state = bot.get_next_state(session.state, msg, session, payload)
    session.state = next_state
    session.temporary_validation = ''
    session.save()


def send_skype_greetings_text(payload, session):
    message = session.tree.greeting_text
    skype.send_with_suggestion(payload, message,
                               ['Yeah Sure', 'Maybe Later', 'Not Interested'])
    if settings.STORE_UNSTRUCTURED_ANSWER:
        store_question_pair(session, message)
    session.num_tries += 1
    session.save()


def send_greetings_text(recipient_id, session):
    facebook.send_typing_on(recipient_id)
    user_info = facebook.get_facebook_user_info(recipient_id)
    message_1 = 'Hi {}'.format(user_info['first_name'])
    message_2 = session.tree.greeting_text
    # if settings.STORE_UNSTRUCTURED_ANSWER:
    #    store_question_pair(session, message_1)
    facebook.send(recipient_id, message_1)
    facebook.send_typing_on(recipient_id)
    facebook.send_with_quick_reply(recipient_id, message_2,
                                   ['Yeah Sure',
                                    'Maybe Later', 'Not Interested'])
    facebook.send_typing_off(recipient_id)
    session.num_tries += 1
    session.save()


def handle_validation_type_queue(session, msg, payload):
    if session.medium == 'skype':
        payload = msg
    # if (session.state.question.question_type == 'text_answer' and
    #        session.state.question.validation_type in ['None', 'none', None]):
    #    return validators.validate_free_text(msg, session), None

    if (not session.state.question.validation_type and
            not session.state.question.question_type == 'radio_buttons'):
        return True, None

    if (session.state.question.validation_type in
            WIT_EXTRACTION_VALIDATION_TYPES):
        response, quick_reply = validators.validate(
                    session.state.question.validation_type, payload, session)
        return response, quick_reply
    response, quick_reply = validators.validate(
                    session.state.question.validation_type, msg, session)
    return response, quick_reply


def handle_validation_replies(session):
    if session.state:
        question = session.state.question
        if question.question_type == 'checkboxes':
            return question.text, True

        if question.validation_type == 'rating':
            return question.text, RATING.keys()
        if question.question_type == 'radio_buttons':
            if question.validation_type == 'rating':
                quick_replies = RATING.keys()
                return question.text, quick_replies
            quick_replies = fetch_quick_replies_for_question(session)
            return question.text, quick_replies
        return question.text, None

    session.status = 'C'
    session.is_active = False
    session.save()
    print('conversation is over')
    post_session_to_callback(session.id)
    return session.tree.completion_text, None


def get_countdown(countdown, num_tries):
    local_countdown = countdown
    if num_tries == 4:
        local_countdown = countdown + 6*3600
    elif num_tries > 4:
        local_countdown = countdown + 9*3600
    return local_countdown


def cancel_session(session):
    session.canceled = True
    email_admins(session)
    session.save()


def send_reminder_text(session):
    message = VALIDATION_RESPONSES.get('reminder_text')[0]
    facebook.send(session.recipient_id, message)
    session.save()


@task(name='send_reminder_to_facebook_user')
def task_send_reminder_to_facebook_user(recipient_id):
    global countdown
    local_countdown = countdown
    session = Session.objects.filter(recipient_id=recipient_id,
                                     is_active=True, canceled=None).first()
    if session:
        if session.status == 'P' and session.num_tries < 6:
            local_countdown = get_countdown(countdown, session.num_tries)
            if float((datetime.now() - session.modified_date.replace(
                    tzinfo=None)).seconds)/3600 >= local_countdown/3600:
                if session.num_tries >= 3:
                    session.num_tries += 1
                    local_countdown = get_countdown(countdown,
                                                    session.num_tries)
                send_reminder_text(session)
            if session.num_tries == 6:
                cancel_session(session)
            task_send_reminder_to_facebook_user.apply_async(
                (session.recipient_id,),
                eta=session.modified_date+timedelta(seconds=local_countdown))


def send_medium_buttons(session, recipient_id, message, payload):
    if settings.STORE_UNSTRUCTURED_ANSWER:
        store_question_pair(session, message)
    if session.medium == 'skype':
        return skype.send_with_hero_card(payload, message)
    if session.medium == 'webchat':
        return webchat.send_with_button(recipient_id, message, session.status)
    return facebook.send_with_button(recipient_id, message)


def send_medium_quick_reply(session,
                            recipient_id, message, quick_reply, payload):
    if settings.STORE_UNSTRUCTURED_ANSWER:
        store_question_pair(session, message)
    if session.medium == 'skype':
        return skype.send_with_suggestion(payload, message, quick_reply)
    if session.medium == 'webchat':
        return webchat.send_with_quick_reply(recipient_id,
                                             message,
                                             quick_reply, session.status)
    return facebook.send_with_quick_reply(recipient_id, message, quick_reply)


def send_medium_text(session, recipient_id, message, payload):
    if settings.STORE_UNSTRUCTURED_ANSWER:
        store_question_pair(session, message)
    if session.medium == 'skype':
        return skype.send(payload, message)
    if session.medium == 'webchat':
        return webchat.send_text(recipient_id, message, session.status)
    return facebook.send(recipient_id, message)


def validate_get_started_for_skype(payload, msg):
    session = Session.objects.filter(
                recipient_id=payload.get('conversation')['id']).first()
    if msg == 'Yeah Sure':
        session.num_tries += 1
        session.save()
    elif msg == 'Maybe Later':
        message = VALIDATION_RESPONSES.get('get_started_text')[0]
        skype.send(payload, message)
    elif msg == 'Not Interested':
        message = VALIDATION_RESPONSES.get('get_started_text')[1]
        skype.send(payload, message)
        cancel_session(session)
    else:
        skype.send_with_suggestion(payload, session.tree.greeting_text,
                                   ['Yeah Sure',
                                    'Maybe Later', 'Not Interested'])


def validate_get_started(session, msg, payload):
    if msg == 'Yeah Sure':
        session.num_tries += 1
        session.save()
    elif msg == 'Maybe Later':
        message = VALIDATION_RESPONSES.get('get_started_text')[0]
        return send_medium_text(session,
                                session.recipient_id, message, payload)
    elif msg == 'Not Interested':
        message = VALIDATION_RESPONSES.get('get_started_text')[1]
        cancel_session(session)
        return send_medium_text(session,
                                session.recipient_id, message, payload)
    else:
        return send_medium_quick_reply(session, session.recipient_id,
                                       session.tree.greeting_text,
                                       ['Yeah Sure',
                                        'Maybe Later', 'Not Interested'],
                                       payload)


def send_reply(session, msg, payload):
    if type(payload) == str:
        payload = json.loads(payload)
    if payload and not strip_tags(payload.get('text')) == 'Resume':
        update_session_state(session, msg, payload)
    question, quick_reply = handle_validation_replies(session)
    if session.state:
        if (quick_reply == True or
                session.state.question.question_type == 'checkboxes' or
                session.state.question.validation_type == 'city'):
            return send_medium_buttons(session,
                                       session.recipient_id, question, payload)
        if quick_reply:
            return send_medium_quick_reply(session, session.recipient_id,
                                           question, quick_reply, payload)
    return send_medium_text(session, session.recipient_id, question, payload)


def send_validation_reply(session, response, quick_reply, payload):
    if quick_reply:
        return send_medium_quick_reply(session, session.recipient_id,
                                       response, quick_reply, payload)
    if (session.state.question.question_type == 'checkboxes' or
            session.state.question.validation_type == 'city'):
        return send_medium_buttons(session,
                                   session.recipient_id, response, payload)
    return send_medium_text(session, session.recipient_id, response, payload)


@periodic_task(run_every=(crontab(minute='*/45', hour=0)),
               name='generate_access_token_after_every_1_hour',
               ignore_result=True)
def task_generate_access_token():
    global skype
    url = skype.ACCESS_TOKEN_URL
    data = [
        ('grant_type', 'client_credentials'),
        ('client_id', settings.MICROSOFT_APP_ID),
        ('client_secret', settings.MICROSOFT_APP_SECRET),
        ('scope', skype.SKYPE_SCOPE)
    ]
    response = requests.post(url, data=data, verify=False)
    access_token = response.json().get('access_token')
    skype_token = SkypeToken.objects.first()
    if not skype_token:
        skype_token = SkypeToken.objects.create(access_token=access_token)
    else:
        skype_token.access_token = access_token
        skype_token.save()

@task(name='handle_user_reply')
def handle_facebook_callback(payload):
    """
    Any callback payload received from the webhook URL that is registered
    with the app, will be handled here.
    """
    global validators
    global facebook
    global skype
    global countdown
    print("Payload: ", payload)
    session = None
    referral, recipient_id = None, None

    # SKYPE LOAD HERE.
    if not type(payload) == str:
        if payload.get('type') == 'conversationUpdate':
            return

        elif (payload.get('type') == 'contactRelationUpdate' and
              payload.get('action') == 'add'):
            message = VALIDATION_RESPONSES.get('skype_verification')[0].format(
                            payload.get('from').get('name').split()[0])
            skype.send_contact_add_message(payload, message)
            return

        elif payload.get('type') == 'message':
            try:
                recipient_id, msg = skype.parse_message(payload)
                response = skype.verify_skype_code(recipient_id, msg)
                if not response:
                    message = VALIDATION_RESPONSES.get(
                                'skype_verification')[1].format(
                                    payload.get('from').get(
                                        'name').split()[0])
                    skype.send(payload, message)
                    return
            except Exception as e:
                print(e)

    else:
        # FACEBOOK LOAD HERE.
        recipient_id, referral = facebook.get_referral(payload)
        print("Hi there")
    # Used only once when the get_started button or the chatbot link is opened.
    if referral:
        session = get_session(referral, recipient_id)
        try:
            session.recipient_id = recipient_id
            session.status = 'P'
            session.save()
            task_send_reminder_to_facebook_user.apply_async((recipient_id,),
                                                            eta=session.modified_date+timedelta(
                                                            seconds=countdown))
            print("Hello inside if referral")
        except Exception as e:
            print (e)
            return
        print("Before sending greeting text")
        print(session.id)
        # Send greetings text when num_tries are 0.
        if session.num_tries == 0:
            print("Sending greetings text")
            send_greetings_text(recipient_id, session)
            post_session_to_callback(session.id)
            post_medium_to_callback(session.id)
            return
    print("Going to parse message")
    # parse facebook message from here.
    try:
        recipient_id, msg = facebook.parse_message(payload)
    except Exception as e:
        print ("WARNING: It's a skype conversation: {}".format(e))
    print("Parsed a message")
    session = obtain_session(recipient_id)
    if not session:
        return
    print("Obtained a session")
    if session.num_tries == 0:
        send_skype_greetings_text(payload, session)
        post_session_to_callback(session.id)
        post_medium_to_callback(session.id)
        return

    # Replacing it for now
    # Obtain session
    # session = obtain_session(recipient_id)
    # if not session:
    #     return

    # Saving user_inputs from here
    if settings.STORE_UNSTRUCTURED_ANSWER:
        store_answer_pair(session, msg, payload)
    if session.medium == 'facebook':
        facebook.send_typing_on(recipient_id)
    try:
        if session.num_tries == 1:
            validate_get_started(session, msg, payload)
            if not session.num_tries > 1:
                return

        # Replying portion of the bot.
        response, quick_reply = handle_validation_type_queue(session,
                                                             msg, payload)
        if not response == True:
            decision = validators.handle_quick_replies(msg, session)
            if decision and session.temporary_validation:
                send_reply(session, session.temporary_validation, payload)
                return
            if response:
                send_validation_reply(session, response, quick_reply, payload)
                return
        send_reply(session, msg, payload)
        return

    except Exception as e:
        print(e)



# @periodic_task(
#     run_every=(crontab(minute=0, hour='*/24')),
#     name = 'email_datasets_after_every_24_hours',
#     ignore_result = True
# )
# def email_datasets_after_every_24_hours():
#     """
#     Sends Question and answer data to the admins after every 24 hours.
#     """
#     connection = pg.connect("dbname={} user={} host={} password={}".format(
#                     get_env_variable('CHATBOT_DBNAME'), get_env_variable('CHATBOT_DBUSER'),
#                     get_env_variable('CHATBOT_DBHOST'), get_env_variable('CHATBOT_DBPASSWORD')))
#     df = psql.read_sql('select * from chat_questionanswerpair, chat_structuredanswer',
#                        connection)
#     df.to_excel('dataset')
#     email_datasets()

# @task(name='email_bot_link')
# def email_bot_link(session_data):
#     tree_id = session_data.get('tree_id')
#     session_details = session_data.get('session_details')
#     for session in session_details:
#         try:
#             key = encode("%s-%s" % (session.get('recipient_email'), tree_id))
#             bot_link = facebook.generate_messenger_share_link() + "?ref=" + key.decode('utf-8')
#             email_chatbot_link(
#                 to = [session.get('recipient_email')],
#                 context={'bot_link': bot_link}
#             )
#             body = 'Click this link to get started. {}'.format(bot_link)
#             message_chatbot_link(session.get('recipient_phone'), body)

#         except Exception as e:
#             session.status = 'failure'
#             session.save()
#             subject = 'Chatbot link failed to send'
#             body = 'Session id: {}, recipient_email: {}, recipient_phone: {}, Identifier: {}'.format(
#                     session.id, session.recipient_email,
#                     session.recipient_phone, session.identifier)
#             print (e.message, e.args)
#             mail_admins(subject, body)

