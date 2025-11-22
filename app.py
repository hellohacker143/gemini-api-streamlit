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


# COPy BUTTON FUNCTION
def copy_box(text, label):
    st.code(text)
    st.button(f"📋 Copy {label}", key=label)


# ---------------------------------------------------
# LEFT FRAME → SEO BLOG GENERATOR
# ---------------------------------------------------
left.subheader("📰 SEO-Optimized 1200-Word Blog Generator")

seo_topic = left.text_input("Enter Blog Topic:")
extra_line = left.text_input("Add required line for first 100 words:")

generate_blog = left.button("🚀 Generate SEO Blog")

# ---------------------------------------------------
# SEO BLOG GENERATION
# ---------------------------------------------------
if generate_blog and seo_topic:

    seo_prompt = f"""
Write a 1200-word SEO-optimized blog post on the topic: "{seo_topic}".

Include ALL SEO elements below:

1. Focus Keyphrase (exact match)
2. SEO-Friendly Slug
3. Meta Title (max 60 chars)
4. Meta Description (max 160 chars)
5. Perfect H1
6. H2 / H3 structure
7. First 100 words must contain this line: "{extra_line}"
8. Full 1200-word blog content

Return output in this format:

### Focus Keyphrase:
(text)

### Slug:
(text)

### Meta Title:
(text)

### Meta Description:
(text)

### H1:
(text)

### Full Blog Content:
(full blog)
"""

    with st.spinner("Generating SEO Blog…"):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=seo_prompt
            )

            full_output = response.text

            # Split sections safely (no JSON needed)
            sections = {
                "Focus Keyphrase": "",
                "Slug": "",
                "Meta Title": "",
                "Meta Description": "",
                "H1": "",
                "Full Blog Content": ""
            }

            for key in sections.keys():
                marker = f"### {key}:"
                if marker in full_output:
                    part = full_output.split(marker)[1]
                    try:
                        next_marker = next(
                            m for m in sections.keys()
                            if m != key and f"### {m}:" in part
                        )
                        sections[key] = part.split(f"### {next_marker}:")[0].strip()
                    except StopIteration:
                        sections[key] = part.strip()

            # RIGHT PANEL → SEO ELEMENTS
            right.subheader("📌 SEO Elements")

            for title, text in sections.items():
                right.markdown(f"### 🔹 {title}")
                copy_box(text, title)

            # LEFT PANEL → FULL BLOG
            left.markdown("### 📰 Full SEO Blog")
            left.markdown(sections["Full Blog Content"])

        except Exception as e:
            left.error(f"Error generating blog: {e}")


# ---------------------------------------------------
# 15-MARK ANSWER GENERATOR
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
                try:
                    final_prompt = exam_prompt_template.replace("{TOPIC}", topic)
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=final_prompt
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")
            st.markdown("---")
