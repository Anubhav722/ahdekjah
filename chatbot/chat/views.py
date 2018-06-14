from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http.response import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models.functions import Cast
from django.db.models import FloatField
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db import IntegrityError

from rest_framework import viewsets
from rest_framework import views
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView


from auth.models import Client
from .models import (
    Tree, Session, Transition, QuestionAnswerPair,
)
from .serializers import (
    SessionSerializer, TreeSerializer, SessionChatInitiateSerializer,
    SessionQuestionAnswerPairSerializer, DemoChatSerializer,
    FilterSessionSerializer, RecipientDetailListSerializer
    )
from .permissions import IsAuthenticated, IsOwner, IsTreeOwner
from medium.facebook import Facebook
from medium.skype import Skype
from . import tasks
from .helpers import *
from .serializers import (
    InitiateChatInputSerializer
)
from .emails import email_admins
from .constants import *
import json


class TreeViewSet(viewsets.ModelViewSet):
    queryset = Tree.objects.filter(default=False)
    serializer_class = TreeSerializer
    permission_classes = [IsAuthenticated, IsTreeOwner]

    def list(self, request):
        queryset = Tree.objects.filter(default=True)
        serializer = TreeSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        if not request.body:
            return Response(
                {'status': 'Failed',
                 'detail': 'Please provide Tree Transitions accordingly.'},
                status=status.HTTP_400_BAD_REQUEST)
        data = json.loads(request.body.decode('utf-8'))

        if not data.get('completion_text'):
            return Response(
                {'status': 'Failed',
                 'detail': 'Please provide the completion text of the tree'},
                status=status.HTTP_400_BAD_REQUEST)

        completion_text = data.get('completion_text')

        if not data.get('greeting_text'):
            return Response(
                {'status': 'Failed',
                 'detail': 'Please provide greeting text for tree creation'},
                status=status.HTTP_400_BAD_REQUEST)

        trigger = data.get('tree_name', '')
        greeting_text = data.get('greeting_text')
        if not data.get('transitions'):
            return Response(
                {'status': 'Failed',
                 'detail': 'Please provide transitions for tree.'},
                status=status.HTTP_400_BAD_REQUEST)

        questions_queryset = create_tree_questions(data)

        treestate_queryset = create_question_state(questions_queryset)
        answers_queryset = create_tree_answers(data)

        transition_queryset, root_state = create_tree_transitions(
                                                data,
                                                treestate_queryset)

        if not transition_queryset:
            return Response({
                'status': 'Failed',
                'detail': 'Tree with transition having same current_state and answer violates the rule'},
                status=status.HTTP_400_BAD_REQUEST)

        client_key = request.META.get('HTTP_CHATBOT_CLIENT_KEY')
        client_secret = request.META.get('HTTP_CHATBOT_CLIENT_SECRET')
        client = Client.objects.get(key=client_key, secret=client_secret)

        tree_queryset = Tree.objects.create(
                                root_state=root_state,
                                completion_text=completion_text,
                                trigger=trigger,
                                belongs_to=client, greeting_text=greeting_text)

        for transition in transition_queryset:
            try:
                tree_queryset.transition_set.add(transition)
            except IntegrityError as e:
                print("USER ERROR: %s" % e)

        return Response({
            'status': 'Created',
            'detail': 'Tree has been successfully created.',
            'tree_id': tree_queryset.pk
        }, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        tree = get_object_or_404(Tree, pk=pk)
        client_key = request.META.get('HTTP_CHATBOT_CLIENT_KEY')
        client_secret = request.META.get('HTTP_CHATBOT_CLIENT_SECRET')
        client = Client.objects.get(key=client_key, secret=client_secret)

        if tree.default == True:
            return Response(
                {'status': 'Failed',
                 'detail': 'Default Trees cannot be edited'},
                status=status.HTTP_403_FORBIDDEN)

        if not tree.belongs_to == client:
            return Response(
                {'status': 'Failed',
                 'detail': 'Authentication credentials were not provided.'},
                status=status.HTTP_403_FORBIDDEN)
        if request.body is None:
            return Response(
                    {'status': 'Failed',
                     'detail': 'Question, Answer, Transition, Tree fields are required. Make sure you are entering valid json'
                     },
                    status=status.HTTP_400_BAD_REQUEST
                )
        data = json.loads(request.body.decode('utf-8'))

        trigger = data.get('tree_name', '')
        if not data.get('completion_text'):
            return Response(
                {'status': 'Failed',
                 'detail': 'Please provide the completion text of the tree'},
                status=status.HTTP_400_BAD_REQUEST)
        completion_text = data.get('completion_text')

        if not data.get('greeting_text'):
            return Response(
                {'status': 'Failed',
                 'detail': 'Please provide the greeting text for the tree'},
                status=status.HTTP_400_BAD_REQUEST)

        greeting_text = data.get('greeting_text')

        if not data.get('transitions'):
            return Response(
                {'status': 'Failed',
                 'detail': 'Please provide transitions for tree'},
                status=status.HTTP_400_BAD_REQUEST)

        tree.transition_set.all().delete()

        questions_queryset = create_tree_questions(data)
        treestate_queryset = create_question_state(questions_queryset)
        answers_queryset = create_tree_answers(data)
        transition_queryset, root_state = create_tree_transitions(
                                                data,
                                                treestate_queryset)

        # tree.transition_set.all().delete()

        tree.root_state = root_state
        for transition in transition_queryset:
            try:
                tree.transition_set.add(transition)
            except IntegrityError as e:
                print("USER ERROR: %s" % e)
        tree.trigger = trigger
        tree.completion_text = completion_text
        tree.greeting_text = greeting_text
        tree.save()

        return Response({
            'status': 'Updated',
            'detail': 'Tree has been successfully updated.',
            'tree_id': tree.id
        }, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        tree = get_object_or_404(Tree, pk=pk)

        if tree.default == True:
            return Response(
                {'status': 'Failed',
                 'detail': 'Default trees cannot be deleted'},
                status=status.HTTP_403_FORBIDDEN)

        client_key = request.META.get('HTTP_CHATBOT_CLIENT_KEY')
        client_secret = request.META.get('HTTP_CHATBOT_CLIENT_SECRET')
        client = Client.objects.get(key=client_key, secret=client_secret)
        if not tree.belongs_to == client:
            return Response(
                {'status': 'Failed',
                 'detail': 'Authentication credentials provided did not match'},
                status=status.HTTP_403_FORBIDDEN)

        sessions = Session.objects.filter(tree=tree)

        if request.query_params.get('force') != 'true':
            if (sessions.filter(status='P').exists() or
                    sessions.filter(status='L').exists()):
                return Response(
                    {'status': 'Failed',
                    'detail': 'Currently some sessions are under process. Please delete those sessions then continue.'},
                    status=status.HTTP_403_FORBIDDEN)
        tree.delete()
        return Response({
            'status': 'Deleted',
            'detail': 'Tree with id: {} has been deleted'.format(pk)
        }, status=status.HTTP_204_NO_CONTENT)


class SessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class Webhook(generic.View):
    """
    Makes connection with facebook from callback url.
    Verifies token received from callback url and returns HttpResponse,
    if it matches.
    Takes post request of incoming messages from user and
    calls the respective functions
    """
    def get(self, request, *args, **kwargs):
        return HttpResponse(self.request.GET['hub.challenge'])

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        incoming_message = self.request.body.decode('utf-8')
        tasks.handle_facebook_callback.delay(incoming_message)
        return HttpResponse()


class SkypeIntegration(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        tasks.handle_facebook_callback.delay(request.data)
        return HttpResponse()


class InitiateChat(generics.GenericAPIView):
    """
    Takes tree_id, receipient_email
    1. Triggers the messenger URL to receipient email
    2. Create session with recipient email and callbackurl
    3. Return the session_id
    """
    serializer_class = InitiateChatInputSerializer
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        if not request.body.decode('utf-8'):
            return Response(
                 {'status': 'Failed',
                  'detail': 'Please provide details of candidates'},
                status=status.HTTP_400_BAD_REQUEST)
        data = json.loads(request.body.decode('utf-8'))
        ser = self.get_serializer(data=data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        client_key = request.META.get('HTTP_CHATBOT_CLIENT_KEY')
        for detail in data.get('recipient_details'):
            recipient_detail = RecipientDetailListSerializer(data=detail)
            if not recipient_detail.is_valid():
                return Response(recipient_detail.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        session = ser.get_session(client_key)
        outser = SessionChatInitiateSerializer(instance=session)

        return Response(data=outser.data, status=status.HTTP_201_CREATED)


class ClientDemoView(generics.GenericAPIView):
    serializer_class = DemoChatSerializer
    permission_classes = [IsAuthenticated, IsTreeOwner]

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if ser.is_valid():
            client_key = request.META.get('HTTP_CHATBOT_CLIENT_KEY')
            session = ser.get_session(client_key)
            session.status = 'L'
            session.save()

            facebook = Facebook(settings.FB_PAGE_ACCESS_TOKEN)
            key = encode("%s-%s" % (session.recipient_email, session.tree.id))
            bot_link = facebook.generate_messenger_share_link() + "?ref=" + key.decode('utf-8')
            return Response(
                {'message': 'Successfully generated messenger chatbot link',
                 'bot_link': bot_link},
                status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class DefaultTreeDetailView(generics.RetrieveAPIView):
    queryset = Tree.objects.filter(default=True)
    serializer_class = TreeSerializer


class DefaultValidationTypeListView(generics.ListAPIView):

    def list(self, request):
        data = {"validation_type": VALIDATION_TYPE,
                "question_type": QUESTION_TYPE,
                "rating_preview": RATING_PREVIEW}
        return Response(data=data, status=status.HTTP_200_OK)


class SessionFilterTagListView(generics.ListAPIView):

    def list(self, request):
        data = SESSION_FILTER_TAGS
        return Response(data=data, status=status.HTTP_200_OK)


class StructuredDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = Session.objects.all().order_by('id')
    serializer_class = SessionQuestionAnswerPairSerializer


class SessionFilterView(generics.ListAPIView):
    serializer_class = FilterSessionSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        queryset = Session.objects.filter(trial=False)

        queryset = self._filter_current_ctc(queryset, self.request)
        queryset = self._filter_expected_ctc(queryset, self.request)
        queryset = self._filter_work_experience(queryset, self.request)
        queryset = self._filter_notice_period(queryset, self.request)
        queryset = self._filter_city(queryset, self.request)
        queryset = self._filter_tree(queryset, self.request)
        return queryset

    def _filter_current_ctc(self, queryset, request):
        ctc_max = request.query_params.get('cur_ctc_max')
        ctc_min = request.query_params.get('cur_ctc_min')
        if not ctc_max and not ctc_min:
            return queryset

        if ctc_max:
            structured_max = QuestionAnswerPair.objects.annotate(
                as_float=Cast(
                    'structured_answer__value', FloatField())).filter(
                as_float__lte=float(ctc_max)*100000).filter(
                structured_answer__entity='current_ctc_inr')
            if queryset:
                queryset = queryset.filter(
                    question_answer_pair__in=structured_max)

        if ctc_min:
            structured_min = QuestionAnswerPair.objects.annotate(
                as_float=Cast(
                    'structured_answer__value', FloatField())).filter(
                as_float__gte=float(ctc_min)*100000).filter(
                structured_answer__entity='current_ctc_inr')
            if queryset:
                queryset = queryset.filter(
                    question_answer_pair__in=structured_min)

        return queryset

    def _filter_expected_ctc(self, queryset, request):
        ctc_min = request.query_params.get('exp_ctc_min')
        ctc_max = request.query_params.get('exp_ctc_max')

        if not ctc_max and not ctc_min:
            return queryset

        if ctc_min:
            structured_min = QuestionAnswerPair.objects.annotate(
                as_float=Cast(
                    'structured_answer__value', FloatField())).filter(
                as_float__gte=float(ctc_min)*100000).filter(
                structured_answer__entity='expect_ctc_inr')
            if queryset:
                queryset = queryset.filter(
                    question_answer_pair__in=structured_min)

        if ctc_max:
            structured_max = QuestionAnswerPair.objects.annotate(
                as_float=Cast(
                    'structured_answer__value', FloatField())).filter(
                as_float__lte=float(ctc_max)*100000).filter(
                structured_answer__entity='expect_ctc_inr')
            if queryset:
                queryset = queryset.filter(
                    question_answer_pair__in=structured_max)
        return queryset

    def _filter_work_experience(self, queryset, request):
        exp_max = request.query_params.get('exp_max')
        exp_min = request.query_params.get('exp_min')

        if not exp_max and not exp_min:
            return queryset

        if exp_max:
            structured_max = QuestionAnswerPair.objects.annotate(
                as_float=Cast(
                    'structured_answer__value', FloatField())).filter(
                as_float__lte=float(exp_max)*365).filter(
                structured_answer__entity='work_experience')
            if queryset:
                queryset = queryset.filter(
                    question_answer_pair__in=structured_max)

        if exp_min:
            structured_min = QuestionAnswerPair.objects.annotate(
                as_float=Cast(
                    'structured_answer__value', FloatField())).filter(
                as_float__gte=float(exp_min)*365).filter(
                structured_answer__entity='work_experience')
            if queryset:
                queryset = queryset.filter(
                    question_answer_pair__in=structured_min)

        return queryset

    def _filter_notice_period(self, queryset, request):
        notice_period = request.query_params.get('notice_period')

        if not notice_period:
            return queryset
        if notice_period == '60+':
            notice_period = 60

        structured_data = QuestionAnswerPair.objects.annotate(
            as_float=Cast('structured_answer__value', FloatField())).filter(
            as_float__lte=float(notice_period)).filter(
            structured_answer__entity='notice_period')
        if queryset:
            queryset = queryset.filter(
                question_answer_pair__in=structured_data)
        return queryset

    def _filter_city(self, queryset, request):
        city = request.query_params.get('loc')

        if not city:
            return queryset

        city = city.split(',')
        structured_data = QuestionAnswerPair.objects.filter(
            structured_answer__entity='location',
            structured_answer__value__in=city)
        if queryset:
            queryset = queryset.filter(
                question_answer_pair__in=structured_data)
        return queryset

    def _filter_tree(self, queryset, request):
        tree_id = request.query_params.get('tree_id')
        if not tree_id:
            return queryset
        if queryset:
            queryset = queryset.filter(tree__in=tree_id.split(','))
        return queryset


class WebViewCheckBoxQuestions(generics.GenericAPIView):

    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        session = obtain_session(kwargs.get('recipient_id'))
        options = None
        if not session:
            return HttpResponse()
        options = Transition.objects.filter(current_state=session.state,
                                            tree=session.tree)
        question_text = session.state.question.text
        return render(request, 'webview.html', {
                                    "options": options,
                                    "recipient_id": kwargs.get('recipient_id'),
                                    "selected": False,
                                    "question_text": question_text})

    @xframe_options_exempt
    def post(self, request, *args, **kwargs):
        # import ipdb; ipdb.set_trace()
        session = obtain_session(kwargs.get('recipient_id'))
        facebook = Facebook(settings.FB_PAGE_ACCESS_TOKEN)
        skype = Skype()
        preferred_options = []
        preferred_options = request.POST.getlist('checkbox')
        preferred_options = ", ".join(preferred_options)
        tasks.update_session_state(session, preferred_options, '')

        payload = {'conversation_id': session.recipient_id}
        # Replying portion of the views via bot.
        if session.state:
            if session.state.question.validation_type == 'rating':
                if session.medium == 'facebook':
                    facebook.send_with_quick_reply(
                        session.recipient_id,
                        session.state.question.text, RATING.keys())
                else:
                    skype.send(payload,
                               session.state.question.text, RATING.keys())

            elif session.state.question.question_type == 'radio_buttons':
                quick_replies = tasks.fetch_quick_replies_for_question(session)
                if session.medium == 'facebook':
                    facebook.send_with_quick_reply(
                        kwargs.get('recipient_id'),
                        session.state.question.text, quick_replies)
                else:
                    skype.send_with_suggestion(
                        payload, session.state.question.text, quick_replies)

            elif (session.state.question.question_type == 'checkboxes' or
                  session.state.question.validation_type == 'city'):
                if session.medium == 'facebook':
                    facebook.send_with_button(session.recipient_id,
                                              session.state.question.text)
                else:
                    skype.send_with_hero_card(payload,
                                              session.state.question.text)
            else:
                if session.medium == 'facebook':
                    facebook.send(kwargs.get('recipient_id'),
                                  session.state.question.text)
                else:
                    skype.send(payload, session.state.question.text)
        else:
            if session.medium == 'facebook':
                facebook.send(session.recipient_id,
                              session.tree.completion_text)
            else:
                skype.send(payload, session.tree.completion_text)
            session.status = 'C'
            session.is_active = False
            session.save()
            tasks.post_session_to_callback(session.id)
        return render(request, 'webview.html', {"selected": True})


class GoogleMapSearchView(generics.GenericAPIView):

    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        session = obtain_session(kwargs.get('recipient_id'))
        if not session:
            return HttpResponse(
                "Seems like you have already chosen your location")
        question_text = session.state.question.text
        return render(request, 'maps.html', {
                            "selected": False,
                            "recipient_id": kwargs.get('recipient_id')})

    @xframe_options_exempt
    def post(self, request, *args, **kwargs):
        facebook = Facebook(settings.FB_PAGE_ACCESS_TOKEN)
        skype = Skype()
        session = obtain_session(kwargs.get('recipient_id'))
        if not session:
            return HttpResponse(
                "Seems like you have already chosen your location")
        from geopy.geocoders import Nominatim
        geolocator = Nominatim()
        location = request.POST.get('location')
        geo_location = geolocator.geocode(location,
                                          addressdetails=True, timeout=20)
        if geo_location:
            geo_loc = geo_location.raw.get('address').get('city')
            if not geo_loc:
                geo_loc = geo_location.raw.get('address').get('state_district')
        else:
            geo_loc = location.split(',')[0]
        geo_location = geo_loc
        tasks.update_session_state(session, geo_location, '')
        message_1 = 'Thanks for choosing your preferences.'
        message_2 = 'Please close off this window and continue'

        payload = {'conversation_id': session.recipient_id}
        # Replying portion of the views bot.
        if session.state:
            if session.state.question.validation_type == 'rating':
                if session.medium == 'facebook':
                    facebook.send_with_quick_reply(
                        session.recipient_id,
                        session.state.question.text, RATING.keys())
                else:
                    skype.send_with_suggestion(payload,
                        session.state.question.text, RATING.keys())

            elif session.state.question.question_type == 'radio_buttons':
                quick_replies = tasks.fetch_quick_replies_for_question(session)
                if session.medium == 'facebook':
                    facebook.send_with_quick_reply(
                        kwargs.get('recipient_id'),
                        session.state.question.text, quick_replies)
                else:
                    skype.send_with_suggestion(payload,
                                               session.state.question.text,
                                               quick_replies)
            elif (session.state.question.question_type == 'checkboxes' or
                  session.state.question.validation_type == 'city'):
                if session.medium == 'facebook':
                    facebook.send_with_button(
                                    kwargs.get('recipient_id'),
                                    session.state.question.text)
                else:
                    skype.send_with_hero_card(payload,
                                              session.state.question.text)
            else:
                if session.medium == 'facebook':
                    facebook.send(kwargs.get('recipient_id'),
                                  session.state.question.text)
                else:
                    skype.send(payload, session.state.question.text)
        else:
            if session.medium == 'facebook':
                facebook.send(session.recipient_id,
                              session.tree.completion_text)
            else:
                skype.send(kwargs.get('recipient_id'),
                           session.state.question.text)
            session.status = 'C'
            session.is_active = False
            session.save()
            tasks.post_session_to_callback(session.id)
        return render(request, 'maps.html', {"selected": True,
                                             "message_1": message_1,
                                             "message_2": message_2})


class SessionCancellation(generics.GenericAPIView):

    def put(self, request, *args, **kwargs):
        session = get_object_or_404(Session, id=kwargs.get('pk'))
        session.canceled = True
        session.status = 'F'
        session.is_active = False
        session.save()
        email_admins(session)
        return Response({
            'status': 'Cancelled',
            'detail': 'Session with session_id {} has been successfully cancelled'.format(
                            session.id)},
            status=status.HTTP_200_OK)

# class SessionFailureCallback(generics.GenericAPIView):

#     def post(self, request, *args, **kwargs):
#         data = json.loads(request.body.decode('utf-8'))
#         if not data.get('session_ids'):
#             return Response({
#                 'status': 'Failed',
#                 'detail': "session_ids is required"},
#                 status=status.HTTP_400_BAD_REQUEST)
#         for session_id in data.get('session_ids'):
#             session = get_object_or_404(Session, id=session_id)
#             session.status = 'F'
#             session.save()
#         return Response({
#             'status': 'Success',
#             'message': 'Successfully updated session status'},
#             status=status.HTTP_200_OK)
