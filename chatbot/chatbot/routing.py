from channels import route, Channel
import json
from channels.sessions import channel_session
from channels.auth import channel_session_user_from_http, channel_session_user
from chat import consumers


@channel_session
def ws_send(reply, message):
    reply = json.dumps(reply)
    message.reply_channel.send({'text': reply})


def ws_receive(message):
    incoming_message = message.get('text')
    incoming_message = json.loads(incoming_message)
    reply, validation_type = consumers.handle_webchat_callback(
                                incoming_message)
    if reply:
        reply['message']['validation_type'] = validation_type
    ws_send(reply, message)


@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({"accept": True})


@channel_session_user
def ws_disconnect(message):
    message.reply_channel.send({'accept': False})

channel_routing = [
    route("websocket.receive", ws_receive),
    route("websocket.connect", ws_connect),
    route("websocket.disconnect", ws_disconnect),
]
