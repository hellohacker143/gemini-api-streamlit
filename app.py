import streamlit as st
from google import genai


# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------
st.set_page_config(
    page_title="Grouped 15-Marks Answer Generator",
    page_icon="📝",
    layout="centered"
)

# ---------------------------------------------------
# MAIN TITLE
# ---------------------------------------------------
st.title("📝 Grouped 15-Marks Answer Generator")
st.markdown("""
Generate **topper-quality**, fully structured **15-mark university exam answers**  
for multiple groups & topics — clean, neat, and exam-ready.
""")


# ---------------------------------------------------
# EXAMPLE FORMAT BOX
# ---------------------------------------------------
st.markdown("""
### 📌 Example Input Format 
""")


# ---------------------------------------------------
# SIDEBAR (API KEY)
# ---------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Enter Gemini API Key",
        type="password",
        help="Get your API Key → https://aistudio.google.com/apikey"
    )

    st.markdown("---")
    st.write("🔹 Generates **structured 15-mark answers**.")
    st.write("🔹 Supports **multiple groups & multiple topics**.")
    st.write("🔹 Powered by **Google Gemini 2.0 Flash**.")


# ---------------------------------------------------
# 15-MARK ANSWER TEMPLATE
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
# GROUP + TOPICS INPUT FIELD
# ---------------------------------------------------
group_text = st.text_area(
    "Enter Groups and Topics Below:",
    height=280,
    placeholder="LLM:\nTransformers\nTokenization\n\nAPI:\nREST API\nGraphQL"
)

generate_btn = st.button("🚀 Generate All Answers")


# ---------------------------------------------------
# PROCESSING & GENERATING ANSWERS
# ---------------------------------------------------
if generate_btn:

    # Check API key
    if not api_key:
        st.error("❌ Please enter your Gemini API key!")
        st.stop()

    # Check input text
    if not group_text.strip():
        st.error("❌ Please enter at least one group with topics!")
        st.stop()

    # Initialize Gemini Client
    client = genai.Client(api_key=api_key)

    groups = {}
    current_group = None

    # ---------------------------------------------------
    # PARSE USER INPUT INTO GROUPS + TOPICS
    # ---------------------------------------------------
    for line in group_text.split("\n"):
        line = line.strip()

        if not line:
            continue

        if line.endswith(":"):  # New group
            current_group = line[:-1].strip()
            groups[current_group] = []
        else:
            if current_group:
                groups[current_group].append(line)


    # ---------------------------------------------------
    # GENERATE ANSWERS FOR EACH TOPIC
    # ---------------------------------------------------
    st.markdown("---")
    st.subheader("📚 **Generated 15-Marks Answers**")

    for group_name, topics in groups.items():

        st.markdown(f"# 🟦 Group: **{group_name}**")
        st.markdown("---")

        for topic in topics:

            st.markdown(f"## 🔹 Topic: **{topic}**")
            st.markdown("---")

            final_prompt = exam_prompt_template.replace("{TOPIC}", topic)

            # Gemini Model Generation
            with st.spinner(f"Generating answer for: {topic} ..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=final_prompt
                    )
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"❌ Error generating answer for {topic}: {e}")

            st.markdown("---")
