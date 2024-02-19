from typing import Any, List, Mapping, Optional
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
import streamlit as st

class NoahLLM(LLM):
    n: int

    @property
    def _llm_type(self)->str:
        return "Noah"

    def _call(
        self,
        prompt:str,
        stop:Optional[List[str]]=None,
        run_manager:Optional[CallbackManagerForLLMRun]=None,
        **kwargs:Any,
    )->str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted")
        return prompt[:self.n]

    @property
    def _identifying_params(self)->Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"n":self.n}


st.title('MobileGPT')

def generate_response(input_text):
    llm = NoahLLM(n=10)
    st.info(llm.invoke(input_text)) # 향후 스트림으로 재구현 필요

with st.form('main_form'):
    text = st.text_area('Enter text', 'Ask anything you want!')
    submitted = st.form_submit_button('Submit')
    if submitted:
        generate_response(text)
