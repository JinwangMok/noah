# pip install beautifulsoup4

from langchain_community.llms import Ollama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS # Facebook AI Similarity Search
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain

loader = WebBaseLoader("https://docs.smith.langchain.com/overview")

docs = loader.load()

embeddings = OllamaEmbeddings()

text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings) # Now we have retrieval vector documents!

# Retrieval Chain
prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")

llm = Ollama(model="llama2")

document_chain = create_stuff_documents_chain(llm, prompt)

## We can directly passing the documents to our chain like,
# from langchain_core.documents import Document
# document_chain.invoke({
#     "input": "how can langsmith help with testing?",
#     "context": [Document(page_content="langsmith can let you visualize test results")]
#
## However, in this case, we use relative document instead. So, like,

retriever = vector.as_retriever()
retrieval_chain = create_retrieval_chain(retriever, document_chain)

def print_stream_generator(chain, input_query):
    for i, sent in enumerate(chain.stream({"input":input_query})):
        # There are 3 keys are in sent. 'input', 'context', and 'answer'.
        # A value of 'input' is input prompt from user.
        # A value of 'context' is retrieval document vector in this case.
        # A values of 'answer' are actual streamed text of LLM.
        # Therefore...
        if 'answer' in sent:
            print(sent['answer'], end="", flush=True) # Warning: flush=True cause inefficiency.
    else:
        print("\n")

print_stream_generator(retrieval_chain, "how can langsmith help with testing?")
