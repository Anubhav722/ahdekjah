README
=======

Chatbot is a simple standalone bot, that can be used to initiate chat with human via fb messanger(possibly other medium in future) and collect all the coversation.

As a client, you signup and get `client-id` and `client-secret`. Every other api request needs to be authenticated via this client-id and secret.

SETUP
======

1. Make virtualenv like: `mkvirtualenv bot`.
2. Activate virtualenv `workon bot`.
3. Make sure you are using python3: `alias python=python3`.
4. Clone the repo like: `git clone git@code.launchyard.com:root/chatbot.git`.
5. Install all the dependencies: `pip install -r chatbot/requirements/local.txt`
6. setup your postgres db_name and db_password: https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04
7. export the environment variables: `source chatbot.env`.

CREDENTIALS
==============

ENDPOINTS AND USAGE
========================

1. Signup and Get `client-id` and `client-secret`.
2. Create `Tree` with collection of questions.
3. Initiate `Chat` conversation with `recipient_phone`, `identifier`, `recipient_email` and `tree_id`
4. Get the entire conversation details via `session_id`
5. Get /update/delete the `tree` that belongs to particular client.

DESIGN (only for Developers)
====================================

### Apps

* auth - Deals with all the accounts and authentication related functionalities.
* chat - Main app where message conversation is handled
* base - Contains default inheritance class for app models.

### Packages
* medium - A simple abstraction on which chatbot communicates. e.g: facebook messanger, watsapp, slack etc.
* nlp - Simple package that helps in structuring the user responses in the conversation.

### Apps relations

#### Chat
- `Session` is an domain model which stores the entire conversation happened between the bot and a user. Every `session` conversation have unique `session_id`.
- Each statement in the conversation corresponds to `message` object. In other words, `chat` is collection of messages.
- `Tree` is just the collection of questions, answers and transitions. Transitions decide the flow of the entire conversation.
- A `Question` can have multiple possible_answers and (optionaly) one correct answer.
- `Question` also have `validation_type`, `quick_replies` which is to understand what type of question the bot is gonna ask user. e.g: FreeText?, Yes/No, Multiple choice
- `Validation Types` : Validation types being supported for now are `CTC (INR)`, City, Notice Period, Work Experience, Rating.
- `Answer` model provides facilities to generate string match. Next question that needs to be asked is decided as per `user_input` (follow_ups).
- `StructredAnswer` stores all the relevant info fetched from the entire user-bot(session) conversation.
- `QuestionAnswerPair` stores all the raw conversation between user-bot.

#### Auth
- `Client` model generate `chatbot-client-key` for `chatbot-client-secret` whenever a new user is registered i.e user-specific.
- `chatbot-client-key` and `chatbot-client-secret` will be required wherever authentication is required.