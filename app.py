import streamlit as st
from google import genai

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="SEO Blog Generator",
    page_icon="📝",
    layout="wide"
)

# ---------------------------------------------------
# MAIN TITLE
# ---------------------------------------------------
st.title("SEO-Optimized 1200-Word Blog Generator")

st.write(
    "Create fully optimized, SEO-first 1200-word blog posts with complete SEO elements."
)

# ---------------------------------------------------
# SIDEBAR — API KEY
# ---------------------------------------------------
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.write("Generates full SEO content + SEO metadata")

if not api_key:
    st.warning("Please enter your Gemini API key to continue.")
else:
    client = genai.Client(api_key=api_key)


# ---------------------------------------------------
# TWO-FRAME LAYOUT
# ---------------------------------------------------
left, right = st.columns([2.2, 1])


# Copy box
def copy_box(text, key):
    st.code(text)
    st.button(f"Copy {key}", key=key)


# ---------------------------------------------------
# LEFT PANEL → SEO GENERATOR
# ---------------------------------------------------
left.subheader("SEO Blog Generator")

seo_topic = left.text_input("Enter Blog Topic:")
extra_line = left.text_input("Sentence required in first 100 words:")
generate_blog = left.button("Generate SEO Blog")

# ---------------------------------------------------
# SEO GENERATION
# ---------------------------------------------------
if generate_blog and seo_topic:

    seo_prompt = f"""
Write a 1200-word SEO-optimized blog article on the topic: "{seo_topic}".

Include:
1. Focus Keyphrase
2. SEO-Friendly Slug
3. Meta Title (max 60 chars)
4. Meta Description (max 160 chars)
5. Perfect H1 (no markdown)
6. H2 / H3 structure (no markdown)
7. First 100 words must contain: "{extra_line}"
8. Full 1200-word content in simple text only (NO **, NO ##, NO markdown)
9. Return output in EXACTLY this format:

Focus Keyphrase:
(text)

Slug:
(text)

Meta Title:
(text)

Meta Description:
(text)

H1:
(text)

Full Blog Content:
(full content, no markdown)
"""

    with st.spinner("Generating SEO Blog…"):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=seo_prompt
            )

            raw = response.text

            # Remove markdown symbols if any appear
            raw = raw.replace("**", "").replace("#", "")

            # Split sections
            sections = {
                "Focus Keyphrase": "",
                "Slug": "",
                "Meta Title": "",
                "Meta Description": "",
                "H1": "",
                "Full Blog Content": ""
            }

            for title in sections.keys():
                marker = f"{title}:"
                if marker in raw:
                    part = raw.split(marker)[1]
                    try:
                        next_marker = next(
                            m for m in sections.keys()
                            if m != title and f"{m}:" in part
                        )
                        sections[title] = part.split(f"{next_marker}:")[0].strip()
                    except StopIteration:
                        sections[title] = part.strip()

            # RIGHT PANEL – SEO ELEMENTS
            right.subheader("SEO Elements")

            for title, text in sections.items():
                right.write(title)
                copy_box(text, title)

            # LEFT PANEL – FULL BLOG CONTENT
            left.write("Full SEO Blog")
            left.write(sections["Full Blog Content"])

        except Exception as e:
            left.error(f"Error generating blog: {e}")
