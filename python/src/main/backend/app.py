import logging
from typing import Dict

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import SQLRecordManager, index
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from models import Conversation, Message
from templates import prompt_template
from utils import create_messages, format_docs

CONNECTION_STRING = "postgresql+psycopg2://admin:admin@postgres:5432/vectordb"
COLLECTION_NAME = "vectordb"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
mem = {}


embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(model="gpt-3.5-turbo")
store = PGVector(
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
    embedding_function=embeddings,
)
retriever = store.as_retriever()
prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
system_message_prompt = SystemMessagePromptTemplate(prompt=prompt)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def prompt_llm(conversation: Conversation) -> Dict[str, str]:
    """
    This function interfaces with the OpenAI api and in particular
    GPT-3.5 Turbo.

    :param conversation: Pydantic model containing a list of Messages
    :return: A dictionary containing the role and content of the response
    """
    query = conversation.conversation[-1].content

    try:
        logger.info("Performing similarity lookup")
        docs = retriever.get_relevant_documents(query=query)
        if len(docs) > 0:
            logger.info("Found relevant document!")
            docs = docs[0].page_content


    except Exception as e:
        logger.error("Similarity lookup failed")
        docs=None

    prompt = system_message_prompt.format(context=docs)
    messages = [prompt] + create_messages(
        conversation=conversation.conversation
    )  # noqa

    try:
        logger.info("Requesting OpenAI API")
        result = llm(messages)
    except Exception as e:
        result = "An error ocurred. Please try again later."

    return {"reply": result.content}


@app.post("/api/prompt/{conversation_id}")
async def process_prompt(conversation_id: str, conversation: Conversation) -> Message:
    """
    This function handles the flow of the LLM proxy. It retrieves or
    instantiates a conversation given a user_id, forwards the conversation
    to the LLM requester

    :param conversation_id: Any string, would be good with a uuid
    :param conversation: Pydantic model containing a list of Messages
    :return: The latest message from the AI or an error message
    """
    logger.info(f"Retrieving conversation with ID {conversation_id}")
    existing_conversation = mem.get(conversation_id)

    if existing_conversation is None:
        logger.info("No existing conversation. Creating a new one")
        existing_conversation = {
            "conversation": [
                Message(**{"role": "system", "content": "You are a helpful assistant."})
            ]
        }
        existing_conversation = Conversation(**existing_conversation)

    existing_conversation.conversation.append(conversation.conversation[-1])

    logger.info(f"Forwarding existing conversation [{conversation_id}]")
    response = prompt_llm(existing_conversation)

    assistant_message = response["reply"]

    logger.info(f"Extending history for [{conversation_id}]")
    existing_conversation.conversation.append(
        Message(**{"role": "assistant", "content": assistant_message})
    )

    mem[conversation_id] = existing_conversation
    return existing_conversation.conversation[-1]


def load_and_index_docs():
    """
    This function loads the text in docs.txt into
    the pgvector database.

    :return:
    """
    loader = TextLoader("./docs.txt")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=150, chunk_overlap=20)
    docs = text_splitter.split_documents(documents)

    namespace = f"pgvector/{COLLECTION_NAME}"
    record_manager = SQLRecordManager(namespace, db_url=CONNECTION_STRING)

    record_manager.create_schema()

    index(
        docs,
        record_manager,
        store,
        cleanup=None,
        source_id_key="source",
    )


load_and_index_docs()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5566)
