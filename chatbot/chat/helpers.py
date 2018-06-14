import base64
from .constants import *
from .models import *


def encode(s):
    return base64.b64encode(s.encode('ascii'))


def decode(encoded):
    if len(encoded) % 4:
        encoded += '=' * (4 - len(encoded) % 4)
    decoded = base64.b64decode(encoded.encode('ascii')).decode('utf-8')
    if ',' in decoded:
        return decoded.split(',')
    return decoded.split('-')


def get_quick_replies(question):
    quick_replies = ''
    for answer in question['answers']:
        if not quick_replies:
            quick_replies += answer['text']
        else:
            quick_replies += ',' + answer['text']
    return quick_replies


def create_tree_questions(data):
    questions_queryset = [Question.objects.get_or_create(
                          text=question['question']['text'],
                          validation_type=question['question'].get(
                            'validation_type'),
                          is_follow_up=question['question'].get(
                            'is_follow_up'),
                          question_type=question['question'].get(
                            'question_type'))
                          if question['question'].get(
                            'question_type') == 'radio_buttons'
                          else Question.objects.get_or_create(
                            text=question['question'].get('text'),
                            validation_type=question['question'].get(
                                'validation_type'),
                            is_follow_up=question['question'].get(
                                'is_follow_up'),
                            question_type=question['question'].get(
                                'question_type'))
                          for question in data['transitions']]
    return questions_queryset


def create_question_state(questions_queryset):
    treestate_queryset = [TreeState.objects.get_or_create(question=question[0],
                          name=question[0].text)
                          for question in questions_queryset]
    return treestate_queryset


def create_tree_answers(data):
    answers_queryset = []
    for answers in data['transitions']:
        if answers['answers']:
            for answer in answers['answers']:
                if answers.get(
                        'question').get(
                        'question_type') == 'radio_buttons':
                    answer = Answer.objects.get_or_create(
                            text=answer.get('text'), answer_type='A')
                else:
                    answer = Answer.objects.get_or_create(
                            text=answer.get('text'), answer_type='S')
                answers_queryset.append(answer)
    return answers_queryset


def create_transitions(current_state, answer, next_state):
    try:
        if not answer:
            transition = Transition.objects.create(
                current_state=current_state, next_state=next_state)
            return transition
        transition = Transition.objects.create(
                        current_state=current_state, answer=answer,
                        next_state=next_state)
        return transition

    except IntegrityError as e:
        print(e)
        return False

def get_treestate(treestate_queryset, question):
    tree_state = [x[0] for x in treestate_queryset if x[0].question.text==question][0]
    return tree_state


def create_tree_transitions(data, treestate_queryset):
    transition_queryset = []
    for transitions in data['transitions']:
        if transitions.get('number') == 0:
            root_state = get_treestate(treestate_queryset,
                                       transitions.get('question')['text'])
        current_state = get_treestate(treestate_queryset,
                                      transitions.get('question')['text'])
        answer = ""
        if transitions.get('answers'):
            for answers in transitions.get('answers'):
                answer = Answer.objects.filter(text=answers.get('text'))[0]
                next_state = [x['question']['text'] for x in data['transitions'] if x['number'] == answers['next_question']]
                if next_state:
                    next_state = [x[0] for x in treestate_queryset if x[0].question.text==next_state[0]][0]
                else:
                    next_state = None
                transition = create_transitions(
                    current_state, answer, next_state)
                transition_queryset.append(transition)
        else:
            next_state = None
            next_question = transitions.get('next_question')
            if next_question:
                next_state = [x['question']['text'] for x in data['transitions'] if x['number'] == next_question]
                next_state = [x[0] for x in treestate_queryset if x[0].question.text==next_state[0]][0]
            transition = create_transitions(current_state, answer, next_state)
            if transition:
                transition_queryset.append(transition)
            else:
                return False, False
    return transition_queryset, root_state


def deactivate_session_with_same_recipient_id(session, recipient_id):
    session.recipient_id = recipient_id
    session.is_active = False
    session.save()


def get_active_session(recipient_id, tree_id, email):
    session = Session.objects.filter(recipient_id=recipient_id,
                                     is_active=True).first()
    if not session:
        session = Session.objects.filter(tree_id=tree_id,
                                         recipient_email=email,
                                         status='L').first()
        if session:
            session.is_active = True
            session.save()
    return session


def get_session(referral, recipient_id):
    encoded = referral['ref']
    email, tree_id = decode(encoded)
    if Session.objects.filter(recipient_id=recipient_id):
        session = Session.objects.filter(recipient_email=email,
                                         tree_id=tree_id,
                                         recipient_id='').first()
        if session:
            deactivate_session_with_same_recipient_id(session, recipient_id)

    return get_active_session(recipient_id, tree_id, email)


def obtain_session(recipient_id):
    session = Session.objects.filter(recipient_id=recipient_id,
                                     is_active=True).first()
    if not session:
        return
    if not session.state:
        return
    return session


def check_validation_extension(text):
    if text:
        if type(text) == dict:
            text = text['entry'][0]['messaging'][0]['message']['text']
        text = text.lower()
        for extension in EXTENSIONS:
            if extension in text:
                return True
    return False
