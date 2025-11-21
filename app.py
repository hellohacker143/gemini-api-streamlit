import streamlit as st
from google import genai
import re

# Page Config
st.set_page_config(page_title="Exam Paper Answer Generator", page_icon="📝", layout="centered")

# Title
st.title("📝 15-Marks Student Answer Helper (Exam Paper Style)")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("---")
    show_diagram = st.checkbox("Show Diagram", value=True)
    st.markdown("---")
    st.markdown("This app writes answers in real exam paper format.")

# Input topic
topic = st.text_input("Enter your exam topic:")

# Generate Button
if st.button("Generate 15-Marks Answer"):
    if not api_key:
        st.error("Please enter API Key!")
    elif not topic:
        st.error("Please enter a topic!")
    else:
        with st.spinner("Generating topper-style answer…"):
            try:
                # Prepare prompt
                diagram_text = "Include neat text-based diagram." if show_diagram else "Do NOT include any diagram."

                prompt = f"""
Generate a perfect 15-marks university exam answer on the topic: "{topic}" in topper-writing style.

Follow this structure:

1. Introduction (4–5 bullet points)
2. Definition (4–5 bullet points)
3. Neat Diagram (text-based) — {diagram_text}
4. 6 Key Points — each must have a heading + 2–3 line explanation
5. Features (4–5 bullet points)
6. Advantages (4–5 bullet points)
7. Characteristics (4–5 bullet points)
8. Applications / Real-world uses
9. Strong conclusion

Important:
- Do NOT display section names like "Introduction", "Definition", etc.
- Only output the content in that order.
- All headings must be small and clear.
- Headings must be in BLUE color.
- Content must be in BLACK color.
- Answer must be exam-oriented and clean.
- Do NOT mention line count or structure in output.
"""

                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )

                answer = response.text.replace("\n", "<br>")

                # ---------------- EXAM PAPER CSS ---------------- #
                exam_css = """
                <style>
                .exam-paper {
                    background: repeating-linear-gradient(
                        white,
                        white 38px,
                        #e8e8e8 40px
                    );
                    padding: 35px;
                    padding-left: 60px;
                    border-left: 8px solid red;
                    border-radius: 8px;
                    line-height: 1.8;
                    font-size: 18px;
                    box-shadow: 0 0 8px #bbb;
                    height: 1200px;
                    overflow-y: auto;
                }
                .blue-head { color: #0055ff; font-weight: 700; }
                .black-text { color: black; }
                </style>
                """

                # Auto detect headings = lines ending with ":" or bold-like text
                def colorize(text):
                    formatted = ""
                    for line in text.split("<br>"):
                        if len(line.strip()) < 2:
                            formatted += "<br>"
                            continue
                        # Detect heading by trailing ":" or short length or title-like
                        if line.strip().endswith(":") or len(line) < 35:
                            formatted += f"<span class='blue-head'>{line}</span><br>"
                        else:
                            formatted += f"<span class='black-text'>{line}</span><br>"
                    return formatted

                final_html = exam_css + f"""
                <div class="exam-paper">
                    {colorize(answer)}
                </div>
                """

                st.markdown(final_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {str(e)}")
