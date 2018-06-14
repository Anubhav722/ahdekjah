# Initiate Chat

## Chat Initiation

```
POST /chat/initiate/
```

### Permissions
Endpoint accessed only by active users.
>NOTE: Headers must be specified with `chatbot-client-key` and `chatbot-client-secret`

```
{
	"chatbot-client-key": "t1IHgSsEw20LIC2qE2cHqkVfAJA1VvK7FY8FS0gI",
	"chatbot-client-secret": "h8T3Sd9UYG5uIdQwtbU7rPgGhgtsKwKNuugIsbYlTZwYyBoswctaMBzatmiEYuvG"
}
```


## Example Request

```
POST /chat/initiate/

{
    "tree_id": 1,
    "recipient_details": [{
        "recipient_phone": "+911111111111",
        "identifier": "dGVzdCtjYW5kaWRhdGUxQGFpcmN0by5jb20tNQ",
        "recipient_email": "test+candidate1@aircto.com"
    }, {
        "recipient_phone": "+918954394159",
        "identifier": "dGVzdCtjYW5kaWRhdGU3QGFpcmN0by5jb20tNQ",
        "recipient_email": "test+candidate7@aircto.com"
    }, {
        "recipient_phone": "+918105570331",
        "identifier": "dGVzdCtjYW5kaWRhdGU0QGFpcmN0by5jb20tNQ",
        "recipient_email": "test+candidate4@aircto.com"
    }]
}
```
>NOTE: Making this request triggers email and message to the params passed `recipient_email`, `recipient_phone` for the messenger chatbot link.

## Example Response

```
{
    "tree_id": 1,
    "session_details": [
        {
            "identifier": "dGVzdCtjYW5kaWRhdGUxQGFpcmN0by5jb20tNQ",
            "status": "link_Sent",
            "recipient_email": "test+candidate1@aircto.com",
            "id": 69
        },
        {
            "identifier": "dGVzdCtjYW5kaWRhdGU3QGFpcmN0by5jb20tNQ",
            "status": "link_Sent",
            "recipient_email": "test+candidate7@aircto.com",
            "id": 70
        },
        {
            "identifier": "dGVzdCtjYW5kaWRhdGU0QGFpcmN0by5jb20tNQ",
            "status": "link_Sent",
            "recipient_email": "test+candidate4@aircto.com",
            "id": 71
        }
    ]
}
```