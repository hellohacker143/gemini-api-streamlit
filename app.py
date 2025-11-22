import streamlit as st
from google import genai
import re

st.set_page_config(page_title="SEO Article Generator + Analyzer", page_icon="📝", layout="wide")

st.title("SEO Blog Generator (H1, Red H2, Blue H3 + Links + Analyzer)")

st.write("Generate full SEO article with clean HTML headings, clickable links, copy buttons, and SEO scoring.")


# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    website_link = st.text_input("Your Website Link", "https://yourwebsite.com")
    st.write("Wikipedia link auto-created using your topic.")

if not api_key:
    st.warning("Enter your Gemini API key to continue.")
    st.stop()

client = genai.Client(api_key=api_key)

# ----------------------------------------------------
# COPY BOX FUNCTION
# ----------------------------------------------------
def copy_box(text, label):
    st.code(text)
    st.button(f"Copy {label}", key=label)


# ----------------------------------------------------
# USER INPUTS
# ----------------------------------------------------
seo_topic = st.text_input("Blog Topic:")
extra_line = st.text_input("Required line (inside first 100 words):")
generate = st.button("Generate SEO Article")


# ----------------------------------------------------
# GENERATE ARTICLE
# ----------------------------------------------------
if generate and seo_topic:

    prompt = f"""
Write a 1200-word SEO-optimized blog article on "{seo_topic}".

RULES:
- NO markdown characters (*, #, **).
- Use ONLY text + H1/H2/H3 markers.
- H1 must be: H1: Main Title
- H2 must be: H2: Section Title
- H3 must be: H3: Subsection Title
- Must include the line: "{extra_line}" within first 100 words.
- Full article must be plain text with H1:, H2:, H3: markers.

Return EXACT structure:

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
(full article with H1:, H2:, H3:)
"""

    with st.spinner("Generating Article…"):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        raw = response.text.replace("*", "").replace("#", "")

        # ----------------------------------------
        # SPLIT SECTIONS
        # ----------------------------------------
        sections = {
            "Focus Keyphrase": "",
            "Slug": "",
            "Meta Title": "",
            "Meta Description": "",
            "H1": "",
            "Full Blog Content": ""
        }

        for key in sections.keys():
            marker = f"{key}:"
            if marker in raw:
                part = raw.split(marker)[1]
                try:
                    next_marker = next(x for x in sections.keys()
                                       if x != key and f"{x}:" in part)
                    sections[key] = part.split(f"{next_marker}:")[0].strip()
                except StopIteration:
                    sections[key] = part.strip()

        # ----------------------------------------
        # FORMAT HEADINGS (convert markers to HTML)
        # ----------------------------------------
        content_html = sections["Full Blog Content"]

        # H1
        content_html = re.sub(
            r"H1:\s*(.+)",
            r"<h1 style='color:black;'>\1</h1>",
            content_html
        )

        # H2
        content_html = re.sub(
            r"H2:\s*(.+)",
            r"<h2 style='color:red;'>\1</h2>",
            content_html
        )

        # H3
        content_html = re.sub(
            r"H3:\s*(.+)",
            r"<h3 style='color:blue;'>\1</h3>",
            content_html
        )

        # ----------------------------------------
        # ADD CLICKABLE LINKS INSIDE CONTENT
        # ----------------------------------------
        wiki_link = f"https://en.wikipedia.org/wiki/{seo_topic.replace(' ', '_')}"

        links_html = f"""
<br><br>
<h3 style='color:blue;'>External References</h3>

<p>Visit My Website:  
<a href="{website_link}" target="_blank">{website_link}</a></p>

<p>Read More on Wikipedia:  
<a href="{wiki_link}" target="_blank">{wiki_link}</a></p>
"""

        content_html = content_html + links_html

        # ----------------------------------------
        # SEO ANALYZER
        # ----------------------------------------
        def seo_analyze(text, keyphrase, title, description):
            score = 100
            data = {}

            words = len(text.split())
            data["Word Count"] = words
            if words < 900:
                score -= 10

            kd = (text.lower().count(keyphrase.lower()) / words) * 100 if words > 0 else 0
            data["Keyword Density %"] = round(kd, 2)
            if kd < 0.8 or kd > 3.5:
                score -= 5

            mt_len = len(title)
            data["Meta Title Length"] = mt_len
            if mt_len > 60:
                score -= 5

            md_len = len(description)
            data["Meta Description Length"] = md_len
            if md_len > 160:
                score -= 5

            passive_hits = len(re.findall(r"\bwas\b|\bwere\b|\bbeen\b", text.lower()))
            passive_percent = (passive_hits / words) * 100 if words > 0 else 0
            data["Passive Voice %"] = round(passive_percent, 2)
            if passive_percent > 7:
                score -= 5

            sentences = re.split(r"[.!?]", text)
            lengths = [len(s.split()) for s in sentences if len(s.split()) > 0]
            avg_len = sum(lengths) / len(lengths) if lengths else 0
            data["Average Sentence Length"] = round(avg_len, 2)
            if avg_len > 22:
                score -= 5

            data["Final SEO Score"] = max(0, score)
            return data

        seo_score = seo_analyze(
            sections["Full Blog Content"],
            sections["Focus Keyphrase"],
            sections["Meta Title"],
            sections["Meta Description"]
        )

        # ------------------------------------------------
        # DISPLAY OUTPUT (FULL PAGE)
        # ------------------------------------------------
        st.subheader("Complete SEO Output")

        st.write("Focus Keyphrase:")
        copy_box(sections["Focus Keyphrase"], "Focus Keyphrase")

        st.write("Slug:")
        copy_box(sections["Slug"], "Slug")

        st.write("Meta Title:")
        copy_box(sections["Meta Title"], "Meta Title")

        st.write("Meta Description:")
        copy_box(sections["Meta Description"], "Meta Description")

        # H1
        st.write("H1:")
        copy_box(sections["H1"], "H1")
        st.markdown(f"<h1>{sections['H1']}</h1>", unsafe_allow_html=True)

        # FULL CONTENT
        st.write("Full SEO Blog Content (H1, H2, H3 + Links):")
        copy_box(sections["Full Blog Content"], "Full Blog Content (Plain)")
        st.markdown(content_html, unsafe_allow_html=True)

        # SEO SCORE
        st.subheader("SEO Analyzer Score")
        for k, v in seo_score.items():
            st.write(f"{k}: {v}")
