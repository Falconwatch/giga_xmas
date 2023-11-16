from langchain.chat_models import GigaChat
from langchain.chains import RetrievalQA, LLMChain
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate, PromptTemplate


class Giga:
    def __init__(self, prompt_template, sys_message):
        self._llm = GigaChat(temperature=1, verify_ssl_certs=False, scope='GIGACHAT_API_CORP')
        self._prompt_template = prompt_template
        self._sys_message = sys_message

    def call(self, user_message):
        chat_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=self._sys_message
                ),
                HumanMessagePromptTemplate.from_template(self._prompt_template),
            ]
        )
        response = self._llm(chat_template.format_messages(message=user_message)).content
        return response

