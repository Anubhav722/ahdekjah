import re

from django.core.management.base import BaseCommand
from chat.models import Tree, Transition

class Command(BaseCommand):
    help = "test chat command for given decision tree"

    def handle(self, *args, **kwargs):
        tree = Tree.objects.all()[0]
        current_state = tree.root_state
        while True:
            print("> ", current_state.question.text)
            response = input("> ")
            current_state = self.get_next_state(current_state, response)
            if current_state is None:
                break
        print("> ", tree.completion_text)

    def get_next_state(self, state, user_input):
        all_transitions = Transition.objects.filter(current_state=state)
        found_transition  = None
        for transition in all_transitions:
            if self.matches(transition.answer, user_input):
                found_transition = transition
                break
        if found_transition:
            return found_transition.next_state

        return None

    def matches(self, answer, user_input):
        if not user_input:
            return False
        if answer.type == "A":
            return user_input.lower() == answer.text.lower()
        if answer.type == "R":
            return re.match(answer.text, user_input, re.IGNORECASE)
        # ignoring custom case for now
        return False
