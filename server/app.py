import streamlit as st
from noah_llm import NoahLLM


st.title('MobileGPT')
llm = NoahLLM()

def generate_response(input_text, system_prompt=None):
    st.toast("Processing... Please wait...")
    msg_container = st.empty()
    system_message = "You''re are a helpful, talkative, and friendly assistant."
    user_message = input_text
    full_response = []
    for chunk in llm.stream(input_text, system_prompt=system_prompt):
        if chunk:
            if "\n" in chunk:
                chunk.replace("\n", "\n\n")
            full_response.append(chunk)
            result = "".join(full_response)
            msg_container.write(result)
    st.toast("Processing complete!")

with st.form('main_form'):
    text = st.text_area('Enter text', 'Ask anything you want!')
    submitted = st.form_submit_button('Submit')
    if submitted:
        generate_response(text)

