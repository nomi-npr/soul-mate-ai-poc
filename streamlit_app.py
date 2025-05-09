import os
import streamlit as st
import openai
from datetime import datetime
from config import SYSTEM_MESSAGE, MODEL_NAME, TEMPERATURE, MAX_TOKENS, MAX_MEMORY_MESSAGES

# Get API key from environment variable
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    st.error("❌ OPENAI_API_KEY environment variable not found. Please set it in Streamlit Cloud settings.")
    st.stop()

# Set page config
st.set_page_config(
    page_title="AI Agent POC",
    page_icon="🤖",
    layout="centered"
)

# App title and description
st.title("AI Agent POC")
st.markdown("Chat with the AI - Using 4o mini LLM model")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "openai_api_key" not in st.session_state:
    st.session_state.openai_key = openai_api_key

# Sidebar for API key input
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    if api_key:
        st.session_state.openai_key = api_key
        openai.api_key = api_key
    
    # Add a reset button
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# System message is imported from config.py

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Chat with the AI..."):
    # Check if API key is provided
    if not st.session_state.openai_key:
        st.error("Please enter your OpenAI API key in the sidebar to continue.")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare conversation history for API call (last 15 messages)
    conversation_history = []
    
    # Always include system message first
    conversation_history.append({"role": "system", "content": SYSTEM_MESSAGE})
    
    # Add up to last 15 messages from chat history
    recent_messages = st.session_state.messages[-MAX_MEMORY_MESSAGES:] if len(st.session_state.messages) > MAX_MEMORY_MESSAGES else st.session_state.messages
    conversation_history.extend(recent_messages)
    
    # Display assistant thinking status
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Call the OpenAI API with configured model
            response = openai.chat.completions.create(
                model=MODEL_NAME,
                messages=conversation_history,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            assistant_response = response.choices[0].message.content
            
            # Update placeholder with actual response
            message_placeholder.markdown(assistant_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            message_placeholder.markdown(f"❌ {error_message}")

# Add footer
st.markdown("---")
st.markdown(f"© {datetime.now().year} AI Agent POC | Session will reset when you close or refresh the page")