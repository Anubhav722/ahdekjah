import unittest

from ..facebook import Facebook

test_access_token = "EAAWBsuDybjkBABDpUR8VOdJMqsVSuMRvLXDwsUBuVqcEGtZAVZCAHN5anHcnPM9TZCMirAXUO1qFBOVFbsiK8ZC67mmIOcpiCqPMmxAmujGBeDNo93zeSaLaiuFRLOZA4QxKfCO7NQRKjXa1DbaoLncBRsbSKV6cxSShxIKpbWExMZCSTCTCNq"

class TestFacebook(unittest.TestCase):
    def setUp(self):
        self.chat = Facebook(access_token=test_access_token)

    def test_message_url(self):
        expected_url = "https://graph.facebook.com/v2.6/me/messages/?access_token="+test_access_token

        assert self.chat.message_url() == expected_url

    def test_create_payload(self):
        input_tests = [
            {'expected': {'recipient': {'id': "123"}, 'message': {'text': "hello"}}, 'input': {'message': "hello", 'recipient_id': "123"}},
            {'expected': {'recipient': {'id': "145"}, 'message': {'text': "hi, hello"}}, 'input': {'message': 'hi, hello', 'recipient_id': "145"}},
            {'expected': {'recipient': {'id': ""}, 'message': {'text': "hi, hello"}}, 'input': {'message': 'hi, hello', 'recipient_id': ""}},
            {'expected': {'recipient': {'id': ""}, 'message': {'text': ""}}, 'input': {'message': '', 'recipient_id': ""}},
        ]


        for test in input_tests:
             out = self.chat.create_payload(test['input']['message'], test['input']['recipient_id'])
             assert out == test['expected']
