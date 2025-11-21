import streamlit as st
from google import genai
import re

# Page Config
st.set_page_config(page_title="Exam Paper Answer Generator", page_icon="📝", layout="centered")

# Title
st.title("📝 15-Marks Student Answer Helper (Perfect Exam Paper Style)")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    show_diagram = st.checkbox("Show Diagram", value=True)
    st.markdown("---")
    st.markdown("This app writes answers in a real exam paper format with perfect lines.")

# Input topic
topic = st.text_input("Enter your exam topic:")

# Generate Button
if st.button("Generate 15-Marks Answer"):
    if not api_key:
        st.error("Please enter API Key!")
    elif not topic:
        st.error("Please enter a topic!")
    else:
        with st.spinner("Writing answer on exam sheet…"):
            try:
                # Diagram ON/OFF
                diagram_text = "Include a neat text-based diagram." if show_diagram else "Do NOT include any diagram."

                # Prompt
                prompt = f"""
Generate a perfect 15-marks university exam answer on: "{topic}".

Follow this structure exactly:
- Introduction (4–5 points)
- Definition (4–5 points)
- Diagram: {diagram_text}
- Six Key Points (heading + 2–3 lines explanation each)
- Features (4–5 points)
- Advantages (4–5 points)
- Characteristics (4–5 points)
- Applications
- Final conclusion

Important:
- DO NOT show section names in the answer.
- Headings must be in BLUE.
- Paragraph/content must be in BLACK.
- No stars (** or *) in the response.
- Produce a clean, topper-level exam answer.
"""

                # API Call
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )

                # Remove ALL star marks
                clean = response.text.replace("**", "").replace("*", "")
                clean = clean.replace("\n", "<br>")

                # PERFECT EXAM PAPER CSS (BEST VERSION)
                exam_css = """
                <style>
                .exam-paper {
                    background:
                        linear-gradient(white 38px, black 38px, black 40px, white 40px);
                    background-size: 100% 40px;
                    padding: 40px 60px;
                    border-left: 10px solid red;
                    height: 1250px;
                    font-size: 19px;
                    line-height: 2.05;
                    overflow-y: auto;
                    border-radius: 6px;
                    box-shadow: 0 0 10px #999;
                }
                .blue-head {
                    color: #0055ff;
                    font-weight: 800;
                    font-size: 20px;
                }
                .black-text {
                    color: black;
                }
                </style>
                """

                # Auto-color headings
                def colorize(text):
                    formatted = ""
                    for line in text.split("<br>"):
                        if len(line.strip()) == 0:
                            formatted += "<br>"
                            continue

                        # Auto-detect heading
                        if line.strip().endswith(":") or len(line.strip()) < 40:
                            formatted += f"<span class='blue-head'>{line}</span><br>"
                        else:
                            formatted += f"<span class='black-text'>{line}</span><br>"
                    return formatted

                final_html = exam_css + f"""
                <div class="exam-paper">
                    {colorize(clean)}
                </div>
                """

                st.markdown(final_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {str(e)}")
