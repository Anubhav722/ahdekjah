# Webhook

## Automated Facebook Integration

### GET Method

Verifies `hub.verify_token` via GET request from Facebook and then posts back `hub.challenge`.

* The token exchange takes place via GET request:
```
<WSGIRequest: GET '/chat/webhook/?hub.mode=subscribe&hub.challenge=762832905&hub.verify_token=7697631870'>
```
>NOTE: The `hub.verify_token` is the one set by the developer to verify the `callback_url`, The response returned is then `hub.challenge` which confirms that the verification is complete.

** Description for the above request :**
 
* `callback_url` : /chat/webhook/
* `hub.verify_token` : 7697631870
* `hub.challenge` : 762832905

### POST Method

Parses incoming messages via POST request from Facebook in `handle_facebook_callback`.

* Sample post request for incoming message
```
<WSGIRequest: POST '/chat/webhook/'>
```

* Sample of incoming message
```
{u'entry': [{u'id': u'128922990987384',
             u'messaging': [{u'message': {u'mid': u'mid.$cAAAvslv3zhdjvrtYAldjXYO771AA',
                                          u'seq': 153783,
                                          u'text': u'hi there.'},
                             u'recipient': {u'id': u'128922990987384'},
                             u'sender': {u'id': u'969833033053167'},
                             u'timestamp': 1501316911106}],
             u'time': 1501316911147}],
 u'object': u'page'}
```

* Sample of response message sent by the bot
```
{u'entry': [{u'id': u'128922990987384',
             u'messaging': [{u'message': {u'app_id': 1377689312323892,
                                          u'is_echo': True,
                                          u'mid': u'mid.$cAAAvslv3zhdjvrteA1djXYVnmSlN',
                                          u'seq': 153785,
                                          u'text': u'Thank you for your time..!!'},
                             u'recipient': {u'id': u'969833033053167'},
                             u'sender': {u'id': u'128922990987384'},
                             u'timestamp': 1501316912643}],
             u'time': 1501316912679}],
 u'object': u'page'}
```

* Sample response when message is delivered to the user

```
{u'entry': [{u'id': u'128922990987384',
             u'messaging': [{u'delivery': {u'mids': [u'mid.$cAAAvslv3zhdjvrteA1djXYVnmSlN'],
                                           u'seq': 0,
                                           u'watermark': 1501316912643},
                             u'recipient': {u'id': u'128922990987384'},
                             u'sender': {u'id': u'969833033053167'},
                             u'timestamp': 1501316913034}],
             u'time': 1501316913037}],
 u'object': u'page'}
```

* Sample response recieved when the user has read the message

```
{u'entry': [{u'id': u'128922990987384',
             u'messaging': [{u'read': {u'seq': 0,
                                       u'watermark': 1501316912643},
                             u'recipient': {u'id': u'128922990987384'},
                             u'sender': {u'id': u'969833033053167'},
                             u'timestamp': 1501316914630}],
             u'time': 1501316914633}],
 u'object': u'page'}
```

## Setup

Visit [Facebook Webhook setup](https://developers.facebook.com/docs/messenger-platform/webhook-reference#setup) to learn more on how to setup webhooks.


>NOTE: You also need to subscribe a page to an app.

```
curl -X POST "https://graph.facebook.com/v2.6/me/subscribed_apps?access_token=PAGE_ACCESS_TOKEN"
```

If subscription is successful, you will receive a response:

```
{
  "success": true
}
```