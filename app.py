import streamlit as st
from google import genai
import re

# Page Config
st.set_page_config(page_title="Exam Paper Answer Generator", page_icon="📘", layout="centered")

# Title
st.title("📘 Real Exam Booklet – 15 Marks Answer Generator")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    show_diagram = st.checkbox("Show Diagram", value=True)
    st.markdown("---")
    st.markdown("Writes answers in REAL booklet format.")

# Input Topic
topic = st.text_input("Enter exam topic:")

# Generate Button
if st.button("Generate 15-Marks Answer"):
    if not api_key:
        st.error("Please enter API Key!")
    elif not topic:
        st.error("Enter a topic!")
    else:
        with st.spinner("Writing answer on real exam booklet…"):
            try:
                # Diagram ON/OFF
                diagram_text = "Include a neat text diagram." if show_diagram else "Do NOT include any diagram."

                # Prompt for AI
                prompt = f"""
Write a topper-level 15-marks university exam answer on "{topic}".

Follow this order strictly:
- Introduction (4–5 points)
- Definition (4–5 points)
- Diagram: {diagram_text}
- Six Key Points (heading + 2–3 lines explanation)
- Features
- Advantages
- Characteristics
- Applications
- Strong conclusion

Rules:
- ONLY the first heading should be BLUE.
- Remaining content must be BLACK.
- No ** or * anywhere.
- No section titles like Introduction/Definition shown.
- Write like a topper.
"""

                # API CALL
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )

                # -------- CLEAN RESPONSE -------- #
                clean = response.text.replace("**", "").replace("*", "")
                clean = clean.replace("\n", "<br>")

                # -------- BOOKLET CSS (PERFECT REAL LOOK) -------- #
                booklet_css = """
                <style>
                .booklet {
                    background: 
                        linear-gradient(white 38px, black 38px, black 40px, white 40px);
                    background-size: 100% 40px;
                    border-left: 10px solid red;
                    padding: 40px 60px;
                    margin: auto;
                    width: 85%;
                    height: 1300px;
                    border-radius: 10px;
                    box-shadow: 0 0 25px #888;
                    line-height: 2.05;
                    font-size: 19px;
                    overflow-y: auto;
                }
                .blue-head {
                    color: #0055ff;
                    font-weight: 900;
                    font-size: 22px;
                }
                .black-text {
                    color: black;
                }
                </style>
                """

                # -------- AUTO COLOR LOGIC -------- #
                applied_first_heading = False

                def colorize(text):
                    nonlocal applied_first_heading
                    output = ""

                    for line in text.split("<br>"):

                        if len(line.strip()) == 0:
                            output += "<br>"
                            continue

                        # FIRST heading (TOP) must be BLUE
                        if not applied_first_heading:
                            output += f"<span class='blue-head'>{line}</span><br>"
                            applied_first_heading = True
                            continue

                        # All remaining text BLACK
                        output += f"<span class='black-text'>{line}</span><br>"

                    return output

                final_html = booklet_css + f"""
                <div class="booklet">
                    {colorize(clean)}
                </div>
                """

                st.markdown(final_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {str(e)}")
