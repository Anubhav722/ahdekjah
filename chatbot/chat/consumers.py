from django.utils.html import strip_tags

from .tasks import *
from .helpers import *
from .bot import *
from .validators import *
from .converters import *
from medium.webchat import *

webchat = WebChat()
validators = ValidateMessage()


def send_webchat_greetings(recipient_id, session):
    # if settings.STORE_UNSTRUCTURED_ANSWER:
    #    store_question_pair(session, session.tree.greeting_text)
    reply = webchat.send_with_quick_reply(recipient_id,
                                          session.tree.greeting_text,
                                          ['Yeah Sure',
                                           'Maybe Later',
                                           'Not Interested'], session.status)
    session.num_tries += 1
    session.save()
    return reply


def get_validation_type(session):
    if not session.state:
        return None
    return session.state.question.validation_type


def handle_webchat_callback(payload):
    global webchat
    print("Payload: ", payload)
    session = None
    if payload.get('type') == 'postback':
        session = webchat.get_session(payload)
    else:
        session = obtain_session(payload.get('recipient_id'))

    if not session:
        return None, None
    if session.num_tries == 0:
        post_session_to_callback(session.id)
        post_medium_to_callback(session.id)
        return (send_webchat_greetings(session.recipient_id, session), None)

    if settings.STORE_UNSTRUCTURED_ANSWER:
        store_answer_pair(session, payload.get('text'), payload)

    if session.num_tries == 1:
        reply = validate_get_started(session, strip_tags(payload.get('text')), payload)
        if not session.num_tries > 1:
            return reply, None

    if (strip_tags(payload.get('text')) == 'Resume' and
            payload.get('type') == 'postback'):
        return (send_reply(session, session.state.question.text, payload),
                get_validation_type(session))

    user_input = strip_tags(payload.get('text'))
    response, quick_reply = handle_validation_type_queue(session,
                                                         user_input, payload)

    if not response == True:
        decision = validators.handle_quick_replies(user_input, session)
        if decision and session.temporary_validation:
            return (send_reply(session, session.temporary_validation, payload),
                    get_validation_type(session))
        if response:
            return (send_validation_reply(session, response, quick_reply, payload),
                    get_validation_type(session))
    return (send_reply(session, user_input, payload),
            get_validation_type(session))
