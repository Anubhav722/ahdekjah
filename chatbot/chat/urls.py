from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter
from .views import *

router = SimpleRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^webhook/?$', Webhook.as_view(), name='webhook'),
    url(r'^initiate/?$', InitiateChat.as_view(), name='initiate'),
    url(r'^session/(?P<pk>[0-9]+)/$',
        SessionDetailView.as_view(), name='session'),

    url(r'^session/(?P<pk>[0-9]+)/structured/$',
        StructuredDetailView.as_view(), name='structured'),

    url(r'^session/cancellation/(?P<pk>[0-9]+)/$',
        SessionCancellation.as_view(), name='cancellation'),

    url(r'^types/?$',
        DefaultValidationTypeListView.as_view(), name='validation-type'),

    url(r'^default/?$', DefaultTreeDetailView.as_view(), name='default'),
    url(r'^filter/?$', SessionFilterView.as_view(), name='filter'),
    url(r'^demo/?$', ClientDemoView.as_view(), name='demo'),
    url(r'^filter/tags/?$',
        SessionFilterTagListView.as_view(), name='filter-tag'),

    url(r'^webview/(?P<recipient_id>[A-Za-z0-9:_-]+)/$',
        WebViewCheckBoxQuestions.as_view(), name='webview'),

    url(r'maps/(?P<recipient_id>[A-Za-z0-9:_-]+)/$',
        GoogleMapSearchView.as_view(), name='maps'),

    url(r'skype/$', SkypeIntegration.as_view(), name='skype'),
]
