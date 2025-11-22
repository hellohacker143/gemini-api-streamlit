import streamlit as st
from google import genai
import re
import json
import os

# -------------------------------------------------------
# PAGE SETUP
# -------------------------------------------------------
st.set_page_config(page_title="SEO Generator + Humanize Mode", page_icon="📝", layout="wide")
st.title("SEO Blog Generator + Analyzer + Saved Articles + Humanize Mode")


# -------------------------------------------------------
# SAFE STORAGE PATH
# -------------------------------------------------------
SAVE_FOLDER = "saved_data"
SAVE_FILE = f"{SAVE_FOLDER}/saved_posts.json"

os.makedirs(SAVE_FOLDER, exist_ok=True)

if not os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "w") as f:
        json.dump({}, f)


# -------------------------------------------------------
# JSON LOAD / SAVE
# -------------------------------------------------------
def load_saved_posts():
    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


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
# SIDEBAR SETTINGS
# -------------------------------------------------------
with st.sidebar:
    st.header("Settings")

    # Your bypass GPT API key
    api_key = st.text_input("Enter Gemini API Key", value="api_key_7283c200036946fa8a5af3cc016fc157", type="password")

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
# LOAD OLD POST
# -------------------------------------------------------
if selected_post != "None":
    post = saved_posts[selected_post]

    st.subheader(f"Loaded Old SEO Article")

    st.write("Focus Keyphrase:")
    copy_box(post["keyphrase"], "Keyphrase")

    st.write("Slug:")
    copy_box(post["slug"], "Slug")

    st.write("Meta Title:")
    copy_box(post["meta_title"], "Meta Title")

    st.write("Meta Description:")
    copy_box(post["meta_description"], "Meta Description")

    st.write("Summary:")
    copy_box(post["summary"], "Summary")
    st.markdown(f"<p>{post['summary']}</p>", unsafe_allow_html=True)

    st.write("Conclusion:")
    copy_box(post["conclusion"], "Conclusion")
    st.markdown(f"<p>{post['conclusion']}</p>", unsafe_allow_html=True)

    st.write("H1:")
    st.markdown(f"<h1>{post['h1']}</h1>", unsafe_allow_html=True)

    st.write("Full Article:")
    st.markdown(post["html_content"], unsafe_allow_html=True)

    st.subheader("SEO Score:")
    for k, v in post["seo_score"].items():
        st.write(f"{k}: {v}")

    st.stop()


# -------------------------------------------------------
# SEO GENERATOR INPUTS
# -------------------------------------------------------
seo_topic = st.text_input("Enter Blog Topic:")
extra_line = st.text_input("Required line inside first 100 words:")
generate = st.button("Generate SEO Article")


# -------------------------------------------------------
# GENERATE NEW ARTICLE
# -------------------------------------------------------
if generate and api_key and seo_topic:

    client = genai.Client(api_key=api_key)

    prompt = f"""
Write a 1200-word SEO blog on: "{seo_topic}"

RULES:
- NO markdown (*, #, **)
- Use ONLY:
  H1: Title
  H2: Section
  H3: Subsection
- Must include this line in first 100 words:
  "{extra_line}"

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

Summary:
(short summary)

Conclusion:
(short conclusion)

Full Blog Content:
(full article using H1:, H2:, H3:)
"""

    with st.spinner("Generating Article…"):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        raw = response.text.replace("*", "").replace("#", "")

        # Extract Sections
        parts = {
            "Focus Keyphrase": "",
            "Slug": "",
            "Meta Title": "",
            "Meta Description": "",
            "H1": "",
            "Summary": "",
            "Conclusion": "",
            "Full Blog Content": ""
        }

        for key in parts.keys():
            marker = f"{key}:"
            if marker in raw:
                try:
                    next_marker = next(
                        x for x in parts.keys() if x != key and f"{x}:" in raw.split(marker)[1]
                    )
                    parts[key] = raw.split(marker)[1].split(f"{next_marker}:")[0].strip()
                except StopIteration:
                    parts[key] = raw.split(marker)[1].strip()

        # Convert to HTML
        html_content = parts["Full Blog Content"]
        html_content = re.sub(r"H1:\s*(.+)", r"<h1 style='color:black;'>\1</h1>", html_content)
        html_content = re.sub(r"H2:\s*(.+)", r"<h2 style='color:red;'>\1</h2>", html_content)
        html_content = re.sub(r"H3:\s*(.+)", r"<h3 style='color:blue;'>\1</h3>", html_content)

        # -------------------------------------------------------
        # SEO ANALYZER
        # -------------------------------------------------------
        def analyzer(text, keyphrase, title, desc):
            score = 100
            d = {}

            words = len(text.split())
            d["Word Count"] = words
            if words < 900:
                score -= 10

            kd = (text.lower().count(keyphrase.lower()) / words) * 100 if words else 0
            d["Keyword Density %"] = round(kd, 2)
            if kd < 0.8 or kd > 3.5:
                score -= 5

            d["Meta Title Length"] = len(title)
            if len(title) > 60:
                score -= 5

            d["Meta Description Length"] = len(desc)
            if len(desc) > 160:
                score -= 5

            passive = len(re.findall(r"\bwas\b|\bwere\b|\bbeen\b", text.lower()))
            pv_percent = (passive / words) * 100 if words else 0
            d["Passive Voice %"] = round(pv_percent, 2)
            if pv_percent > 7:
                score -= 5

            sentences = re.split(r"[.!?]", text)
            lens = [len(s.split()) for s in sentences if len(s.split())]
            avg_len = sum(lens) / len(lens) if lens else 0
            d["Average Sentence Length"] = round(avg_len, 2)
            if avg_len > 22:
                score -= 5

            d["Final SEO Score"] = score
            return d

        seo_score = analyzer(
            parts["Full Blog Content"],
            parts["Focus Keyphrase"],
            parts["Meta Title"],
            parts["Meta Description"]
        )

        # -------------------------------------------------------
        # SAVE POST
        # -------------------------------------------------------
        post_id = parts["Slug"] or parts["H1"] or seo_topic

        save_post(post_id, {
            "keyphrase": parts["Focus Keyphrase"],
            "slug": parts["Slug"],
            "meta_title": parts["Meta Title"],
            "meta_description": parts["Meta Description"],
            "h1": parts["H1"],
            "summary": parts["Summary"],
            "conclusion": parts["Conclusion"],
            "plain_content": parts["Full Blog Content"],
            "html_content": html_content,
            "seo_score": seo_score,
            "topic": seo_topic
        })

        # -------------------------------------------------------
        # DISPLAY NEW ARTICLE (NO NEW TAB LINK)
        # -------------------------------------------------------
        st.subheader("Generated SEO Article")

        st.write("Focus Keyphrase:")
        copy_box(parts["Focus Keyphrase"], "Keyphrase")

        st.write("Slug:")
        copy_box(parts["Slug"], "Slug")

        st.write("Meta Title:")
        copy_box(parts["Meta Title"], "Meta Title")

        st.write("Meta Description:")
        copy_box(parts["Meta Description"], "Meta Description")

        st.write("Summary:")
        copy_box(parts["Summary"], "Summary")
        st.markdown(f"<p>{parts['Summary']}</p>", unsafe_allow_html=True)

        st.write("Conclusion:")
        copy_box(parts["Conclusion"], "Conclusion")
        st.markdown(f"<p>{parts['Conclusion']}</p>", unsafe_allow_html=True)

        st.write("H1:")
        st.markdown(f"<h1>{parts['H1']}</h1>", unsafe_allow_html=True)

        st.write("Full Blog Content:")
        st.markdown(html_content, unsafe_allow_html=True)

        st.subheader("SEO Score:")
        for k, v in seo_score.items():
            st.write(f"{k}: {v}")

        # -------------------------------------------------------
        # HUMANIZE BUTTON
        # -------------------------------------------------------
        st.write("---")
        st.subheader("Humanize / Bypass GPT Detection")

        if st.button("Humanize Content"):
            with st.spinner("Humanizing content…"):
                human_prompt = f"""
Rewrite the following article in a fully human, natural, undetectable style.
Remove all AI patterns and make it sound like written by a real content writer.
Keep same H1, H2, H3 structure.

CONTENT:
{parts['Full Blog Content']}
"""

                human_response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=human_prompt
                )

                human_text = human_response.text.replace("*", "").replace("#", "")

                # Update HTML
                human_html = re.sub(r"H1:\s*(.+)", r"<h1 style='color:black;'>\1</h1>", human_text)
                human_html = re.sub(r"H2:\s*(.+)", r"<h2 style='color:red;'>\1</h2>", human_text)
                human_html = re.sub(r"H3:\s*(.+)", r"<h3 style='color:blue;'>\1</h3>", human_text)

                st.subheader("Humanized Content")
                st.markdown(human_html, unsafe_allow_html=True)

                # Overwrite saved content
                save_post(post_id, {
                    "keyphrase": parts["Focus Keyphrase"],
                    "slug": parts["Slug"],
                    "meta_title": parts["Meta Title"],
                    "meta_description": parts["Meta Description"],
                    "h1": parts["H1"],
                    "summary": parts["Summary"],
                    "conclusion": parts["Conclusion"],
                    "plain_content": human_text,
                    "html_content": human_html,
                    "seo_score": seo_score,
                    "topic": seo_topic
                })
