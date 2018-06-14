from collections import OrderedDict

rating = {'Beginner': 1,
          'Intermediate': 2, 'Expert': 3, 'Professional': 4, 'Yoda': 5}
RATING = OrderedDict(sorted(rating.items(), key=lambda t: t[1]))
CTC_FORMAT_INR = ['lac', 'lakh', 'lpa', 'crore', 'cpa']

WORK_EXPERIENCE_FORMAT = ['year', 'yr', 'month', 'week', 'day']
WIT_EXTRACTION_VALIDATION_TYPES = ['notice_period',
                                   'ctc_inr', 'work_experience']

VALIDATION_TYPE_WITH_QUICK_REPLIES = ['bool', 'rating']

EXTENSIONS = ['not working', 'fresher', 'founder', 'not employed', 'college',
              'startup', 'co-founder', 'unemployed', 'graduated',
              'no experience', 'not worked', 'experience', 'working', 'work',
              'first', 'job', 'not', 'applying', 'jobs']

RATING_PREVIEW = [
    {"label": "Beginner"},
    {"label": "Intermediate"},
    {"label": "Expert"},
    {"label": "Professional"},
    {"label": "Yoda"}
    ]

QUESTION_TYPE = [
    {"type": "text_answer",
     "label": "Text Answer",
     "help_text": "Candidate can write any free text"},
    {"type": "radio_buttons",
     "label": "Single Choice",
     "help_text": "Candidate can select multiple answers from the given options"},
    {"type": "checkboxes",
     "label": "Multiple Choice",
     "help_text": "Candidate can select a single answer from the given options"}
]

VALIDATION_TYPE = [
    {"type": "ctc_inr",
     "label": "CTC (INR)",
     "help_text": "Extracts amount from the user input"},
    {"type": "city",
     "label": "City",
     "help_text": "Collects city from the user"},
    {"type": "notice_period",
     "label": "Notice Period",
     "help_text": "Extracts duration from the user input"},
    {"type": "work_experience",
     "label": "Work Experience",
     "help_text": "Exracts days/months/years from the user input"},
    {"type": "rating",
     "label": "Rating",
     "help_text": "Shows ratings (like Beginner/etc) to the user"},
    {"type": "None",
     "label": "None",
     "help_text": "No validation required"}
]


VALIDATION_RESPONSES = {
    "city": [
        "Hey {}, Please make sure to share your location via maps"],
    "ctc_inr": [
        "Hey {}, did you mean {} lpa?",
        "Hey {}, please make sure you are entering CTC in lpa."],
    "notice_period": [
        "Hey {}, did you mean {} weeks?",
        "Hey {}, make sure you entered your time duration in days/months/weeks",
        "Ok! Let me confirm, you can join us on {}?"],
    "work_experience": [
        "Hey {}, did you mean {} years?",
        "Hey {}, please make sure you are entering work experience in years.",
        "Hey {}, are you kiddin'? Seriously {} years :O"],
    "rating": [
        "Hey {}, can you please provide an apt rating."],
    "bool": [
        "Hey {}, {}"],
    "reminder_text": [
        "Hi there, it seems like we haven't completed our conversation yet. Let me know when you're ready. :)"],
    "get_started_text": [
        "Okay. Ping me when ever you're ready.",
        "Okay. Thanks for your time."],
    "analyzers": [
        "Hey there, please make sure to check your spelling before hitting send. ",
        'I am not sure what "{}" means. '],
    "skype_verification": [
        "Hi {}, please paste/send the verification code to get started.",
        "Hey {}, it was not a valid verification code."]
}

SESSION_FILTER_TAGS = [
                    {'label': 'Notice Period',
                     'single_params': True,
                     'question_type': 'single_choice',
                     'options': [
                      {'notice_period': 15, 'title': '15 days'},
                      {'notice_period': 30, 'title': '30 days'},
                      {'notice_period': 45, 'title': '45 days'},
                      {'notice_period': 60, 'title': '60 days'},
                      {'notice_period': '60+', 'title': '60+ days'}]},
                    {'label': 'Current Annual CTC (in lakhs)',
                     'question_type': 'single_choice',
                     'double_params': True,
                     'options': [
                      {'cur_ctc_min': 0, 'cur_ctc_max': 3, 'title': '0-3 lpa'},
                      {'cur_ctc_min': 3, 'cur_ctc_max': 6, 'title': '3-6 lpa'},
                      {'cur_ctc_min': 6, 'cur_ctc_max': 12, 'title': '6-12 lpa'},
                      {'cur_ctc_min': 12,'cur_ctc_max': 20, 'title': '12-20 lpa'},
                      {'cur_ctc_min': 20, 'title': '20+ lpa'}]
                     },

                    {'label': 'Expected Annual CTC (in lakhs)',
                     'question_type': 'single_choice',
                     'double_params': True,
                     'options': [
                      {'exp_ctc_min': 0, 'exp_ctc_max': 3, 'title': '0-3 lpa'},
                      {'exp_ctc_min': 3, 'exp_ctc_max': 6, 'title': '3-6 lpa'},
                      {'exp_ctc_min': 6, 'exp_ctc_max': 12, 'title': '6-12 lpa'},
                      {'exp_ctc_min': 12,'exp_ctc_max': 20, 'title': '12-20 lpa'},
                      {'exp_ctc_min': 20, 'title': '20+ lpa'}]
                     },

                    {'label': 'Total year of experience (in years)',
                     'question_type': 'single_choice',
                     'double_params': True,
                     'options': [
                      {'exp_min': 0, 'exp_max': 1, 'title': '0-1 yr'},
                      {'exp_min': 1, 'exp_max': 3, 'title': '1-3 yrs'},
                      {'exp_min': 3, 'exp_max': 6, 'title': '3-6 yrs'},
                      {'exp_min': 6, 'exp_max': 12, 'title': '6-12 yrs'},
                      {'exp_min': 12, 'title': '12+ yrs'}]
                     },

                    {'label': 'Current Location',
                     'question_type': 'multiple_choice',
                     'single_params': True,
                     'options': [
                      {'loc': 'bangalore', 'title': 'Bangalore'},
                      {'loc': 'pune', 'title': 'Pune'},
                      {'loc': 'hyderabad', 'title': 'Hyderabad'},
                      {'loc': 'chennai', 'title': 'Chennai'}]},
                     ]
