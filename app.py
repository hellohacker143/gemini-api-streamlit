import streamlit as st
from google import genai
import re
import json
import os

# -------------------------------------------------------
# PAGE SETUP
# -------------------------------------------------------
st.set_page_config(page_title="SEO Generator + Saved History", page_icon="📝", layout="wide")
st.title("SEO Blog Generator + Analyzer + Saved Articles")


# -------------------------------------------------------
# FUNCTIONS FOR JSON STORAGE
# -------------------------------------------------------

SAVE_FILE = "/mnt/data/saved_posts.json"

def load_saved_posts():
    if not os.path.exists(SAVE_FILE):
        return {}
    with open(SAVE_FILE, "r") as f:
        return json.load(f)

def save_post(post_id, data):
    saved = load_saved_posts()
    saved[post_id] = data
    with open(SAVE_FILE, "w") as f:
        json.dump(saved, f, indent=4)

def delete_post(post_id):
    saved = load_saved_posts()
    if post_id in saved:
        del saved[post_id]
        with open(SAVE_FILE, "w") as f:
            json.dump(saved, f, indent=4)


# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")

    website_link = st.text_input("Your Website:", "https://yourwebsite.com")

    st.write("---")
    st.subheader("Saved SEO Posts")

    saved_posts = load_saved_posts()

    selected_post = st.selectbox(
        "Select Old Post",
        ["None"] + list(saved_posts.keys())
    )

    if selected_post != "None":
        if st.button("Delete This Post"):
            delete_post(selected_post)
            st.experimental_rerun()


# -------------------------------------------------------
# COPY BUTTON
# -------------------------------------------------------
def copy_box(text, label):
    st.code(text)
    st.button(f"Copy {label}", key=label)


# -------------------------------------------------------
# LOAD OLD POST IF SELECTED
# -------------------------------------------------------
if selected_post != "None":
    post = saved_posts[selected_post]

    st.subheader(f"Loaded Old SEO Article: {selected_post}")

    st.write("Focus Keyphrase:")
    copy_box(post["keyphrase"], "Keyphrase")

    st.write("Slug:")
    copy_box(post["slug"], "Slug")

    st.write("Meta Title:")
    copy_box(post["meta_title"], "Meta Title")

    st.write("Meta Description:")
    copy_box(post["meta_description"], "Meta Description")

    st.write("H1:")
    st.markdown(f"<h1>{post['h1']}</h1>", unsafe_allow_html=True)

    st.write("Full SEO Content (H1,H2,H3 + Links):")
    st.markdown(post["html_content"], unsafe_allow_html=True)

    st.subheader("SEO Score")
    for k, v in post["seo_score"].items():
        st.write(f"{k}: {v}")

    st.stop()   # STOP — DO NOT SHOW GENERATOR WHEN OLD POST IS LOADED


# -------------------------------------------------------
# SEO GENERATOR SECTION (MAIN PAGE)
# -------------------------------------------------------

seo_topic = st.text_input("Enter Blog Topic:")
extra_line = st.text_input("Required line in first 100 words:")
generate = st.button("Generate New SEO Article")

if generate and api_key and seo_topic:

    client = genai.Client(api_key=api_key)

    prompt = f"""
Write a 1200-word SEO-optimized blog on "{seo_topic}".

RULES:
- NO markdown (*, #, **).
- Use ONLY:
  H1: Title
  H2: Section Title
  H3: Subsection Title
- Must contain line: "{extra_line}" in first 100 words.

Return EXACT structured output:

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
(full article using H1:, H2:, H3:)
"""

    with st.spinner("Generating SEO Article…"):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        raw = response.text.replace("*", "").replace("#", "")

        # Extract Sections
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

        # HTML Conversion
        content_html = sections["Full Blog Content"]

        # H1 Default Black
        content_html = re.sub(r"H1:\s*(.+)", r"<h1 style='color:black;'>\1</h1>", content_html)

        # H2 Red
        content_html = re.sub(r"H2:\s*(.+)", r"<h2 style='color:red;'>\1</h2>", content_html)

        # H3 Blue
        content_html = re.sub(r"H3:\s*(.+)", r"<h3 style='color:blue;'>\1</h3>", content_html)

        # External Links
        wiki_link = f"https://en.wikipedia.org/wiki/{seo_topic.replace(' ', '_')}"
        links_html = f"""
<br><br>
<h3 style='color:blue;'>External References</h3>
<p>My Website: <a href="{website_link}" target="_blank">{website_link}</a></p>
<p>Wikipedia: <a href="{wiki_link}" target="_blank">{wiki_link}</a></p>
"""
        content_html += links_html

        # -------------------------------------------------------
        # SEO ANALYZER
        # -------------------------------------------------------
        def analyze(text, keyphrase, title, desc):
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

            data["Meta Title Length"] = len(title)
            if len(title) > 60:
                score -= 5

            data["Meta Description Length"] = len(desc)
            if len(desc) > 160:
                score -= 5

            passive_hits = len(re.findall(r"\bwas\b|\bwere\b|\bbeen\b", text.lower()))
            passive_percent = (passive_hits / words) * 100 if words else 0
            data["Passive Voice %"] = round(passive_percent, 2)
            if passive_percent > 7:
                score -= 5

            sentences = re.split(r"[.!?]", text)
            s_lengths = [len(s.split()) for s in sentences if len(s.split())]
            avg_len = sum(s_lengths) / len(s_lengths) if s_lengths else 0
            data["Average Sentence Length"] = round(avg_len, 2)
            if avg_len > 22:
                score -= 5

            data["Final SEO Score"] = score
            return data

        seo_score = analyze(
            sections["Full Blog Content"],
            sections["Focus Keyphrase"],
            sections["Meta Title"],
            sections["Meta Description"]
        )

        # -------------------------------------------------------
        # SAVE POST
        # -------------------------------------------------------
        post_id = sections["Slug"] or sections["H1"] or seo_topic
        post_data = {
            "keyphrase": sections["Focus Keyphrase"],
            "slug": sections["Slug"],
            "meta_title": sections["Meta Title"],
            "meta_description": sections["Meta Description"],
            "h1": sections["H1"],
            "plain_content": sections["Full Blog Content"],
            "html_content": content_html,
            "seo_score": seo_score,
            "topic": seo_topic
        }

        save_post(post_id, post_data)

        # -------------------------------------------------------
        # DISPLAY RESULT
        # -------------------------------------------------------
        st.subheader("New SEO Article Generated")

        st.write("Focus Keyphrase:")
        copy_box(sections["Focus Keyphrase"], "Keyphrase")

        st.write("Slug:")
        copy_box(sections["Slug"], "Slug")

        st.write("Meta Title:")
        copy_box(sections["Meta Title"], "Meta Title")

        st.write("Meta Description:")
        copy_box(sections["Meta Description"], "Meta Description")

        st.write("H1:")
        st.markdown(f"<h1>{sections['H1']}</h1>", unsafe_allow_html=True)

        st.write("Full SEO Content:")
        st.markdown(content_html, unsafe_allow_html=True)

        st.subheader("SEO Score")
        for k, v in seo_score.items():
            st.write(f"{k}: {v}")
