from langchain_openai import ChatOpenAI

# import getpass
# import os
# if not os.environ.get("OPENAI_API_KEY"):
#     os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")


# from langchain_core.messages import HumanMessage, SystemMessage
# messages = [
#     SystemMessage("Translate the following from English into Italian"),
#     HumanMessage("hi!"),
# ]


class SimpleChat:
    def __init__(self, model):
        if not model:
            model = ChatOpenAI(model="gpt-4o-mini")
        self.model = model

    def chat(self, messages):
        return self.model.invoke(messages)
