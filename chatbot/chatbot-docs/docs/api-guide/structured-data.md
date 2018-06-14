# StructuredData

StructuredData is the data obtained after extracting useful information from the chat.
For example: `city`, `current_ctc_inr`, `work_experience` etc.

## Retrive StructuredData Endpoint

```
GET /chat/session/structured/<session-id/structured/
```

> NOTE: All the data fetched from chat is converted into a standard fixed unit.

### Permissions

Only authenticated users and Session owners can view the structured data.

### Sample Request

```
GET /chat/session/structured/<session-id/structured/

{
    "question_answer_pair": [
        {
            "answer": "4.5 lacs",
            "question": "What is your current annual CTC in lakhs?",
            "structured_answer": {
                "entity": "CTC_INR",
                "unit": "inr",
                "value": "450000.0"
            }
        },
        {
            "answer": "Ok I am expecting a ctc of 12 lacs",
            "question": "What is your expected annual CTC in lakhs?",
            "structured_answer": {
                "entity": "CTC_INR",
                "unit": "inr",
                "value": "1200000"
            }
        },
        {
            "answer": "I have a work experience of 11 months",
            "question": "What is your total work experience?",
            "structured_answer": {
                "entity": "duration",
                "unit": "days",
                "value": "False"
            }
        },
        {
            "answer": "I am currently in lucknow",
            "question": "What is your current city?",
            "structured_answer": {
                "entity": "location",
                "unit": "city",
                "value": "lucknow"
            }
        },
        {
            "answer": "yes",
            "question": "Are you willing to relocate?",
            "structured_answer": {
                "entity": "boolean",
                "unit": "bool",
                "value": "yes"
            }
        },
        {
            "answer": "no",
            "question": "Do you have any notice period at your current company?",
            "structured_answer": {
                "entity": "boolean",
                "unit": "bool",
                "value": "no"
            }
        },
        {
            "answer": "2017-09-01",
            "question": "Great. When can you join us?",
            "structured_answer": {
                "entity": "datetime",
                "unit": "date",
                "value": "2017-09-01"
            }
        }
    ]
}
```

## StructuredData Update View

### Permissions

Only authenticated users and Session Owners can update the StructuredData.

### Sample Request

```
PUT /chat/session/<session-id>/structured/
```

## StructuredData Delete View

### Permissions

Only authenticated users and session owners can delete the StructuredData.

### Sample Request

```
DELETE /chat/session/<session-id>/structured/
```