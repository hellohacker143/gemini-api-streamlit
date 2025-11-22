import streamlit as st
from google import genai

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------
st.set_page_config(
    page_title="Grouped 15-Marks Answer Generator",
    page_icon="📝",
    layout="wide"
)

# ---------------------------------------------------
# MAIN TITLE
# ---------------------------------------------------
st.title("📝 Grouped 15-Marks Answer Generator")
st.markdown("""
Generate **topper-quality**, fully structured **15-mark university exam answers**  
for multiple groups & topics — clean, neat, SEO-optimized.
""")


# ---------------------------------------------------
# SIDEBAR (API KEY)
# ---------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Enter Gemini API Key",
        type="password",
        help="Get API Key → https://aistudio.google.com/apikey"
    )

    st.markdown("---")
    st.write("🔹 Generates **structured 15-mark answers**.")
    st.write("🔹 Supports **multiple groups & multiple topics**.")
    st.write("🔹 Adds **SEO title, keywords, meta description**.")
    st.write("🔹 Powered by **Gemini 2.0 Flash**.")


# ---------------------------------------------------
# 15-MARK ANSWER TEMPLATE
# ---------------------------------------------------
exam_prompt_template = """
Generate a perfect 15-marks university exam answer on: “{TOPIC}”.
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

After completing the 15-mark answer, also generate an SEO panel with:

SEO Title  
Focus Keyphrase  
Meta Description (150 chars)  
5 Strong Keywords  
Short Summary For Blog (5 lines)

Do NOT mention headings like "SEO panel" inside the main answer.
"""


# ---------------------------------------------------
# GROUP + TOPIC INPUT
# ---------------------------------------------------
group_text = st.text_area(
    "Enter Groups and Topics Below:",
    height=280,
    placeholder="LLM:\nTransformers\nTokenization\n\nAPI:\nREST API\nGraphQL"
)

generate_btn = st.button("🚀 Generate All Answers")


# ---------------------------------------------------
# COPY BUTTON FUNCTION
# ---------------------------------------------------
def copy_button(label, text, key):
    st.code(text)
    st.button(label, key=key, on_click=st.session_state.update, kwargs={"key": key})


# ---------------------------------------------------
# PROCESS
# ---------------------------------------------------
if generate_btn:

    if not api_key:
        st.error("❌ Please enter API key!")
        st.stop()

    if not group_text.strip():
        st.error("❌ Enter at least one group with topics!")
        st.stop()

    # Gemini Client
    client = genai.Client(api_key=api_key)

    groups = {}
    current_group = None

    # Parse Groups + Topics
    for line in group_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        if line.endswith(":"):
            current_group = line[:-1].strip()
            groups[current_group] = []
        else:
            if current_group:
                groups[current_group].append(line)

    st.markdown("---")
    st.subheader("📚 **Generated Structured Content**")

    # ---------------------------------------------------
    # GENERATION LOOP
    # ---------------------------------------------------
    for group_name, topics in groups.items():

        st.markdown(f"# 🟦 Group: **{group_name}**")
        st.markdown("---")

        for topic in topics:

            st.markdown(f"## 🔹 Topic: **{topic}**")

            prompt = exam_prompt_template.replace("{TOPIC}", topic)

            with st.spinner(f"Generating answer for: {topic} ..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt
                    )

                    output = response.text

                except Exception as e:
                    st.error(f"Error: {e}")
                    continue

            # ---------------------------------------------------
            # SPLIT MAIN ANSWER + SEO PANEL
            # ---------------------------------------------------
            if "SEO Title" in output:
                main_answer, seo_panel = output.split("SEO Title", 1)
                seo_panel = "SEO Title" + seo_panel
            else:
                main_answer = output
                seo_panel = "SEO not generated"

            # ---------------------------------------------------
            # TWO FRAME LAYOUT
            # ---------------------------------------------------
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📘 15-Mark Answer")
                st.code(main_answer)
                st.button("📋 Copy Answer", key=f"copy_answer_{topic}")

            with col2:
                st.subheader("🔍 SEO Content Panel")
                st.code(seo_panel)
                st.button("📋 Copy SEO Panel", key=f"copy_seo_{topic}")

            st.markdown("---")
