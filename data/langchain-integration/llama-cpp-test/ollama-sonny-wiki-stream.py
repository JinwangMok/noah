from langchain.chains import create_retrieval_chain
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.llms import Ollama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS 


def generate_chat_stream(chain, chat_history, user_input)->str:
    answer_content = ""
    for response in chain.stream({"chat_history":chat_history, "input":user_input}):
        if "answer" in response:
            print(response["answer"], end="", flush=True)
            answer_content += response["answer"]
    else:
        print("\n", "-"*50,"\n")

    return answer_content

if __name__ == "__main__":
    bot_name = "Sonny-Bot"
    loader = WebBaseLoader("https://en.wikipedia.org/wiki/Son_Heung-min")
    docs = loader.load()
    embeddings = OllamaEmbeddings()
    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(docs)
    print("Embedding Sonny's wiki docs...")
    vector = FAISS.from_documents(documents, embeddings)

    llm = Ollama(model="llama2")

    retriever = vector.as_retriever()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user's questions based on the below context:\n\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])

    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    chat_history = []
    print(f"===== Welcome! This is {bot_name}. =====")
    print("-"*50)
    print(f"[{bot_name}]: Hi, there! Please ask me anything about Sonny! If you want to exit, please enter 'exit'.")
    
    running = True
    while running:
        user_input = input("[You]: ")
        if user_input == "exit":
            break
        print("\n[{bot_name}] :", end="")
        answer_content = generate_chat_stream(retrieval_chain, chat_history, user_input)
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=answer_content))

