# Miscellaneous
import random

# App Imports
from .constants import UNICODE_ASCII_CHARACTER_SET


def generate_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    """
    Generates token

    ======================
    random.SystemRandom()
    ======================
    https://docs.python.org/2/library/random.html#random.SystemRandom
    Class that uses the os.urandom() function for
    generating random numbers from sources provided by the OS.
    Doesn't rely on software state & sequences aren't reproducible.
    """
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))
