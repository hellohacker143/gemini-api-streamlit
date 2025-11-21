import streamlit as st
from google import genai
import os

# Page configuration
st.set_page_config(
    page_title="Gemini API Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Title and description
st.title("🤖 Gemini API Q&A Chatbot")
st.markdown("Ask me anything! Powered by Google's Gemini AI")

# API Key input in sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Enter your Gemini API Key", 
        type="password",
        help="Get your API key from https://aistudio.google.com/apikey"
    )
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This is a simple Q&A chatbot using Google's Gemini API.")
    st.markdown("[Get API Key](https://aistudio.google.com/apikey)")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar!")
    else:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Initialize Gemini client
                    client = genai.Client(api_key=api_key)
                    
                    # Generate response
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt
                    )
                    
                    # Display response
                    assistant_response = response.text
                    st.markdown(assistant_response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": assistant_response}
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Make sure your API key is valid and you have internet connection.")

# Clear chat button
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()
