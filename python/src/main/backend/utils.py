from langchain.schema import AIMessage, HumanMessage, SystemMessage

ROLE_CLASS_MAP = {"assistant": AIMessage, "user": HumanMessage, "system": SystemMessage}


def create_messages(conversation):
    return [
        ROLE_CLASS_MAP[message.role](content=message.content)
        for message in conversation
    ]


def format_docs(docs):
    formatted_docs = []
    for doc in docs:
        formatted_doc = "Source: " + doc.metadata["source"]
        formatted_docs.append(formatted_doc)
    return "\n".join(formatted_docs)
