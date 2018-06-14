from django.conf.urls import url, include

from rest_framework import routers


from auth import views

router = routers.DefaultRouter()
router.register(r'signup', views.UserViewSet)

urlpatterns = [
    url(r'^api-auth', include(
                    'rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(router.urls)),
]
