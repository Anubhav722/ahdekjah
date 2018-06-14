from django.conf import settings
import re

from .models import Tree, Transition, QuestionAnswerPair
from .converters import *


class Bot(object):
    """
    Bot is an abtraction which traverse the decision tree based on
    answer validation.
    """

    def __init__(self, start_state):
        self.start_state = start_state

    def start_test(self):
        tree = Tree.objects.all()[0]
        current_state = tree.root_state
        while True:
            print("> ", current_state.question.text)
            response = input("> ")
            current_state = self.get_next_state(current_state, response)
            if current_state is None:
                break
        print("> ", tree.completion_text)

    def store_question_answer_pair(self, question, user_input,
                                   session, payload):
        qapair = QuestionAnswerPair()
        qapair.question = question
        if type(user_input) == list:
            qapair.answer = ", ".join(user_input)
        else:
            if (session.medium == 'webchat' and
               not session.temporary_validation):
                qapair.answer = payload.get('text')
            else:
                qapair.answer = user_input
        qapair.save(session, payload)
        return qapair

    def fetch_previous_transitions(self, session):
        transitions = Transition.objects.filter(next_state=session.state,
                                                tree=session.tree)
        for transition in transitions:
            if transition.current_state.question.question_type == 'checkboxes':
                answer = Transition.objects.filter(
                                  current_state=transition.current_state,
                                  tree=session.tree).first().answer
                return answer

    def get_next_state(self, state, user_input, session, payload):
        radio_answer = None
        answer = None
        if session.tree and session.state:
            all_transitions = Transition.objects.filter(
                              current_state=state,
                              tree=session.tree).order_by('answer')
            found_transition = None
            for transition in all_transitions:
                answer = transition.answer
                if self.matches(answer, user_input, session):
                    if (not session.trial and
                       not settings.STORE_UNSTRUCTURED_ANSWER):
                        qapair = self.store_question_answer_pair(
                                 transition.current_state.question.text,
                                 user_input,
                                 session, payload)

                        session.question_answer_pair.add(qapair)
                    found_transition = transition
                    break
            if found_transition:
                return found_transition.next_state

        # for now keep repeating the same state till validate passes
        return state

    def matches(self, answer, user_input, session):
        if not user_input:
            return False

        if not answer or not answer.text:
            return True

        if session.state.question.question_type == 'checkboxes':
            if type(user_input) == list:
                for x in user_input:
                    if x.lower() in answer.text.lower():
                        return True
                return False
            return answer.text.lower() in user_input.lower()

        if answer.answer_type == "A":
            return user_input.lower() == answer.text.lower()

        if answer.answer_type == "S":
            answer_text = answer.text.split(',')
            answer_text = [answer.strip().lower() for answer in answer_text]
            # user_input = [user_input.strip() for x_input in user_input]
            if not type(user_input) == list:
                user_input = user_input.split()
            for x_input in user_input:
                if x_input.lower() in answer_text:
                    return True
            return False

        if answer.answer_type == "R":
            regex_search = re.findall(re.compile(str(answer.text)), user_input)
            if len(regex_search) > 0:
                return True
            return False
        # ignoring custom case for now
        return False
