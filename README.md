# OpenAI Chatbot Proxy POC

---

## Introduction

This is a basic system serving as a proof-of-concept for an implementation of a proxy to a large language model. This system is designed to interface with the GPT 3.5 Turbo model from OpenAI, but it can be configured to interface with anything supported by langchain.  

## Overview

This system relies upon LangChain as an abstraction layer to interfacing with an LLM. The choice of using this approach is primarily to avoid tailoring to a specific model provider API, such that the underlying model could relatively easily be replaced. Although there would not be any difference in practise here as only one model is considered, it would be a nice feature to have for a production application nonetheless. 

The backend application interfacing with the LLM is a FastAPI app. While for the POC only one user will be utilising the app at any given time, it is probably the best choice in a scenario where we would like asynchronous exection of the various interactions in this system.


## Setup and usage

This system runs as individual microservices. To test it out clone this repository. Make sure to set the `OPENAI_API_KEY` environment variable and then run:

`docker compose up`

Will spin up a postgres database necessary for RAG functionality and the backend microservice.

You can then send POST requests to the service at:

`localhost:5566:api/prompt/{conversation_id}`

Where `conversation_id` can be anything. The request body should look like:

```
{
    "conversation": [
        {
            "role": "user",
            "content": "Hi there, what's the most awesome toy company in the world?"
        }
    ]
}

```
