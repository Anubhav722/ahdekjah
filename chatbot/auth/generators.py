import os, random, hashlib, binascii

# Django Imports
from django.contrib.auth.models import User

# App Imports
from .constants import (
    CLIENT_KEY_GENERATOR_LENGTH, CLIENT_SECRET_GENERATOR_LENGTH,
    UNICODE_ASCII_CHARACTER_SET
)
from .common import generate_token


class BaseHashGenerator(object):
    """
    All generators should extend this class overriding `.hash()` method.
    """
    def hash(self):
        raise NotImplementedError("Subclasses should implement this!")


class ClientKeyGenerator(BaseHashGenerator):
    """
    Generate a client_key
    """
    def hash(self):
        return generate_token(
            length=CLIENT_KEY_GENERATOR_LENGTH,
            chars=UNICODE_ASCII_CHARACTER_SET
        )


class ClientSecretGenerator(BaseHashGenerator):
    """
    Generate a client_secret
    """
    def hash(self):
        return generate_token(
            length=CLIENT_SECRET_GENERATOR_LENGTH,
            chars=UNICODE_ASCII_CHARACTER_SET
        )


def generate_client_key():
    """
    Generate a suitable client key
    """
    return ClientKeyGenerator().hash()


def generate_client_secret():
    """
    Generate a suitable client secret
    """
    return ClientSecretGenerator().hash()
