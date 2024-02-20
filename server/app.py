from datetime import datetime
import streamlit as st
from noah_llm import NoahLLM

# Global Variables
llm = NoahLLM()
chat_history = {} 
system_prompt_list = []
last_system_prompt = "You are an AI assistant. Please answer to my question with step-by-step manner." # By default

def get_timestamp():
    return f"[{datetime.now().strftime('%y.%m.%d %H:%M')}]"

def response_generator(input_text, system_prompt=None):
    system_message = "You''re are a helpful, talkative, and friendly assistant."
    user_message = input_text
    for chunk in llm.stream(input_text, system_prompt=system_prompt):
        if chunk:
            if "\n" in chunk:
                chunk.replace("\n", "\n\n") # For a readability.
            yield chunk

# Sidebar:chat history
chat_history_box = st.sidebar.container(height=400)
chat_history_box.header("Chat History", divider="gray")
# TBD

# Sidebar:system prompt
system_prompts_box_wrapper = st.sidebar.container(height=400)
system_prompts_box_wrapper.header("System Prompts", divider="gray")
system_prompts_box = system_prompts_box_wrapper.container(height=250)
system_prompt = system_prompts_box_wrapper.chat_input("Custom your chatbot!") 
if system_prompt:
    chatbot_spec = system_prompts_box.expander(f"{get_timestamp()} {system_prompt[:10]}...")
    chatbot_spec.write(system_prompt)
    last_system_prompt = system_prompt

# Main plain
st.title('Mobile:red[G]:gray[PT]')
st.info(f"[🤖System Prompt]\n\n{last_system_prompt}")
"---"
chat_result_box = st.container()
main_plain_place_holder = chat_result_box.markdown(
    "<h1 style='text-align: center; color: black;'></br></br></br>Welcome!👋🏻</br>May I help you?</h1>",
    unsafe_allow_html=True
)
chat_prompt = st.chat_input("Hello, MobileGPT!")
if chat_prompt:
    main_plain_place_holder.empty()
    chat_result_box.chat_message("user").write(f"You: {chat_prompt}")
    chat_result_box.chat_message("assistant").write_stream(
        response_generator(
            chat_prompt,
            system_prompt=(None if system_prompt is None else system_prompt)
        )
    )
    # Add to chat history
