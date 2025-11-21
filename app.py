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
st.title("🤖 Gemini API Chatbot + 📝 Student Answer Helper")
st.markdown("Use Google Gemini for chatting or generating topper-level exam answers.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Enter your Gemini API Key",
        type="password",
        help="Get your API key from https://aistudio.google.com/apikey"
    )

    st.markdown("---")
    mode = st.radio("Choose Mode", ["💬 Chatbot", "📝 15-Marks Student Answer Helper"])
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This app uses Google Gemini API.")
    st.markdown("[Get API Key](https://aistudio.google.com/apikey)")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# ----------------------------------------------------
# 1️⃣ NORMAL CHATBOT MODE
# ----------------------------------------------------
if mode == "💬 Chatbot":

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask anything..."):
        if not api_key:
            st.error("Please enter your API key!")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        response = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=prompt
                        )
                        output = response.text
                        st.markdown(output)

                        st.session_state.messages.append(
                            {"role": "assistant", "content": output}
                        )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# ----------------------------------------------------
# 2️⃣ STUDENT ANSWER HELPER MODE
# ----------------------------------------------------
else:
    st.subheader("📝 15-Marks University Answer (White Paper Style)")

    topic = st.text_input("Enter your exam topic:")

    if st.button("Generate 15-Marks Answer"):
        if not api_key:
            st.error("Please enter your API key!")
        elif not topic:
            st.error("Please enter a topic!")
        else:
            with st.spinner("Writing topper-style answer..."):
                try:
                    client = genai.Client(api_key=api_key)

                    prompt = f"""
Generate a topper-level 15-marks university exam answer on the topic:
“{topic}”

Important rules:
- DO NOT include section titles like "Introduction", "Definition", "Key Points", etc.
- Write a smooth flowing exam answer.
- Use small black-color mini headings where necessary.
- Use blue color for body text.
- Include a simple text diagram inside the answer.
- Maintain clarity, depth, neatness.
- Make it look like text written on a clean white exam sheet.
"""

                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt
                    )

                    answer = response.text

                    # Convert text to HTML formatting
                    formatted = answer.replace("\n", "<br>")

                    # Create a white paper container
                    st.markdown("""
                    <div style='background-color:white; padding:25px; border-radius:10px;
                                border:1px solid #ddd; box-shadow:0px 0px 6px #ccc;
                                width:100%;'>
                    """, unsafe_allow_html=True)

                    # Convert bold-looking headings
                    formatted = formatted.replace("**", "")
                    formatted = formatted.replace(":", ":</span><span style='color:blue;'>")

                    # Final rendering
                    st.markdown(
                        f"<span style='color:blue; font-size:18px; line-height:1.6;'>{formatted}</span>",
                        unsafe_allow_html=True
                    )

                    st.markdown("</div>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error: {str(e)}")
