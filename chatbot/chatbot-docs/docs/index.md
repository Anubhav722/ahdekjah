# Overview

## Authentication

Authentication is simple. If any endpoints require login just add `chatbot-client-key` and `chatbot-client-secret` in the header of each request as below
```
{
	"chatbot-client-key": "41e31930e450a0e6317e4a76481130fc83c6c73f",
	"chatbot-client-secret": "MXUNBs6iepGPT9o5nMAeyOcr5zIQWIdC07FZjjpcxnjGBW27Rf1ZvNbCH8DWc2xH"
}
```
>NOTE: You can get `client_key` and `client_secret` via `/auth/signup/` endpoint.

## Response Structure

Every response is contained by an envelope. That is, each response has a predictable set of keys with which you can expect to interact.

```
{
    "status": "Created",
    "detail": "Tree has been successfully created.",
    "tree_id": "1",
    "tree_name": "NAME OF THE TREE"
}
```