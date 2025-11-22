
            import streamlit as st
from google import genai
import re

st.set_page_config(page_title="SEO Writer + Full SEO Page", page_icon="📝", layout="wide")

st.title("Complete SEO Blog Writer (1200 Words + Full SEO Page + Analyzer)")

st.write("This tool generates a full SEO article with red H2 headings, external links, SEO score, and copy buttons for ALL sections.")


# ----------------------------------------
# SIDEBAR
# ----------------------------------------
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    website_link = st.text_input("Enter Your Website Link:", "https://yourwebsite.com")
    st.write("Wiki link auto-added from topic.")


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
extra_line = st.text_input("Required line for first 100 words:")
generate = st.button("Generate Full SEO Page")


# ----------------------------------------
# GENERATE
# ----------------------------------------
if generate and seo_topic:

    prompt = f"""
Write a 1200-word SEO-optimized blog article on "{seo_topic}".

RULES:
- No markdown: no *, no #, no **.
- Use plain text.
- H1 must be written as: H1: Title Here
- Each H2 must be written as: H2: Heading Text
- First 100 words MUST contain: "{extra_line}"

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
(full article, only H1: and H2: format)
"""

    with st.spinner("Generating Article…"):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        raw = response.text

        raw = raw.replace("*", "").replace("#", "")

        sections = {
            "Focus Keyphrase": "",
            "Slug": "",
            "Meta Title": "",
            "Meta Description": "",
            "H1": "",
            "Full Blog Content": ""
        }

        # SPLITTING
        for key in sections.keys():
            marker = f"{key}:"
            if marker in raw:
                part = raw.split(marker)[1]
                try:
                    next_marker = next(
                        other for other in sections.keys()
                        if other != key and f"{other}:" in part
                    )
                    sections[key] = part.split(f"{next_marker}:")[0].strip()
                except StopIteration:
                    sections[key] = part.strip()

        # Format H1
        h1_html = f"<h1 style='color:black; font-weight:bold;'>{sections['H1']}</h1>"

        # Format H2 as red
        content_html = sections["Full Blog Content"]
        content_html = re.sub(
            r"H2:\s*(.+)",
            r"<h2 style='color:red;'>\1</h2>",
            content_html
        )

        # Remove H1: from content if exists
        content_html = content_html.replace("H1:", "")

        # ----------------------------------------
        # SEO ANALYZER
        # ----------------------------------------
        def seo_analyze(text, keyphrase, title, desc):
            score = 100
            results = {}

            wc = len(text.split())
            results["Word Count"] = wc
            if wc < 900:
                score -= 10
            elif wc < 1200:
                score -= 4

            kcount = text.lower().count(keyphrase.lower())
            density = (kcount / wc) * 100 if wc > 0 else 0
            results["Keyword Density %"] = round(density, 2)
            if density < 0.8:
                score -= 10
            elif density > 3.5:
                score -= 5

            tlen = len(title)
            results["Meta Title Length"] = tlen
            if tlen > 60:
                score -= 5

            dlen = len(desc)
            results["Meta Description Length"] = dlen
            if dlen > 160:
                score -= 5

            passive = len(re.findall(r"\\bwas\\b|\\bwere\\b|\\bbeen\\b", text.lower()))
            passive_per = (passive / wc) * 100 if wc > 0 else 0
            results["Passive Voice %"] = round(passive_per, 2)
            if passive_per > 7:
                score -= 5

            sentences = re.split(r"[.!?]", text)
            lens = [len(s.split()) for s in sentences if len(s.split()) > 0]
            avg_len = sum(lens) / len(lens) if lens else 0
            results["Average Sentence Length"] = round(avg_len, 2)
            if avg_len > 22:
                score -= 5

            results["Final SEO Score"] = max(0, score)
            return results

        score = seo_analyze(
            sections["Full Blog Content"],
            sections["Focus Keyphrase"],
            sections["Meta Title"],
            sections["Meta Description"]
        )

        # ----------------------------------------
        # DISPLAY FULL PAGE (OPTION A)
        # ----------------------------------------

        st.subheader("Full SEO Page Output")

        # Focus Keyphrase
        st.write("Focus Keyphrase:")
        copy_box(sections["Focus Keyphrase"], "Focus Keyphrase")

        # Slug
        st.write("Slug:")
        copy_box(sections["Slug"], "Slug")

        # Meta Title
        st.write("Meta Title:")
        copy_box(sections["Meta Title"], "Meta Title")

        # Meta Description
        st.write("Meta Description:")
        copy_box(sections["Meta Description"], "Meta Description")

        # H1
        st.write("H1:")
        st.markdown(h1_html, unsafe_allow_html=True)
        copy_box(sections["H1"], "H1")

        # CONTENT
        st.write("Full Blog Content:")
        copy_box(sections["Full Blog Content"], "Full Blog Content (Plain)")
        st.markdown(content_html, unsafe_allow_html=True)

        # ----------------------------------------
        # EXTERNAL LINKS
        # ----------------------------------------
        st.subheader("External Links")
        wiki_link = f"https://en.wikipedia.org/wiki/{seo_topic.replace(' ', '_')}"
        st.write("Your Website Link:", website_link)
        st.write("Wikipedia Link:", wiki_link)

        # ----------------------------------------
        # SEO SCORE
        # ----------------------------------------
        st.subheader("SEO Score Analyzer")

        for k, v in score.items():
            st.write(f"{k}: {v}")
