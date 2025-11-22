import streamlit as st
from google import genai
import re

st.set_page_config(page_title="SEO Blog Generator + SEO Analyzer", page_icon="📝", layout="wide")

st.title("SEO Blog Generator (1200 Words + Full SEO Page + Analyzer)")

st.write("This tool generates a full SEO article with red H2 headings, external links, SEO scoring, and copy buttons for all sections.")

# ----------------------------------------
# SIDEBAR
# ----------------------------------------
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    website_link = st.text_input("Enter Your Website Link:", "https://yourwebsite.com")
    st.write("Wikipedia link is auto-added from topic.")

if not api_key:
    st.warning("Please enter your Gemini API key.")
    st.stop()

client = genai.Client(api_key=api_key)

# ----------------------------------------
# COPY BUTTON FUNCTION
# ----------------------------------------
def copy_box(text, label):
    st.code(text)
    st.button(f"Copy {label}", key=label)

# ----------------------------------------
# INPUTS
# ----------------------------------------
seo_topic = st.text_input("Enter Blog Topic:")
extra_line = st.text_input("Required line inside first 100 words:")
generate = st.button("Generate Full SEO Page")

# ----------------------------------------
# GENERATOR START
# ----------------------------------------
if generate and seo_topic:

    prompt = f"""
Write a 1200-word SEO-optimized blog article on "{seo_topic}".

RULES:
- No markdown (*, **, #).
- Use plain text.
- H1 must be written as: H1: Title here
- H2 must be written as: H2: Heading text
- First 100 words must contain: "{extra_line}"

Return EXACT format:

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
(full article with only H1: and H2:)
"""

    with st.spinner("Generating Article…"):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        raw = response.text.replace("*", "").replace("#", "")

        sections = {
            "Focus Keyphrase": "",
            "Slug": "",
            "Meta Title": "",
            "Meta Description": "",
            "H1": "",
            "Full Blog Content": ""
        }

        # SPLIT SECTIONS
        for key in sections.keys():
            marker = f"{key}:"
            if marker in raw:
                part = raw.split(marker)[1]
                try:
                    next_marker = next(
                        x for x in sections.keys()
                        if x != key and f"{x}:" in part
                    )
                    sections[key] = part.split(f"{next_marker}:")[0].strip()
                except StopIteration:
                    sections[key] = part.strip()

        # FORMAT H1
        h1_html = f"<h1 style='color:black; font-weight:bold;'>{sections['H1']}</h1>"

        # FORMAT H2 → RED HTML
        content_html = sections["Full Blog Content"]
        content_html = re.sub(
            r"H2:\s*(.+)",
            r"<h2 style='color:red;'>\1</h2>",
            content_html
        )

        # ----------------------------------------
        # SEO ANALYZER
        # ----------------------------------------
        def seo_analyze(text, keyphrase, title, desc):
            score = 100
            data = {}

            wc = len(text.split())
            data["Word Count"] = wc
            if wc < 900:
                score -= 10

            kd = (text.lower().count(keyphrase.lower()) / wc) * 100 if wc > 0 else 0
            data["Keyword Density %"] = round(kd, 2)
            if kd < 0.8 or kd > 3.5:
                score -= 5

            tl = len(title)
            data["Meta Title Length"] = tl
            if tl > 60:
                score -= 5

            dl = len(desc)
            data["Meta Description Length"] = dl
            if dl > 160:
                score -= 5

            pv = len(re.findall(r"\\bwas\\b|\\bwere\\b|\\bbeen\\b", text.lower()))
            pv_percent = (pv / wc) * 100 if wc > 0 else 0
            data["Passive Voice %"] = round(pv_percent, 2)
            if pv_percent > 7:
                score -= 5

            sentences = re.split(r"[.!?]", text)
            sent_lens = [len(s.split()) for s in sentences if len(s.split()) > 0]
            avg_len = sum(sent_lens) / len(sent_lens) if sent_lens else 0
            data["Average Sentence Length"] = round(avg_len, 2)
            if avg_len > 22:
                score -= 5

            data["Final SEO Score"] = max(0, score)
            return data

        score = seo_analyze(
            sections["Full Blog Content"],
            sections["Focus Keyphrase"],
            sections["Meta Title"],
            sections["Meta Description"]
        )

        # ----------------------------------------
        # OUTPUT — FULL PAGE
        # ----------------------------------------
        st.subheader("Full SEO Page Output")

        # FOCUS KEYPHRASE
        st.write("Focus Keyphrase:")
        copy_box(sections["Focus Keyphrase"], "Focus Keyphrase")

        # SLUG
        st.write("Slug:")
        copy_box(sections["Slug"], "Slug")

        # META TITLE
        st.write("Meta Title:")
        copy_box(sections["Meta Title"], "Meta Title")

        # META DESCRIPTION
        st.write("Meta Description:")
        copy_box(sections["Meta Description"], "Meta Description")

        # H1
        st.write("H1:")
        st.markdown(h1_html, unsafe_allow_html=True)
        copy_box(sections["H1"], "H1")

        # FULL CONTENT
        st.write("Full Blog Content:")
        copy_box(sections["Full Blog Content"], "Full Blog Content (Plain)")
        st.markdown(content_html, unsafe_allow_html=True)

        # EXTERNAL LINKS
        st.subheader("External Links")
        wiki = f"https://en.wikipedia.org/wiki/{seo_topic.replace(' ', '_')}"
        st.write("Your Website:", website_link)
        st.write("Wikipedia:", wiki)

        # SEO SCORE
        st.subheader("SEO Score Analyzer")
        for k, v in score.items():
            st.write(f"{k}: {v}")
