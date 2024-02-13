from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are world class technical documentation writer."),
    ("user", "{input}")
])

llm = Ollama(model="llama2")

output_parser = StrOutputParser()

chain = prompt | llm | output_parser

def print_stream_generator(chain, input_query):
    for sent in chain.stream({"input":input_query}):
        print(sent, end="", flush=True)
    else:
        print()

print_stream_generator(chain, "how can langsmith help with testing?")
