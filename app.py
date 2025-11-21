import streamlit as st
from google import genai
import re
from fpdf import FPDF
import base64

# -----------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------
st.set_page_config(page_title="15-Marks Answer Generator", page_icon="📝", layout="centered")
st.title("📝 15-Marks Student Answer Helper")

# -----------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    api_key = st.text_input("Enter Gemini API Key", type="password")

    show_diagram = st.checkbox("Include Diagram", value=True)
    show_lines = st.checkbox("Show Ruled Lines", value=True)

    answer_length = st.selectbox(
        "Answer Depth",
        ["Short (200 words)", "Medium (300–350 words)", "Long (450+ words)"]
    )

    font_choice = st.selectbox(
        "Font Style",
        ["Normal", "Handwritten", "Exam Sheet"]
    )

    margin = st.slider("Page Side Margin", 20, 120, 60)

    st.markdown("---")
    st.markdown("Writes answers in topper-style exam paper format.")

# -----------------------------------------------------
# TOPIC INPUT
# -----------------------------------------------------
topic = st.text_input("Enter your exam topic:")

# -----------------------------------------------------
# HELPER: PDF EXPORT
# -----------------------------------------------------
def export_pdf(html):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = re.sub('<[^<]+?>', '', html)  # Remove HTML
    pdf.multi_cell(0, 10, clean_text)
    file_path = "/mnt/data/exam_answer.pdf"
    pdf.output(file_path)
    return file_path

# -----------------------------------------------------
# GENERATE ANSWER
# -----------------------------------------------------
if st.button("Generate 15-Marks Answer"):
    if not api_key:
        st.error("Enter API Key!")
    elif not topic:
        st.error("Enter a topic!")
    else:
        with st.spinner("Writing answer…"):
            try:
                diagram_text = (
                    "Include a neat text-based diagram."
                    if show_diagram else
                    "Do NOT include any diagram."
                )

                # Writing depth
                prompt = f"""
Generate a perfect 15-marks university exam answer on: "{topic}".

Follow this EXACT structure:
- Introduction (4–5 points)
- Definition (4–5 points)
- Diagram: {diagram_text}
- Six Key Points (heading + 2–3 lines each)
- Features (4–5 points)
- Advantages (4–5 points)
- Characteristics (4–5 points)
- Applications
- Final Conclusion

Important:
- DO NOT show section names in the response.
- Headings must be BLUE.
- Paragraphs must be BLACK.
- No symbols like * or **.
- Produce a PERFECT topper-level exam paper answer.
Write depth: {answer_length}.
"""

                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )

                # Clean unwanted marks
                clean = response.text.replace("**", "").replace("*", "")
                clean = clean.replace("\n", "<br>")

                # ---------------------------------------------
                # Extra Enhancements
                # ---------------------------------------------
                # Auto Highlight
                keywords = ["Important", "Key Point", "Therefore", "Hence", "Conclusion"]
                for word in keywords:
                    clean = clean.replace(word, f"<mark>{word}</mark>")

                # Auto Numbering
                lines = clean.split("<br>")
                numbered = []
                i = 1
                for line in lines:
                    if len(line.strip()) > 0 and ":" not in line:
                        numbered.append(f"{i}. {line}")
                        i += 1
                    else:
                        numbered.append(line)
                clean = "<br>".join(numbered)

                # ---------------------------------------------
                # CSS BUILDER
                # ---------------------------------------------
                # Ruled lines ON/OFF
                if show_lines:
                    background_css = """
                        background:
                            linear-gradient(white 38px, black 38px, black 40px, white 40px);
                        background-size: 100% 40px;
                    """
                else:
                    background_css = "background: white;"

                # Font styles
                if font_choice == "Handwritten":
                    font_css = "font-family: 'Comic Sans MS';"
                elif font_choice == "Exam Sheet":
                    font_css = "font-family: 'Times New Roman';"
                else:
                    font_css = "font-family: Arial;"

                # ---------------------------------------------
                # COLORIZE HEADINGS
                # ---------------------------------------------
                def colorize(text):
                    formatted = ""
                    for line in text.split("<br>"):
                        if len(line.strip()) == 0:
                            formatted += "<br>"
                            continue

                        if line.strip().endswith(":") or len(line.strip()) < 40:
                            formatted += f"<span class='blue-head'>{line}</span><br>"
                        else:
                            formatted += f"<span class='black-text'>{line}</span><br>"
                    return formatted

                styled = colorize(clean)

                # Final CSS + HTML
                exam_css = f"""
                <style>
                .exam-paper {{
                    {background_css}
                    padding: 40px {margin}px;
                    border-left: 10px solid red;
                    height: 1250px;
                    font-size: 19px;
                    line-height: 2.05;
                    overflow-y: auto;
                    border-radius: 6px;
                    box-shadow: 0 0 10px #999;
                    {font_css}
                }}
                .blue-head {{
                    color: #0055ff;
                    font-weight: 800;
                    font-size: 20px;
                }}
                .black-text {{
                    color: black;
                }}
                </style>
                """

                final_html = exam_css + f"""
                <div class="exam-paper">
                    {styled}
                </div>
                """

                st.markdown(final_html, unsafe_allow_html=True)

                # ---------------------------------------------
                # Download Buttons
                # ---------------------------------------------
                pdf_path = export_pdf(final_html)
                with open(pdf_path, "rb") as f:
                    st.download_button("📄 Download PDF", f, file_name="exam_answer.pdf")

                st.download_button(
                    "📜 Download TXT",
                    clean,
                    file_name="exam_answer.txt"
                )

                if st.button("🔄 Regenerate Answer"):
                    st.experimental_rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")
