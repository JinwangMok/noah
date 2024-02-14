from langchain_community.llms import Ollama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS # Facebook AI Similarity Search
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

loader = WebBaseLoader("https://docs.smith.langchain.com/overview")
docs = loader.load()
embeddings = OllamaEmbeddings()
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings) # Now we have retrieval vector documents!

llm = Ollama(model="llama2")

retriever = vector.as_retriever()

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the user's questions based on the below context:\n\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}")
])

document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

chat_history = [HumanMessage(content="Can LangSmith help test my LLM application?"), AIMessage(content="Yes!")]

def print_stream_generator(chain, chat_history, input_query):
    for sent in chain.stream({"chat_history":chat_history, "input":input_query}):
        if 'answer' in sent:
            print(sent['answer'], end="", flush=True) 
    else:
        print("\n")

print_stream_generator(retrieval_chain, chat_history, "Tell me how")
