from django.conf import settings

from rest_framework import serializers

from auth.models import Client
from .models import (
    Answer,
    Question,
    Tree,
    TreeState,
    Transition,
    Session,
    QuestionAnswerPair,
    StructuredAnswer
)
from .helpers import encode, decode
from medium.facebook import Facebook
facebook = Facebook(settings.FB_PAGE_ACCESS_TOKEN)


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['answer_type', 'text']


class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ['text', 'validation_type']


class TreeStateSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = TreeState
        fields = ['question']


class TransitionSerializer(serializers.ModelSerializer):
    current_state = TreeStateSerializer()
    answers = AnswerSerializer()
    next_state = TreeStateSerializer()

    class Meta:
        model = Transition
        fields = ['id', 'current_state', 'answers', 'next_state']


class DemoChatSerializer(serializers.Serializer):
    tree_id = serializers.PrimaryKeyRelatedField(queryset=Tree.objects.all())
    recipient_email = serializers.EmailField()

    def get_session(self, client_key):
        if not self.is_valid():
            return None
        client = Client.objects.get(key=client_key)
        Session.objects.filter(
            recipient_email=self.validated_data['recipient_email']).delete()
        session = Session.objects.create(
            tree=self.validated_data['tree_id'],
            recipient_email=self.validated_data['recipient_email'],
            belongs_to=client,
            trial=True
        )
        session.state = session.tree.root_state
        session.save()
        return session


class RecipientDetailListSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    recipient_email = serializers.EmailField(required=True)
    recipient_phone = serializers.CharField(max_length=13, required=True)


class InitiateChatInputSerializer(serializers.Serializer):
    tree_id = serializers.PrimaryKeyRelatedField(queryset=Tree.objects.all())
    # callback_url = serializers.CharField(validators=[URLValidator])
    # recipient_email = serializers.EmailField()
    recipient_details = serializers.JSONField(required=True)
    # recipient_details = RecipientDetailListSerializer(child=serializers.JSONField(),
    #                     required=True)

    # Uncomment when twilio number is obtained.
    # recipient_phone = serializers.CharField(max_length=13)

    class Meta:
        list_serializer_class = RecipientDetailListSerializer

    def get_session(self, client_key):
        if not self.is_valid():
            return None
        client = Client.objects.get(key=client_key)
        session_details = []
        session_dict = {}
        for detail in self.validated_data['recipient_details']:
            session = Session.objects.create(
                            tree=self.validated_data['tree_id'],
                            belongs_to=client,
                            recipient_email=detail.get('recipient_email'),
                            recipient_phone=detail.get('recipient_phone'),
                            state=self.validated_data['tree_id'].root_state,
                            status='L')

            session = {'session': session,
                       'identifier': detail.get('identifier')}
            session_details.append(session)
        response_data = {'tree_id': self.validated_data['tree_id'],
                         'session_details': session_details}
        return response_data


class InitiateChatResponseSerializer(serializers.Serializer):
    class Meta:
        model = Session
        fields = ('id',)


def order_all_questions(transitions):
    questions = []
    for transition in transitions:
        if not transition.current_state.question.text in questions:
            questions.append(transition.current_state.question.text)
    return questions


class TreeSerializer(serializers.ModelSerializer):
    transitions = serializers.SerializerMethodField()
    tree_name = serializers.CharField(source='trigger')

    class Meta:
        model = Tree
        fields = ['id', 'tree_name',
                  'greeting_text', 'completion_text', 'transitions']

    def get_transitions(self, instance):
        y = []
        transition_all = []
        ordered_questions = order_all_questions(
                                instance.transition_set.all().order_by('id'))
        for indx, value in enumerate(
                                instance.transition_set.all().order_by('id')):
            if not value.current_state.question.text in y:
                y.append(value.current_state.question.text)
                number = ordered_questions.index(
                                value.current_state.question.text)
                current_question = value.current_state.question.text
                validation_type = value.current_state.question.validation_type
                is_follow_up = value.current_state.question.is_follow_up
                question_type = value.current_state.question.question_type
                question = {'text': current_question,
                            'validation_type': validation_type,
                            'is_follow_up': is_follow_up,
                            'question_type': question_type}
                answers = list()
                if value.answer:
                    transitions = Transition.objects.filter(
                                    current_state=value.current_state,
                                    tree_id=instance.id)
                    for transition in transitions:
                        answer = {}
                        answer['text'] = None
                        answer['next_question'] = None
                        next_question = None
                        if transition.answer:
                            answer['text'] = transition.answer.text
                            if transition.next_state:
                                next_question = transition.next_state.question.text
                            if next_question:
                                answer['next_question'] = ordered_questions.index(
                                                            next_question)
                        else:
                            if transition.next_state:
                                next_question = transition.next_state.question.text
                                answer['next_question'] = ordered_questions.index(next_question)
                        answers.append(answer)
                if not answers and not value.next_state == None:
                    next_question = Transition.objects.filter(
                                        current_state=value.next_state,
                                        tree_id=instance.id).first().current_state.question.text
                    next_question = ordered_questions.index(next_question)
                else:
                    next_question = None

                transition_set = {'number': number,
                                  'question': question,
                                  'answers': answers,
                                  'next_question': next_question}
                transition_all.append(transition_set)
        return transition_all


class StructuredAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = StructuredAnswer
        fields = ['entity', 'unit', 'value']


class QuestionAnswerPairSerializer(serializers.ModelSerializer):
    structured_answer = StructuredAnswerSerializer()

    class Meta:
        model = QuestionAnswerPair
        fields = ('answer', 'question', 'structured_answer')


class SessionQuestionAnswerPairSerializer(serializers.ModelSerializer):
    question_answer_pair = QuestionAnswerPairSerializer(many=True)

    class Meta:
        model = Session
        fields = ('question_answer_pair', )


class FilterSessionSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = Session
        fields = ('id', 'status', 'recipient_email', 'tree')


class SessionSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    tree = TreeSerializer()
    state = TreeStateSerializer()
    question_answer_pair = QuestionAnswerPairSerializer(many=True)

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = Session
        fields = ('id', 'status', 'recipient_id',
                  'recipient_email', 'tree', 'start_date',
                  'state', 'num_tries', 'canceled',
                  'last_modified', 'question_answer_pair')


class SessionChatInitiateSerializer(serializers.Serializer):
    tree_id = serializers.SerializerMethodField()
    session_details = serializers.SerializerMethodField()

    def get_tree_id(self, obj):
        return obj.get('tree_id').id

    def get_status(self, obj):
        return obj.get_status_display()

    def generate_bot_link(self, recipient_email, tree_id):
        key = encode("%s-%s" % (recipient_email, tree_id))
        bot_link = facebook.generate_messenger_share_link() + "?ref=" + key.decode('utf-8')
        return bot_link

    def get_session_details(self, obj):
        session_details = []
        session = {}
        identifier = {}
        for detail in obj.get('session_details'):
            bot_link = self.generate_bot_link(
                        detail.get('session').recipient_email,
                        obj.get('tree_id').id)
            session_details.append(
                {'id': detail.get('session').id,
                 'status': self.get_status(detail.get('session')),
                 # 'recipient_email': detail.get('session').recipient_email,
                 'identifier': detail.get('identifier'),
                 # 'recipient_phone': detail.get('recipient_phone'),
                 'bot_link': bot_link})
        return session_details

    class Meta:
        fields = ('tree_id', 'session_details')


class SessionMediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ('id', 'medium')
