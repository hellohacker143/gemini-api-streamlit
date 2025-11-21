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
st.markdown("Use Google Gemini for normal chatting or generate topper-level exam answers.")

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
    st.markdown("This is a multi-feature Gemini AI app.")
    st.markdown("[Get API Key](https://aistudio.google.com/apikey)")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# 1️⃣ NORMAL CHATBOT MODE
# -----------------------------
if mode == "💬 Chatbot":

    # Show chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat typing input
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



# -----------------------------
# 2️⃣ STUDENT ANSWER HELPER MODE
# -----------------------------
else:
    st.subheader("📝 Generate 15-Marks University Answer")

    topic = st.text_input("Enter your exam topic:")

    if st.button("Generate 15-Marks Answer"):
        if not api_key:
            st.error("Please enter your API key!")
        elif not topic:
            st.error("Please enter a topic!")
        else:
            with st.spinner("Generating topper-level answer..."):
                try:
                    client = genai.Client(api_key=api_key)

                    prompt = f"""
Generate a perfect, topper-style 15-marks university exam answer on:
“{topic}”

Strict structure:
1. Introduction (4–5 bullet points)
2. Definition (4–5 bullet points)
3. Neat Text-Based Diagram
4. Six Key Points (each 2–3 lines)
5. Features (4–5 points)
6. Advantages (4–5 points)
7. Characteristics (4–5 points)
8. Applications / Real-world uses
9. Strong conclusion

Write in clean exam style. Do NOT mention number of lines.
Color format:
- Headings → **BLACK**
- Paragraphs → **BLUE**
"""

                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt
                    )

                    answer = response.text

                    # Color formatting (exam style)
                    answer = answer.replace("**", "")  # remove markdown bold
                    formatted = answer.replace("\n", "<br>")
                    formatted = formatted.replace(":", "</span><br><span style='color:blue;'>")

                    # Heading styling
                    for h in ["Introduction", "Definition", "Neat Diagram", "Key Points", 
                              "Features", "Advantages", "Characteristics", "Applications", 
                              "Conclusion"]:
                        formatted = formatted.replace(
                            h, f"<span style='color:black; font-weight:700; font-size:22px;'>{h}</span>"
                        )

                    st.markdown("<span style='color:blue; font-size:18px;'>" + formatted + "</span>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error: {str(e)}")
