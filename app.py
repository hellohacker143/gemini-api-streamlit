import streamlit as st
from google import genai

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="15-Marks Multi-Topic Answer Generator",
    page_icon="📝",
    layout="centered"
)

# ---------------------------------------------------
# Title and Description
# ---------------------------------------------------
st.title("📝 Multi-Topic 15-Marks Answer Generator")
st.markdown("Enter multiple topics and get separate topper-quality answers for each.")

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
    st.markdown("### About")
    st.write("This app generates 15-marks answers for multiple topics individually.")
    st.markdown("[Get API Key](https://aistudio.google.com/apikey)")

# ---------------------------------------------------
# Exam Prompt Template
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
# Multi-Topic Text Box
# ---------------------------------------------------
topics_text = st.text_area(
    "Enter multiple topics (one per line):",
    placeholder="Example:\nRank of a Matrix\nGauss Elimination Method\nGauss-Seidel Method"
)

generate_btn = st.button("Generate Answers")

# ---------------------------------------------------
# Generate Answers
# ---------------------------------------------------
if generate_btn:
    if not api_key:
        st.error("⚠️ Please enter your Gemini API Key in the sidebar!")
    elif not topics_text.strip():
        st.error("⚠️ Please enter at least one topic!")
    else:
        topics = [t.strip() for t in topics_text.split("\n") if t.strip()]

        client = genai.Client(api_key=api_key)

        st.markdown("---")
        st.subheader("📘 Generated 15-Marks Answers")

        for i, topic in enumerate(topics, start=1):

            st.markdown(f"## 🎯 **Answer {i}: {topic}**")
            st.markdown("---")

            final_prompt = exam_prompt_template.replace("{TOPIC}", topic)

            with st.spinner(f"Generating answer for: {topic} ..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=final_prompt
                    )
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

            st.markdown("---")
