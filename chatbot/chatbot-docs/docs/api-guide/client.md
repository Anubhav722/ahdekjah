# Client Endpoints

## Client Signup

```
POST /auth/signup/
```
### Permissions

Any user can become a Client

### Params

|name         | type          | description |
|------------ | ------------- | ------------|
|username     | string        | required    |
|password     | string        | required    |


### Example Request

```
POST /auth/signup/

{
	"username": "launchyard",
	"password": "launchyard"
}
```

### Example Response

```
{
    "chatbot-client-secret": "ZRqLvKCuHeeeprfn2WCkQZiglTAQ01vH0N0bQV5nambd2qftWUdhCQHce1ZT53Wv",
    "chatbot-client-key": "jDhC9AZ7ac4jkEUqPFwvTEdQhvlvRRUTy27ta91y"
}
```

## Access Client Data

```
GET /auth/signup/:client_id
```

### Example Request

```
GET /auth/signup/1
```

### Example Response

```
{
    "username": "launchyard",
    "email": "",
    "password": "launchyard"
}
```

## Update Client Details

```
PUT /auth/signup/:client_id/
```

### Params

| name       | type        | description|
|------------|-------------|------------|
| username   | string      | optional   |
| password   | string      | optional   |

### Example Request

```
PUT /auth/signup/1/
{
	"username": "launchyard-chatbot",
	"password": "password123"
}
```

### Example Response

```
{
    "username": "launchyard-chatbot",
    "email": "",
    "password": "password123"
}
```
