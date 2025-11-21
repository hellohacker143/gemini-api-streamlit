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
    api_key = st.text_input("Enter Gemini API Key", type="password")
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
# 2️⃣ EXAM PAPER MODE — FULL EXAM SHEET + BLACK HEADINGS
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
- DO NOT include section headings.
- Write smooth continuous exam-style content.
- Use natural internal headings (not section labels).
- Convert headings to BLACK.
- Body text must be BLUE.
- Include a simple diagram.
- Answer should look handwritten on an exam sheet.
"""

                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt
                    )

                    text = response.text.replace("\n", "<br>")

                    # ---------------- CSS for FULL EXAM SHEET + HEADING COLORS ---------------- #
                    exam_css = """
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
                    .heading-black {
                        color: black;
                        font-weight: 900;
                        font-size: 20px;
                    }
                    </style>
                    """

                    # ---------------- AUTO-DETECT HEADINGS ---------------- #
                    # Any line ending with ":" becomes a black heading
                    import re
                    def make_headings_black(html):
                        return re.sub(
                            r"(.*?):<br>",
                            r"<span class='heading-black'>\1</span>:<br>",
                            html
                        )

                    text = make_headings_black(text)

                    # Wrap all non-headings in blue
                    final_html = exam_css + f"""
                    <div class="exam-paper">
                        <span class="blue-text">{text}</span>
                    </div>
                    """

                    st.markdown(final_html, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error: {str(e)}")
