from langchain_openai import ChatOpenAI

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnablePassthrough
from langchain.callbacks.base import BaseCallbackHandler

from utils.chatbot.embedding.pdf_embedding import Embedder


class ChatCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.message = ""
        # self.num_of_tokens = 0
        super().__init__()

    def on_llm_start(self, *args, **kargs):
        self.num_of_tokens = 0

    def on_llm_end(self, *args, **kargs):
        # save_message(self.message, "ai")
        pass

    def on_llm_new_token(self, token, *args, **kargs):
        pass
        # self.num_of_tokens += 1
        # self.message += token
        # self.message_box.markdown(self.message)


class Chatbot:
    def __init__(self, conversation, file_path, embed_path):
        self.conversation = conversation
        self.file_path = file_path
        self.embed_path = embed_path
        self.llm_model = ChatOpenAI(
            temperature=0.1,
            model="gpt-4o",
            # streaming=True,
            # callbacks=[ChatCallbackHandler()],
        )

        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
        )
        self.template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are a helpful assistant for a user who is reading a PDF document. The user has asked you to help them understand the content of the document. 

I will summarize the conversation between you and me and deliver it as 'Context'. Please answer based on the PDF document and this `Context`.

If you can't answer a question, you should let the user know that you are unable to provide an answer.
Don't worry about providing a perfect answer. Just do your best to help the user understand the content of the document.

`Context`: {context}
        """,
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )

    def chat(self, message):
        embedder = Embedder()
        retriever = embedder.load(self.embed_path, self.file_path)

        # docs = retriever.get_relevant_documents(message)
        docs = retriever.invoke(message)
        context = "\n\n".join(document.page_content for document in docs)

        chain = RunnablePassthrough() | self.llm_model

        chat_history = self.memory.load_memory_variables({})["chat_history"]

        formatted_prompt = self.template.format(
            chat_history=chat_history, context=context, question=message
        )
        result = chain.invoke(formatted_prompt).content.replace("$", "\$")

        self.memory.save_context({"input": message}, {"output": result})
        return result
