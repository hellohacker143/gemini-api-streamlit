import streamlit as st
from google import genai
import os

# Page configuration
st.set_page_config(
    page_title="Gemini Exam Paper Answer Helper",
    page_icon="📝",
    layout="centered"
)

# Title
st.title("📝 15-Marks Student Answer Helper + 🤖 Gemini Chatbot")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Enter Gemini API Key",
        type="password"
    )

    st.markdown("---")
    mode = st.radio("Choose Mode", ["💬 Chatbot", "📝 Student Answer Helper"])
    st.markdown("---")
    st.markdown("This app uses Google Gemini API.")


# Init chat
if "messages" not in st.session_state:
    st.session_state.messages = []


# ----------------------------------------------------
# 1️⃣ NORMAL CHATBOT
# ----------------------------------------------------
if mode == "💬 Chatbot":

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask anything…"):
        if not api_key:
            st.error("Enter API key!")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
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
# 2️⃣ EXAM PAPER MODE (FULL EXAM BACKGROUND)
# ----------------------------------------------------
else:
    st.subheader("📝 Generate 15-Marks Exam Answer (FULL Exam Paper Background)")

    topic = st.text_input("Enter your exam topic:")

    if st.button("Generate Answer"):
        if not api_key:
            st.error("Enter API key!")
        elif not topic:
            st.error("Enter a topic!")
        else:
            with st.spinner("Writing answer on exam sheet…"):
                try:
                    client = genai.Client(api_key=api_key)

                    prompt = f"""
Write a topper-level 15-marks answer on:
{topic}

Rules:
- Do NOT write section headings.
- Smooth continuous answer.
- Include a simple text diagram.
- Use black mini-headings and blue body text.
- Format like a real handwritten exam paper.
"""

                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt
                    )

                    raw = response.text
                    html_text = raw.replace("\n", "<br>")

                    # -------------- FULL EXAM SHEET BACKGROUND CSS ---------------- #
                    exam_paper_css = """
                    <style>
                    .exam-paper {
                        background: repeating-linear-gradient(
                            white,
                            white 38px,
                            #c2d3ff 40px
                        );
                        background-size: 100% 40px;
                        border-left: 6px solid #4aa3ff;
                        padding: 35px;
                        padding-left: 50px;
                        font-size: 18px;
                        line-height: 1.8;
                        border-radius: 10px;
                        box-shadow: 0 0 6px #999;
                    }
                    .blue-text { color: #0055ff; }
                    .black-head { color: black; font-weight: 700; }
                    </style>
                    """

                    # Convert simple "**Heading**" to black headings
                    html_text = html_text.replace("**", "")
                    html_text = html_text.replace(":", ":</span><span class='blue-text'>")

                    final_html = f"""
                    {exam_paper_css}
                    <div class="exam-paper">
                        <span class="blue-text">{html_text}</span>
                    </div>
                    """

                    st.markdown(final_html, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error: {str(e)}")
