# filter-session.md

## Filter Session

REQUEST URL: http://yoda.local:8000/chat/filter/?<query-params>

### Example Request
``` 
GET http://yoda.local:8000/chat/filter/?tree_id=1&ctc_min=3&ctc_max=15&exp_min=5&exp_max=30&notice_period=20&loc=bangalore,lucknow,pune
```

### Example Response

```
[
    {
        "id": 26,
        "status": "completed",
        "recipient_email": "suraj@launchyard.com",
        "tree": 1
    },
    {
        "id": 25,
        "status": "completed",
        "recipient_email": "anubhav@launchyard.com",
        "tree": 1
    }
]
```



## Filter Tags

```
GET /chat/filter/tags/

[
    {
        "options": [
            {
                "title": "15 days",
                "notice_period": 15
            },
            {
                "title": "30 days",
                "notice_period": 30
            },
            {
                "title": "45 days",
                "notice_period": 45
            },
            {
                "title": "60 days",
                "notice_period": 60
            },
            {
                "title": "60+ days",
                "notice_period": "60+"
            }
        ],
        "label": "Notice Period",
        "single_params": true,
        "question_type": "single_choice"
    },
    {
        "options": [
            {
                "title": "0-3 lpa",
                "cur_ctc_min": 0,
                "cur_ctc_max": 3
            },
            {
                "title": "3-6 lpa",
                "cur_ctc_min": 3,
                "cur_ctc_max": 6
            },
            {
                "title": "6-12 lpa",
                "cur_ctc_min": 6,
                "cur_ctc_max": 12
            },
            {
                "title": "12-20 lpa",
                "cur_ctc_min": 12,
                "cur_ctc_max": 20
            },
            {
                "title": "20+ lpa",
                "cur_ctc_min": 20
            }
        ],
        "label": "Current Annual CTC (in lakhs)",
        "double_params": true,
        "question_type": "single_choice"
    },
    {
        "options": [
            {
                "title": "0-3 lpa",
                "exp_ctc_max": 3,
                "exp_ctc_min": 0
            },
            {
                "title": "3-6 lpa",
                "exp_ctc_max": 6,
                "exp_ctc_min": 3
            },
            {
                "title": "6-12 lpa",
                "exp_ctc_max": 12,
                "exp_ctc_min": 6
            },
            {
                "title": "12-20 lpa",
                "exp_ctc_max": 20,
                "exp_ctc_min": 12
            },
            {
                "title": "20+ lpa",
                "exp_ctc_min": 20
            }
        ],
        "label": "Expected Annual CTC (in lakhs)",
        "double_params": true,
        "question_type": "single_choice"
    },
    {
        "options": [
            {
                "exp_max": 1,
                "title": "0-1 yr",
                "exp_min": 0
            },
            {
                "exp_max": 3,
                "title": "1-3 yrs",
                "exp_min": 1
            },
            {
                "exp_max": 6,
                "title": "3-6 yrs",
                "exp_min": 3
            },
            {
                "exp_max": 12,
                "title": "6-12 yrs",
                "exp_min": 6
            },
            {
                "title": "12+ yrs",
                "exp_min": 12
            }
        ],
        "label": "Total year of experience (in years)",
        "double_params": true,
        "question_type": "single_choice"
    },
    {
        "options": [
            {
                "loc": "bangalore",
                "title": "Bangalore"
            },
            {
                "loc": "pune",
                "title": "Pune"
            },
            {
                "loc": "hyderabad",
                "title": "Hyderabad"
            },
            {
                "loc": "chennai",
                "title": "Chennai"
            }
        ],
        "label": "Current Location",
        "single_params": true,
        "question_type": "multiple_choice"
    }
]
```