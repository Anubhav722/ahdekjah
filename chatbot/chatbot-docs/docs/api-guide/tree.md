# Tree Endpoint

## Tree List View

### Permissions

Authenticated users can view the default tree.

### Sample Response:

```
GET /trees/

[
    {
        "id": 1,
        "tree_name": "Default Tree",
        "greeting_text": "This is on behalf of Happy Company. We would like to ask you a few questions.",
        "completion_text": "Thanks for your time. Have a nice day :)",
        "transitions": [
            {
                "next_question": 1,
                "number": 0,
                "answers": [],
                "question": {
                    "is_follow_up": false,
                    "question_type": "text_answer",
                    "text": "What is your current annual CTC in lakhs?",
                    "quick_replies": "",
                    "validation_type": "ctc_inr"
                }
            },
            {
                "next_question": 2,
                "number": 1,
                "answers": [],
                "question": {
                    "is_follow_up": false,
                    "question_type": "text_answer",
                    "text": "What is your expected annual CTC in lakhs?",
                    "quick_replies": "",
                    "validation_type": "ctc_inr"
                }
            },
            {
                "next_question": 3,
                "number": 2,
                "answers": [],
                "question": {
                    "is_follow_up": false,
                    "question_type": "text_answer",
                    "text": "What is your total work experience?",
                    "quick_replies": "",
                    "validation_type": "work_experience"
                }
            },
            {
                "next_question": 4,
                "number": 3,
                "answers": [],
                "question": {
                    "is_follow_up": false,
                    "question_type": "text_answer",
                    "text": "What is your current location (City)?",
                    "quick_replies": "",
                    "validation_type": "city"
                }
            },
            {
                "next_question": null,
                "number": 4,
                "answers": [
                    {
                        "next_question": 5,
                        "text": "Bangalore, Pune, Mumbai"
                    }
                ],
                "question": {
                    "is_follow_up": false,
                    "question_type": "checkboxes",
                    "text": "Please select the cities you are OK to work in?",
                    "quick_replies": "",
                    "validation_type": null
                }
            },
            {
                "next_question": null,
                "number": 5,
                "answers": [
                    {
                        "next_question": 6,
                        "text": "yes"
                    },
                    {
                        "next_question": 7,
                        "text": "no"
                    }
                ],
                "question": {
                    "is_follow_up": false,
                    "question_type": "text_answer",
                    "text": "Do you have any notice period at your current company?",
                    "quick_replies": "yes,no",
                    "validation_type": null
                }
            },
            {
                "next_question": 8,
                "number": 6,
                "answers": [],
                "question": {
                    "is_follow_up": true,
                    "question_type": "text_answer",
                    "text": "How long is your notice period?",
                    "quick_replies": "",
                    "validation_type": "notice_period"
                }
            },
            {
                "next_question": 8,
                "number": 7,
                "answers": [],
                "question": {
                    "is_follow_up": true,
                    "question_type": "text_answer",
                    "text": "Great. When can you join us?",
                    "quick_replies": "",
                    "validation_type": "notice_period"
                }
            },
            {
                "next_question": 9,
                "number": 8,
                "answers": [],
                "question": {
                    "is_follow_up": false,
                    "question_type": "text_answer",
                    "text": "What are the skills you are comfortable with?",
                    "quick_replies": "",
                    "validation_type": null
                }
            },
            {
                "next_question": 10,
                "number": 9,
                "answers": [],
                "question": {
                    "is_follow_up": false,
                    "question_type": "text_answer",
                    "text": "Why do you want to change the job?",
                    "quick_replies": "",
                    "validation_type": null
                }
            },
            {
                "next_question": null,
                "number": 10,
                "answers": [],
                "question": {
                    "is_follow_up": false,
                    "question_type": "text_answer",
                    "text": "Why do you want join our company?",
                    "quick_replies": "",
                    "validation_type": null
                }
            }
        ]
    }
]
```


## Tree Create View

```
POST /trees/
```

### Permissions

Only a client can create a tree.
> NOTE: Must provide `chatbot-client-key` and `chatbot-client-secret` in headers to access the tree endpoint.

```
{
	"chatbot-client-key": "xxxx",
	"chatbot-client-secret": "yyyy"
}
```

### Example Request

```
POST /trees/


   "tree_name": "DARTH VADER Tree",
    "completion_text": "Thank you from zeroth tree. We will get back to you",
    "greeting_text": "Hello",
    "transitions": [{
            "number": 1,
            "question": {
                "text": "Have you ever worked with ionic?",
                "validation_type": "bool",
                "is_follow_up": false,
                "quick_replies": "yes,no",
                "question_type": "answer_text"
            },
            "answers": [{
                "text": "yes",
                "next_question": 2
            }, {
                "text": "no",
                "next_question": 3
            }],
            "next_question": null
        },

        {
            "number": 2,
            "question": {
                "text": "Where did you do your engineering?",
                "validation_type": "",
                "is_follow_up": false,
                "question_type": "answer_text",
                "quick_replies": ""
            },
            "answers": [],
            "next_question": null
        },
        {
            "number": 3,
            "question": {
                "text": "Are you willing to learn ionic",
                "validation_type": "",
                "is_follow_up": true
                "quick_replies": "yes, no",
                "question_type": "answer_text"
            },
            "answers": [{
                "text": "yes",
                "next_question": null
            }, {
                "text": "no",
                "next_question": null
            }],
            "next_question": null
        }
    ]
}
```

### Example Response

```
{
    "status": "Created",
    "detail": "Tree has been successfully created.",
    "tree_id": 2,
    "tree_name": "DARTH VADER Tree"
}
```

## Tree Update View

```
PUT /trees/<tree-id>/
```

### Permissions

Only authenticated clients can update their own tree i.e. TreeOwners can only edit a particular tree. 

> NOTE: Default tree cannot be edited. It is a read-only tree.

> NOTE: Reordering can also be done using PUT request.

### Sample Request

> NOTE: Same as create request.

```
PUT /trees/2/

   "tree_name": "DARTH VADER Tree",
    "completion_text": "Thank you from zeroth tree. We will get back to you",
    "greeting_text": "Hello",
    "transitions": [{
            "number": 1,
            "question": {
                "text": "Have you ever worked with ionic?",
                "validation_type": "bool",
                "is_follow_up": false,
                "quick_replies": "yes,no",
                "question_type": "answer_text"
            },
            "answers": [{
                "text": "yes",
                "next_question": 2
            }, {
                "text": "no",
                "next_question": 3
            }],
            "next_question": null
        },

        {
            "number": 2,
            "question": {
                "text": "Where did you do your engineering?",
                "validation_type": "",
                "is_follow_up": false,
                "question_type": "answer_text",
                "quick_replies": ""
            },
            "answers": [],
            "next_question": null
        },
        {
            "number": 3,
            "question": {
                "text": "Are you willing to learn ionic",
                "validation_type": "",
                "is_follow_up": true
                "quick_replies": "yes, no",
                "question_type": "answer_text"
            },
            "answers": [{
                "text": "yes",
                "next_question": null
            }, {
                "text": "no",
                "next_question": null
            }],
            "next_question": null
        }
    ]
}
```

### Sample Response

```
{
    "tree_name": "ZEROTH Tree",
    "detail": "Tree has been successfully updated.",
    "status": "Updated",
    "tree_id": 2
}
```

## Tree Delete View

```
DELETE /trees/<tree-id>/
```

### Permissions

Only Authenticated users and TreeOwners can a delete a tree.

> NOTE: Default trees cannot be deleted.

### Sample Request

```
DELETE /trees/2/

{
    "detail": "Tree with id: 2, name: Zeroth Tree has been deleted",
    "status": "Deleted"
}
```

## Tree Detail View

```
GET /trees/<tree-id>/
```

### Permissions

Only Authenticated users and TreeOwners can access tree details

### Sample Request

```
GET /trees/<tree-id>/

{
    "id": 2,
    "tree_name": "First Tree",
    "greeting_text": "This is on behalf of Happy Company. Thanks for applying for the job. We've got some quick questions for you. Are you ready?",
    "completion_text": "Thanks for your time. We'll get back to you ASAP. Meanwhile, you can go through our website to know more about us: http://happycompany.com",
    "transitions": [
        {
            "next_question": 1,
            "number": 0,
            "answers": [],
            "question": {
                "is_follow_up": false,
                "question_type": "text_answer",
                "text": "What is your current annual CTC in lakhs?",
                "quick_replies": "",
                "validation_type": "ctc_inr"
            }
        },
        {
            "next_question": 2,
            "number": 1,
            "answers": [],
            "question": {
                "is_follow_up": false,
                "question_type": "text_answer",
                "text": "What is your expected annual CTC in lakhs?",
                "quick_replies": "",
                "validation_type": "ctc_inr"
            }
        },
        {
            "next_question": 3,
            "number": 2,
            "answers": [],
            "question": {
                "is_follow_up": false,
                "question_type": "text_answer",
                "text": "What is your total work experience?",
                "quick_replies": "",
                "validation_type": "work_experience"
            }
        },
        {
            "next_question": null,
            "number": 3,
            "answers": [
                {
                    "next_question": 4,
                    "text": "yes"
                },
                {
                    "next_question": 5,
                    "text": "no"
                }
            ],
            "question": {
                "is_follow_up": false,
                "question_type": "text_answer",
                "text": "Do you have any notice period at your current company?",
                "quick_replies": "yes,no",
                "validation_type": null
            }
        },
        {
            "next_question": 6,
            "number": 4,
            "answers": [],
            "question": {
                "is_follow_up": true,
                "question_type": "text_answer",
                "text": "How long is your notice period?",
                "quick_replies": "",
                "validation_type": "notice_period"
            }
        },
        {
            "next_question": 6,
            "number": 5,
            "answers": [],
            "question": {
                "is_follow_up": true,
                "question_type": "text_answer",
                "text": "Great. When can you join us?",
                "quick_replies": "",
                "validation_type": "notice_period"
            }
        },
        {
            "next_question": 7,
            "number": 6,
            "answers": [],
            "question": {
                "is_follow_up": false,
                "question_type": "text_answer",
                "text": "What is your current location (City)?",
                "quick_replies": "",
                "validation_type": "city"
            }
        },
        {
            "next_question": null,
            "number": 7,
            "answers": [
                {
                    "next_question": 8,
                    "text": "Bangalore, Pune, Mumbai"
                }
            ],
            "question": {
                "is_follow_up": false,
                "question_type": "checkboxes",
                "text": "Please select the cities you are OK to work in?",
                "quick_replies": "",
                "validation_type": null
            }
        },
        {
            "next_question": 9,
            "number": 8,
            "answers": [],
            "question": {
                "is_follow_up": false,
                "question_type": "text_answer",
                "text": "What are the skills you are comfortable with?",
                "quick_replies": "",
                "validation_type": null
            }
        },
        {
            "next_question": 10,
            "number": 9,
            "answers": [],
            "question": {
                "is_follow_up": false,
                "question_type": "text_answer",
                "text": "Why do you want to change the job?",
                "quick_replies": "",
                "validation_type": null
            }
        },
        {
            "next_question": null,
            "number": 10,
            "answers": [],
            "question": {
                "is_follow_up": false,
                "question_type": "text_answer",
                "text": "Why do you want join our company?",
                "quick_replies": "",
                "validation_type": null
            }
        }
    ]
}
```