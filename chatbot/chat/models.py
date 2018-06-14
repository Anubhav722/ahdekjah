from model_utils import Choices

from django.db import models
from django.conf import settings
from base.models import BaseModel

# from model_utils.fields import StatusField
# from model_utils import Choices

# from auth.models import Client
import auth
from .constants import *


class Question(BaseModel):
    """
    Question represents a single instance of question that bot usually asks
    its client.
    e.g: What is your current Location?
    """

    QUESTION_TYPES = (
        ('text_answer', 'Text Answer'),
        ('radio_buttons', 'Radio Buttons'),
        ('checkboxes', 'Checkboxes'),
        )

    text = models.TextField(blank=False)
    question_type = models.CharField(
                        max_length=15,
                        choices=QUESTION_TYPES, default='text_answer')
    # quick_replies will be comma seperated string
    # that will be passed as quick replies
    # to the user by bot.
    # quick_replies = models.CharField(blank=True, max_length=300)
    is_follow_up = models.BooleanField(default=False)
    validation_type = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.validation_type == 'rating':
            self.quick_replies = ",".join(RATING.keys())
        super(Question, self).save(*args, **kwargs)

    def __str__(self):
        return "Q%s: %s" % (self.pk, self.text)


class Answer(BaseModel):
    """An answer to a question.

    There are three possible types of answers:

    The simplest is an exact answer. Messages will only match this answer if
    the text is exactly the same as the answer specified.

    The second is a regular expression.  In this case the system will run a
    regular expression over the message and match the answer if the regular
    expression matches.

    The final type is custom logic.  In this case the answer should be a
    special keyword that the application developer defines. The application
    developer can then register a function tied to this keyword with the tree
    app and the tree app will call that function to see if the answer should
    match. The function should return any value that maps to True if the answer
    is valid, otherwise any value that maps to False.
    """

    ANSWER_TYPES = (
        ('A', 'Exact Match'),
        ('R', 'Regular Expression'),
        ('C', 'Custom Logic'),
        ('S', 'String Match'),
    )

    answer_type = models.CharField(max_length=1, choices=ANSWER_TYPES)
    text = models.TextField(blank=False)

    def save(self, *args, **kwargs):
        if self.answer_type == 'contains':
            self.answer_type = 'S'
        super(Answer, self).save(*args, **kwargs)

    def __str__(self):
        return self.text


class TreeState(BaseModel):
    """
    A TreeState is a location in a tree.  It is associated with a question and
    a set of answers (transitions) that allow traversal to other states.
    """
    name = models.CharField(max_length=150)
    question = models.ForeignKey(Question)
    num_retries = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="The number of tries the user has to get out of this state"
    )

    def __str__(self):
        return self.question.text

    def add_all_unique_children(self, added):
        """
        Adds all unique children of the state to the passed in list.  This
        happens recursively.
        """
        transitions = self.transition_set.select_related(
                                'next_state__question')
        for transition in transitions:
            if transition.next_state:
                if transition.next_state not in added:
                    added.append(transition.next_state)
                    transition.next_state.add_all_unique_children(added)

    def has_loops_below(self):
        return TreeState.path_has_loops([self])

    @classmethod
    def path_has_loops(klass, path):
        # we're going to get all unique paths through the this
        # (or until we hit a loop)
        # a path is defined as an ordered set of states
        # if at any point in a path we reach a state we've
        # already seen then we have a loop
        # this is basically a depth first search
        last_node = path[len(path) - 1]
        transitions = last_node.transition_set.all()
        for transition in transitions:
            if transition.next_state:
                # Base case.  We have already seen this state in the path
                if path.__contains__(transition.next_state):
                    return True
                next_path = path[:]
                next_path.append(transition.next_state)
                # recursive case - there is a loop somewhere below this path
                if TreeState.path_has_loops(next_path):
                    return True
        # we trickle down to here -
        # went all the way through without finding any loops
        return False


class Tree(BaseModel):
    """A decision tree.

    Trees have a trigger, which is is the incoming message that will initiate a
    tree.  They also have a root state which is the first state the tree will
    be in.  The question linked to the root state will be the one that is sent
    when the tree is initiated.  The remaining logic of the tree is
    encapsulated by the Transition objects, which define how answers to
    questions move from one state to the next.

    A tree also has optional completion text, which is the message that will be
    sent to the user when they reach a node in the tree with no possible
    transitions.
    """

    trigger = models.CharField(
        max_length=100, unique=False, verbose_name="Keyword",
        help_text="The incoming message which triggers this Tree.")
    root_state = models.ForeignKey(
        "TreeState", related_name="tree_set",
        help_text="The first Question sent when this Tree is triggered, "
                  "which may lead to many more.")
    completion_text = models.CharField(
        max_length=160, blank=True, null=True,
        help_text="The message that will be sent when the tree is completed")
    greeting_text = models.CharField(
        max_length=200, blank=True, null=True,
        help_text="The message that will be sent when user clicks the bot link")
    summary = models.CharField(max_length=160, blank=True)
    default = models.BooleanField(
                default=False,
                help_text="Default trees have type as True")
    # transitions = models.ManyToManyField(Transition)
    belongs_to = models.ForeignKey('auths.Client', related_name='trees')

    def __str__(self):
        return u"T%s: %s -> %s" % (self.pk, self.trigger, self.root_state)

    def has_loops_below(self):
        tree_state = self.root_state
        return Tree.path_has_loops([tree_state])

    @classmethod
    def path_has_loops(klass, path):
        # we're going to get all unique paths through the this
        # (or until we hit a loop)
        # a path is defined as an ordered set of states
        # if at any point in a path we reach a state we've
        # already seen then we have a loop
        # this is basically a depth first search
        last_node = path[len(path)-1]

        transitions = last_node.transition_set.all()
        for transition in transitions:
            if transition.next_state:
                # Base case.  We have already seen this state in the path
                if path.__contains__(transition.next_state):
                    return True
                next_path = path[:]
                next_path.append(transition.next_state)
                # recursive case - there is a loop somewhere below this path
                # if TreeState.path_has_loops(next_path):
                if Tree.path_has_loops(next_path):
                    return True
        # we trickle down to here -
        # went all the way through without finding any loops
        return False

    def save(self, *args, **kwargs):
        # import ipdb; ipdb.set_trace()
        # if self.has_loops_below():
        #     raise ValueError("The tree has loops.")
        super(Tree, self).save(*args, **kwargs)


class Transition(models.Model):
    """
    A Transition is a way to navigate from one TreeState to another, via an
    appropriate Answer.
    """
    current_state = models.ForeignKey(TreeState)
    answer = models.ForeignKey(
                Answer,
                related_name='transitions', blank=True, null=True)
    next_state = models.ForeignKey(
                    TreeState,
                    blank=True, null=True,
                    related_name='next_state_transitions')
    tree = models.ForeignKey(Tree, blank=True, null=True)

    class Meta(object):
        unique_together = ('current_state', 'answer', 'tree'),

    def __str__(self):
        return "%s: %s ---> %s" % (self.current_state,
                                   self.answer, self.next_state)


class SessionQuerySet(models.query.QuerySet):
    _closed_conditions = models.Q(state=None) | models.Q(canceled=True)

    def open(self):
        return self.exclude(self._closed_conditions)

    def closed(self):
        return self.filter(self._closed_conditions)


class StructuredAnswer(BaseModel):
    """
    Model to extracted info for a particular question.
    """

    ENTITY_TYPES = Choices(
            ('duration', [
                'notice_period', 'work_experience', 'notice_period_none']),
            ('ctc_inr', ['current_ctc_inr', 'expect_ctc_inr']),
            ('location', 'Location'),
            ('datetime', 'DateTime'),
            ('boolean', 'Boolean'),
            ('rating', 'Rating'),
        )

    entity = models.CharField(max_length=15, choices=ENTITY_TYPES, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    value = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.entity


class QuestionAnswerPair(BaseModel):
    question = models.CharField(unique=False, blank=False, max_length=255)
    answer = models.TextField(blank=False, max_length=255)
    structured_answer = models.ForeignKey(StructuredAnswer,
                                          null=True, blank=True)

    def save(self, session, payload, *args, **kwargs):
        from .converters import StructuredAnswerConverter
        if session:
            super(QuestionAnswerPair, self).save(*args, **kwargs)
            session.question_answer_pair.add(self)
            if not settings.STORE_UNSTRUCTURED_ANSWER:
                converter = StructuredAnswerConverter()
                structured_data = converter.get_structured_data(
                                        session, payload)
                if structured_data:
                    sapair = StructuredAnswer()
                    sapair.entity = structured_data.get('entity')
                    sapair.unit = structured_data.get('unit')
                    sapair.value = structured_data.get('value')
                    sapair.save()
                    self.structured_answer = sapair
                super(QuestionAnswerPair, self).save(*args, **kwargs)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ('id',)


class Session(BaseModel):
    """
    A Session represents a single person's current status traversing through a
    Tree. It is a way to persist information about what state they are in, how
    many retries they have had, etc. so that we aren't storing all of that
    in-memory.
    """
    # connection = models.ForeignKey('medium.Connection')
    STATUS = (
        ('L', 'link_sent'),
        ('LNS', 'link_not_sent'),
        ('C', 'completed'),
        ('P', 'in_process'),
        ('F', 'failure'),
    )

    MEDIUM = (
        ('facebook', 'Facebook'),
        ('webchat', 'WebChat'),
        ('skype', 'Skype')
    )

    recipient_id = models.CharField(max_length=1000, blank=False)
    recipient_email = models.CharField(max_length=100, blank=False, default='')
    recipient_phone = models.CharField(max_length=13, blank=False, default='')
    tree = models.ForeignKey(Tree,
                             related_name='sessions',
                             on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    state = models.ForeignKey(
        TreeState, blank=True, null=True,
        help_text="None if the session is complete.")
    num_tries = models.PositiveIntegerField(default=0,
        help_text="The number of times the user has tried to answer the "
                  "current question.")
    # this flag stores the difference between completed
    # on its own, or manually canceled.
    canceled = models.NullBooleanField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, null=True)
    question_answer_pair = models.ManyToManyField(QuestionAnswerPair)
    belongs_to = models.ForeignKey('auths.Client', related_name='sessions')
    status = models.CharField(max_length=3, choices=STATUS, default='')
    objects = SessionQuerySet.as_manager()
    temporary_validation = models.CharField(max_length=50, blank=True)
    trial = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    medium = models.CharField(max_length=10,
                              choices=MEDIUM, default='facebook')

    def __str__(self):
        return self.recipient_email

    def cancel(self):
        return self.close(canceled=True)

    def close(self, canceled=False):
        """Forcibly close this session.

        No operation if session is already closed.
        """
        # TODO: call app listeners?
        if not self.is_closed():
            self.state = None
            self.canceled = canceled
            self.save()

    def is_closed(self):
        return not bool(self.state_id) or self.canceled

    def is_open(self):
        return bool(self.state_id) and not self.canceled


class SkypeToken(BaseModel):
    access_token = models.CharField(max_length=1000)

    def __str__(self):
        return self.access_token
