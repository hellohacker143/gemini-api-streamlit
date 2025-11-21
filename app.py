import streamlit as st
from google import genai

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="15-Marks Exam Answer Generator",
    page_icon="📝",
    layout="centered"
)

# ---------------------------------------------------
# Title Section
# ---------------------------------------------------
st.title("📝 15-Marks Exam Answer Generator Chatbot")
st.markdown("Generate topper-quality university exam answers using Google's Gemini AI.")

# ---------------------------------------------------
# Sidebar – API Key
# ---------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Enter Gemini API Key",
        type="password",
        help="Get your API key from https://aistudio.google.com/apikey"
    )
    st.markdown("---")
    st.markdown("### About This App")
    st.write("This chatbot generates structured 15-marks exam answers with neat diagrams and headings.")
    st.markdown("[Get Gemini API Key](https://aistudio.google.com/apikey)")

# ---------------------------------------------------
# Initialize Chat History
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------
# 15-Marks Exam Prompt Template
# ---------------------------------------------------
exam_prompt_template = """
Generate a perfect 15-marks university exam answer on the topic: “{TOPIC}” in topper-writing style.
Follow this exact structure:

Introduction – (4–5 bullet points)
Definition – (4–5 bullet points)
Neat Diagram – (text-based block diagram)
6 Key Points – (Each with heading + 2–3 line explanation)
Features – (4–5 bullet points)
Advantages – (4–5 bullet points)
Characteristics – (4–5 bullet points)
Applications / Real-world uses
Strong conclusion

Make the answer clean, structured, exam-oriented, and easy to score full marks.
Do NOT mention how many lines the sections should have.
Generate the answer directly.
"""

# ---------------------------------------------------
# User Input (Chat Box)
# ---------------------------------------------------
if topic := st.chat_input("Enter your topic for the 15-marks answer..."):
    if not api_key:
        st.error("⚠️ Please enter your Gemini API key in the sidebar first!")
    else:

        # Insert topic into the exam template
        final_prompt = exam_prompt_template.replace("{TOPIC}", topic)

        # Add user message to session
        st.session_state.messages.append({"role": "user", "content": topic})
        with st.chat_message("user"):
            st.markdown(topic)

        # AI Response
        with st.chat_message("assistant"):
            with st.spinner("Generating topper-style answer..."):
                try:
                    # Initialize Gemini Client
                    client = genai.Client(api_key=api_key)

                    # Generate Response
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=final_prompt
                    )

                    # Display AI Output
                    bot_reply = response.text
                    st.markdown(bot_reply)

                    # Save to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": bot_reply}
                    )

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Check your API key and internet connection.")

# ---------------------------------------------------
# Clear Chat Button
# ---------------------------------------------------
with st.sidebar:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
