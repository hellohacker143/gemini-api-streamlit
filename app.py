import streamlit as st
from google import genai
import re

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="SEO Blog Generator + SEO Analyzer",
    page_icon="📝",
    layout="wide"
)

# ---------------------------------------------------
# MAIN TITLE
# ---------------------------------------------------
st.title("SEO Blog Generator with SEO Score Analyzer")

st.write("Generate 1200-word SEO content with red H2 headings and detailed SEO scoring.")


# ---------------------------------------------------
# SIDEBAR — API KEY
# ---------------------------------------------------
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.write("Features:")
    st.write("- SEO Article Generator")
    st.write("- Red H2 HTML Headings")
    st.write("- SEO Score Analyzer")

if not api_key:
    st.warning("Please enter your Gemini API key to continue.")
else:
    client = genai.Client(api_key=api_key)

# ---------------------------------------------------
# TWO-FRAME LAYOUT
# ---------------------------------------------------
left, right = st.columns([2.2, 1])

# Utility
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
- No markdown: no *, no **, no #, no ##
- Use plain text only
- H2 headings must be written exactly as: H2: Heading Text
- The first 100 words must contain: "{extra_line}"

Return output exactly like:

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

            # Clean just in case
            raw = raw.replace("*", "").replace("#", "")

            # Sections
            sections = {
                "Focus Keyphrase": "",
                "Slug": "",
                "Meta Title": "",
                "Meta Description": "",
                "H1": "",
                "Full Blog Content": ""
            }

            # Split output
            for title in sections.keys():
                marker = f"{title}:"
                if marker in raw:
                    part = raw.split(marker)[1]
                    try:
                        next_marker = next(
                            x for x in sections.keys()
                            if x != title and f"{x}:" in part
                        )
                        sections[title] = part.split(f"{next_marker}:")[0].strip()
                    except StopIteration:
                        sections[title] = part.strip()

            # Replace H2: with red HTML H2
            content = sections["Full Blog Content"]
            content = re.sub(
                r"H2:\s*(.+)",
                r'<h2 style="color:red;">\1</h2>',
                content
            )

            # --------------------------------------------------------
            # SEO ANALYZER FUNCTION
            # --------------------------------------------------------
            def seo_analyzer(text, keyphrase, title, description):
                score = 100
                results = {}

                # Word count
                words = len(text.split())
                results["Word Count"] = words

                if words < 900:
                    score -= 10
                elif words < 1200:
                    score -= 4

                # Keyword density
                kcount = text.lower().count(keyphrase.lower())
                density = (kcount / words) * 100 if words > 0 else 0
                results["Keyword Density %"] = round(density, 2)

                if density < 0.8:
                    score -= 10
                elif density > 3.5:
                    score -= 5

                # Meta title length
                tlen = len(title)
                results["Meta Title Length"] = tlen
                if tlen > 60:
                    score -= 5

                # Meta description length
                dlen = len(description)
                results["Meta Description Length"] = dlen
                if dlen > 160:
                    score -= 5

                # Passive voice (approx)
                passive_hits = len(re.findall(r"\bwas\b|\bwere\b|\bbeen\b", text.lower()))
                passive_percent = (passive_hits / words) * 100 if words > 0 else 0
                results["Passive Voice %"] = round(passive_percent, 2)

                if passive_percent > 7:
                    score -= 5

                # Simple readability check (sentence length avg)
                sentences = re.split(r"[.!?]", text)
                sentence_lengths = [len(s.split()) for s in sentences if len(s.split()) > 0]
                avg_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
                results["Average Sentence Length"] = round(avg_length, 2)

                if avg_length > 22:
                    score -= 5

                # Final score
                results["Final SEO Score"] = max(0, score)
                return results

            # Run Analyzer
            seo_score = seo_analyzer(
                text=sections["Full Blog Content"],
                keyphrase=sections["Focus Keyphrase"],
                title=sections["Meta Title"],
                description=sections["Meta Description"]
            )

            # RIGHT PANEL – SEO ELEMENTS + SCORE
            right.subheader("SEO Elements")

            for title, text in sections.items():
                if title == "Full Blog Content":
                    continue
                right.write(title)
                copy_box(text, title)

            right.subheader("SEO Score Analyzer")

            for k, v in seo_score.items():
                right.write(f"{k}: {v}")

            # LEFT PANEL — FULL BLOG
            left.write("Final SEO Blog Content with Red H2 Headings:")
            left.markdown(content, unsafe_allow_html=True)

        except Exception as e:
            left.error(f"Error generating blog: {e}")
