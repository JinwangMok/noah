from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp

template = """Question: {question}

Answer: Let's work this out in a step by step way to be wure we have the right answer."""

prompt = PromptTemplate(template=template, input_variables=["question"])

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

llm = LlamaCpp(
        model_path="../llms/Mistral-7B-Instruct-v0.1-GGUF/mistral-7b-instruct-v0.1.Q4_0.gguf",
        n_gpu_layers = -1,
        n_batch=512,
        temperature=0.75,
        max_tokens=2000,
        top_p=1,
        callback_manager=callback_manager,
        verbose=True,
)

llm_chain = LLMChain(prompt=prompt, llm=llm)

question = "What NFL team won the Super Bowl in the year Justin Biber was born?"
llm_chain.run(question)
