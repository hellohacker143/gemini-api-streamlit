import streamlit as st
from google import genai

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Grouped + SEO Blog Generator",
    page_icon="📝",
    layout="wide"
)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.title("📝 Multi-Purpose Generator: 15-Marks + SEO Blog Writer")

st.markdown("""
Generate **university 15-marks answers** and **1200-word SEO-optimized blog posts**
with complete SEO elements in two clean frames.
""")

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Enter Gemini API Key",
        type="password"
    )
    st.markdown("---")
    st.write("🔹 15-Marks Answer Generator")
    st.write("🔹 1200-Words SEO Blog Generator")
    st.write("🔹 Powered by Gemini 2.0 Flash")

if not api_key:
    st.warning("Enter your API key to start.")
else:
    client = genai.Client(api_key=api_key)

# ---------------------------------------------------
# TWO-FRAME LAYOUT
# ---------------------------------------------------
left, right = st.columns([2.2, 1])

# ---------------------------------------------------
# LEFT FRAME → SEO BLOG GENERATOR
# ---------------------------------------------------
left.subheader("📰 SEO-Optimized 1200-Word Blog Generator")

seo_topic = left.text_input("Enter Blog Topic:")
extra_line = left.text_input("Add a required sentence in first 100 words:")
generate_blog = left.button("🚀 Generate SEO Blog")

# SEO Prompt
seo_prompt = """
Write a fully SEO-optimized blog post of 1200 words on the topic: "{TOPIC}"

Include:
✔️ Focus Keyphrase (exact match)
✔️ SEO-Friendly Slug
✔️ Meta Title (60 characters)
✔️ Meta Description (160 characters)
✔️ Perfect H1
✔️ H2 and H3 structure
✔️ First 100 words containing this line: "{EXTRA}"
✔️ Clean, neat, SEO-first writing style
✔️ Format in Markdown

Return output in this JSON structure:
{
 "keyphrase": "",
 "slug": "",
 "meta_title": "",
 "meta_description": "",
 "h1": "",
 "content": ""
}
"""

# ---------------------------------------------------
# RIGHT FRAME → SEO ELEMENT PANEL
# ---------------------------------------------------
right.subheader("📌 SEO Elements")

def copy_btn(text, label):
    right.code(text, language="")
    right.button(f"📋 Copy {label}", key=label)

# ---------------------------------------------------
# GENERATE BLOG
# ---------------------------------------------------
if generate_blog and seo_topic:
    with st.spinner("Generating SEO-Optimized Blog…"):
        final_prompt = seo_prompt.replace("{TOPIC}", seo_topic).replace("{EXTRA}", extra_line)

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=final_prompt
            )

            import json
            data = json.loads(response.text)

            # SHOW OUTPUT IN RIGHT FRAME
            right.markdown("### 🎯 Focus Keyphrase")
            copy_btn(data["keyphrase"], "Keyphrase")

            right.markdown("### 🔗 SEO-Friendly Slug")
            copy_btn(data["slug"], "Slug")

            right.markdown("### 🏷️ Meta Title")
            copy_btn(data["meta_title"], "Meta Title")

            right.markdown("### 📝 Meta Description")
            copy_btn(data["meta_description"], "Meta Description")

            right.markdown("### 🏆 H1 Tag")
            copy_btn(data["h1"], "H1")

            # FULL CONTENT IN LEFT PANEL
            left.markdown("### 📰 Full 1200-Word SEO Blog")
            left.markdown(data["content"])

        except Exception as e:
            left.error(f"Error: {e}")

# ---------------------------------------------------
# 15-MARK ANSWER GENERATOR BELOW
# ---------------------------------------------------
st.markdown("---")
st.header("📚 Grouped 15-Marks Answer Generator")

group_text = st.text_area(
    "Enter Groups and Topics:",
    height=250,
    placeholder="LLM:\nTransformers\nTokenization\n\nAPI:\nREST\nGraphQL"
)

generate_btn = st.button("🧾 Generate All 15-Mark Answers")

exam_prompt_template = """
Generate a perfect 15-marks university exam answer on the topic: “{TOPIC}” in topper-writing style.

Structure:
Introduction – bullets
Definition – bullets
Diagram – text format
6 Key Points – heading + explanation
Features – bullets
Advantages – bullets
Characteristics – bullets
Applications
Conclusion

Direct answer only.
"""

if generate_btn:
    if not group_text.strip():
        st.error("Enter at least one group!")
        st.stop()

    groups = {}
    current_group = None

    # Parse text
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

    st.markdown("## 📘 Generated Answers")

    for group_name, topics in groups.items():
        st.markdown(f"### 🟦 Group: **{group_name}**")
        st.markdown("---")

        for topic in topics:
            st.markdown(f"## 🔹 Topic: **{topic}**")
            with st.spinner(f"Generating {topic}..."):
                final_prompt = exam_prompt_template.replace("{TOPIC}", topic)
                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=final_prompt
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")
            st.markdown("---")
