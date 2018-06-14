import requests

def has_connection():
    try:
        requests.get('https://google.com/')
        return True
    except requests.ConnectionError:
        return False

requires_internet = pytest.mark.skipif(
    """
    A simple helper decorator, that can used to skip the test case if that
    requires internet connectivity.
    """

    not has_connection(),
    reason="requires internet connectivity"
)
