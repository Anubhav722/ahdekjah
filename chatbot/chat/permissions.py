from auth.models import Client
from .models import Session, Tree

from rest_framework import permissions
from rest_framework.exceptions import APIException


class IsAuthenticated(permissions.BasePermission):
    """
    Allows access only to active users
    """
    def has_permission(self, request, view):
        client_key = request.META.get('HTTP_CHATBOT_CLIENT_KEY', None)
        client_secret = request.META.get('HTTP_CHATBOT_CLIENT_SECRET', None)

        try:
            assert (client_key and client_secret)
            client = Client.objects.get(key=client_key, secret=client_secret)
        except(AssertionError, Client.DoesNotExist):
            raise APIException({
                    'status': 'Unauthorized',
                    'message': 'Authentication values are incorrect/missing',
                })

        request.client = client
        return request


class IsOwner(permissions.BasePermission):
    """Custom permission class to allow only Session owners to edit them."""

    def has_object_permission(self, request, view, obj):
        """Return True if permission is granted to the Session owner."""
        if isinstance(obj, Session):
            return obj.belongs_to.key == request.META.get(
                                            'HTTP_CHATBOT_CLIENT_KEY')
        return obj.belongs_to.key == request.META.get(
                                            'HTTP_CHATBOT_CLIENT_KEY')


class IsTreeOwner(permissions.BasePermission):
    """
    Custom permission class to allow only Tree owners to
       edit, delete and view them
    """

    def has_object_permission(self, request, view, obj):
        """Return true if permission is granted to Tree owner."""
        if isinstance(obj, Tree):
            return obj.belongs_to.key == request.META.get(
                                            'HTTP_CHATBOT_CLIENT_KEY')
        return obj.belongs_to.key == request.META.get(
                                            'HTTP_CHATBOT_CLIENT_KEY')
