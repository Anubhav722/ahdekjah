# Types Endpoint

## Validation Types

User's can add a validation type while creating a question.
Available validation types are as follows:

* notice_period
* ctc_inr
* work_experience
* rating
* city
* bool

## Question Types

Question type have been classified as:

* Answer Text
* Radio Buttons
* Checkboxes


### Permissions

No permissions are required to access this endpoint.

### Sample Request

```
GET /chat/types/
```


### Sample Response

```
{
    "question_type": [
        {
            "type": "answer_text",
            "label": "Answer Text"
        },
        {
            "type": "radio_buttons",
            "label": "Radio Buttons"
        },
        {
            "type": "checkboxes",
            "label": "Checkboxes"
        }
    ],
    "validation_type": [
        {
            "type": "ctc_inr",
            "label": "CTC (INR)"
        },
        {
            "type": "city",
            "label": "City"
        },
        {
            "type": "notice_period",
            "label": "Notice Period"
        },
        {
            "type": "work_experience",
            "label": "Work Experience"
        },
        {
            "type": "rating",
            "label": "Rating"
        }
    ]
}
```
