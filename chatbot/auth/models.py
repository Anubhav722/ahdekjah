from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save

from rest_framework.authtoken.models import Token

from base.models import BaseModel
from auth.generators import (generate_client_key,
                            generate_client_secret
                            )

class Client(BaseModel):
    """
    Client represents a single valid entity that can access the chatbot.
    """

    name = models.CharField(unique=True, null=False, blank=False, max_length=50)
    description = models.CharField(max_length=255)
    key = models.CharField(max_length=50)
    secret = models.CharField(max_length=255)

    def __str__(self):
        return self.name


@receiver(signal=post_save, sender=User)
def create_access_token_for_user(sender, instance, created=False, **kwargs):
    """
    Automatically create access_token for user whenever user object is created
    """
    if created:
        try:
            Token.objects.create(user=instance)
            client = Client.objects.create(name=instance.username)
        except Token.DoesNotExist:
            return None


@receiver(signal=post_save, sender=Client)
def create_client_key_and_secret(sender, instance, created=False, **kwargs):
    """
    Automatically create client key and client secret whenever a user is created
    """
    if created:
        client_key = generate_client_key()
        while Client.objects.filter(key=client_key).exists():
            client_key = generate_client_key()

        client_secret = generate_client_secret()
        while Client.objects.filter(secret=client_secret).exists():
            client_secret = generate_client_secret()

        instance.key = client_key
        instance.secret = client_secret
        instance.save()
