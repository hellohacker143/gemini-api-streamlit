import streamlit as st
from google import genai

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------
st.set_page_config(
    page_title="Grouped 15-Marks + SEO Generator",
    page_icon="📝",
    layout="wide"
)

# ---------------------------------------------------
# MAIN TITLE
# ---------------------------------------------------
st.title("📝 Grouped 15-Marks Answer + SEO Content Generator")
st.markdown("""
Generate **topper-quality exam answers** and **SEO content** in two frames.
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
    st.write("🔹 15-Marks Generator")
    st.write("🔹 SEO Title + Description + Keywords")
    st.write("🔹 Copy buttons included")


# ---------------------------------------------------
# LEFT + RIGHT COLUMNS
# ---------------------------------------------------
left, right = st.columns(2)


# ---------------------------------------------------
# ---------------------- FRAME 1 ---------------------
# ------------------ 15-MARKS ANSWERS ----------------
# ---------------------------------------------------
with left:
    st.header("📘 15-Marks Grouped Answer Generator")

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

Make the answer clean, structured, and ready to score full marks.
"""

    group_text = st.text_area(
        "Enter Groups & Topics:",
        height=250,
        placeholder="LLM:\nTransformers\nTokenization\n\nAPI:\nREST API\nGraphQL"
    )

    generate_answers = st.button("🚀 Generate Answers")

    if generate_answers:

        if not api_key:
            st.error("Please enter your API key!")
            st.stop()

        if not group_text.strip():
            st.error("Please enter groups and topics!")
            st.stop()

        client = genai.Client(api_key=api_key)
        groups = {}
        current_group = None

        # ---- PARSE GROUPS ----
        for line in group_text.split("\n"):
            line = line.strip()
            if not line:
                continue

            if line.endswith(":"):
                current_group = line[:-1]
                groups[current_group] = []
            else:
                if current_group:
                    groups[current_group].append(line)

        st.subheader("📚 Generated Answers")

        # ---- GENERATE ANSWERS ----
        for group, topics in groups.items():
            st.markdown(f"### 🟦 Group: **{group}**")
            for topic in topics:
                st.markdown(f"#### 🔹 Topic: **{topic}**")
                final_prompt = exam_prompt_template.replace("{TOPIC}", topic)

                with st.spinner(f"Generating answer for {topic}..."):
                    try:
                        res = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=final_prompt
                        )
                        answer = res.text

                        # Display answer
                        st.markdown(answer)

                        # Copy button
                        st.code(answer)
                        st.button(f"📋 Copy Answer: {topic}", key=f"copy_{topic}")

                    except Exception as e:
                        st.error(f"Error: {e}")

                st.markdown("---")


# ---------------------------------------------------
# ---------------------- FRAME 2 ---------------------
# --------------------- SEO TOOL KIT -----------------
# ---------------------------------------------------
with right:
    st.header("📈 SEO Content Generator")

    seo_topic = st.text_input(
        "Enter Topic / Keyword:",
        placeholder="Example: Best AI Tools for Students"
    )

    generate_seo = st.button("✨ Generate SEO Content")

    if generate_seo:

        if not api_key:
            st.error("Please enter your API key!")
            st.stop()

        if not seo_topic.strip():
            st.error("Enter a keyword for SEO!")
            st.stop()

        seo_prompt = f"""
Generate SEO content for the topic: {seo_topic}
Include:
- SEO Optimized Article (150–200 words)
- 10 Focus Keywords
- SEO Title (70 characters)
- SEO Description (160 characters)
"""

        client = genai.Client(api_key=api_key)

        with st.spinner("Generating SEO content..."):
            try:
                res = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=seo_prompt
                )
                seo_output = res.text

                st.subheader("📝 SEO Content Output")
                st.markdown(seo_output)

                st.code(seo_output)
                st.button("📋 Copy SEO Content", key="copy_seo")

            except Exception as e:
                st.error(f"Error: {e}")
