from django.contrib.auth.models import User

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework import mixins

from auth.models import Client
from auth.serializers import UserSerializer
# Create your views here.


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint that allows users to register,
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        client = Client.objects.last()
        return Response({'client_key': client.key,
                         'client_secret': client.secret},
                        status=status.HTTP_201_CREATED,
                        headers=headers)
