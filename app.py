import streamlit as st
from google import genai
import re

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

st.write("Generates clean SEO articles with RED H2 headings and zero markdown symbols.")


# ---------------------------------------------------
# SIDEBAR — API KEY
# ---------------------------------------------------
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.write("1200-word SEO content + red H2 headings")

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

RULES:
1. NO markdown symbols: no *, no **, no #, no ##
2. Use plain text only
3. H2 headings MUST be written like this format inside text:
   H2: Your Heading
4. The first 100 words MUST contain: "{extra_line}"
5. Include these sections:

Focus Keyphrase:
Slug:
Meta Title:
Meta Description:
H1:
Full Blog Content:

### In Full Blog Content:
- H2 headings MUST be marked as: H2: Heading Text
- Do NOT use any markdown

Return output EXACTLY in this format:

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
(full text with H2: headings only)
"""

    with st.spinner("Generating SEO Blog…"):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=seo_prompt
            )

            raw = response.text

            # remove *, **, # just in case
            raw = raw.replace("*", "").replace("#", "")

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

            # APPLY RED H2 FORMATTING
            content = sections["Full Blog Content"]

            # Replace "H2: text" → red HTML H2
            content = re.sub(
                r"H2:\s*(.*)",
                r'<h2 style="color:red;">\1</h2>',
                content
            )

            # Show RIGHT panel items
            right.subheader("SEO Elements")

            for title, text in sections.items():
                if title == "Full Blog Content":
                    continue
                right.write(title)
                copy_box(text, title)

            # Show LEFT panel content with HTML enabled
            left.write("Full SEO Blog Content (with Red H2 headings):")
            left.markdown(content, unsafe_allow_html=True)

        except Exception as e:
            left.error(f"Error generating blog: {e}")
