from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, TextStreamer
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import ChatGenerationChunk, GenerationChunk
import transformers
import torch

print(torch.cuda.is_available())
