import streamlit as st
from google import genai
from fpdf import FPDF
import base64
from PIL import Image
import io
import PyPDF2

# ----------------------------------
st.set_page_config(
    page_title="15-Marks Answer Generator",
    page_icon="📝",
    layout="wide"
)

# ----------------------------------
# Initialize State
# ----------------------------------
if "notes" not in st.session_state:
    st.session_state.notes = []
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "image_text" not in st.session_state:
    st.session_state.image_text = None
if "syllabus_content" not in st.session_state:
    st.session_state.syllabus_content = None
if "subjects" not in st.session_state:
    st.session_state.subjects = {
        "Computer Networks (CN)": [
            "OSI Model", "TCP/IP Model", "Routing Algorithms", "Network Security",
            "Subnetting", "Switching Techniques", "Transport Layer",
            "IP Addressing", "Wireless Networks", "Application Layer Protocols"
        ],
        "Operating Systems (OS)": [
            "Process Synchronization", "Deadlocks", "CPU Scheduling",
            "Memory Management", "Paging and Segmentation", "File System",
            "Virtual Memory", "Threads & Multithreading", "Disk Scheduling",
            "System Calls"
        ],
        "Machine Learning (ML)": [
            "Linear Regression", "Logistic Regression", "Decision Trees",
            "K-Nearest Neighbors (KNN)", "Naive Bayes", "Support Vector Machines (SVM)",
            "Neural Networks", "K-Means Clustering", "Overfitting & Underfitting",
            "Train-Test Split"
        ]
    }

# ----------------------------------
# Sidebar
# ----------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("---")

    st.header("📖 Notes Book")
    st.write(f"Saved Notes: **{len(st.session_state.notes)}**")

    for i, note in enumerate(st.session_state.notes):
        with st.expander(f"📌 {note['topic']}"):
            if note.get("image"):
                st.image(note["image"], use_container_width=True)
            if note.get("image_text"):
                st.info(note["image_text"])
            st.markdown(note["answer"], unsafe_allow_html=True)
            if st.button(f"Delete {i+1}", key=f"del{i}"):
                st.session_state.notes.pop(i)
                st.rerun()

    if st.session_state.notes:
        if st.button("⬇️ Download Notes PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(True, margin=15)

            for note in st.session_state.notes:
                pdf.set_font("Arial", "B", 16)
                pdf.set_text_color(255, 0, 0)
                pdf.cell(0, 10, note["topic"], ln=True)

                pdf.set_font("Arial", size=12)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 8, note["plain_text"])
                pdf.ln(5)

            pdf.output("NotesBook.pdf")
            with open("NotesBook.pdf", "rb") as f:
                st.download_button("📥 Download", f, file_name="NotesBook.pdf")

# ----------------------------------
st.title("📝 15-Marks Answer Generator (HTML Styled)")
st.markdown("Generate topper-quality answers with clean HTML formatting.")

# ----------------------------------
# Syllabus Upload
# ----------------------------------
with st.expander("📚 Upload Syllabus PDF"):
    syllabus_file = st.file_uploader("Upload Syllabus PDF", type=["pdf"])
    if syllabus_file and api_key:
        if st.button("Extract PDF Text"):
            reader = PyPDF2.PdfReader(syllabus_file)
            text = "".join(page.extract_text() for page in reader.pages)
            st.session_state.syllabus_content = text
            st.text_area("Extracted Syllabus", text, height=200)

# ----------------------------------
# Subject
# ----------------------------------
st.subheader("📚 Select Subject")
selected_subject = st.selectbox("Choose Subject", list(st.session_state.subjects.keys()))

# ----------------------------------
# Add New Topic
# ----------------------------------
st.subheader("➕ Add Topic")
new_topic = st.text_input("New Topic")
if st.button("Add Topic") and new_topic.strip():
    st.session_state.subjects[selected_subject].append(new_topic)
    st.success("Topic Added!")
    st.rerun()

# ----------------------------------
# Topic Search + Display
# ----------------------------------
st.subheader("🔥 Topics")
search = st.text_input("Search Topic")
all_topics = st.session_state.subjects[selected_subject]
filtered = [t for t in all_topics if search.lower() in t.lower()] if search else all_topics

cols = st.columns(3)
for i, topic in enumerate(filtered):
    with cols[i % 3]:
        if st.button(topic):
            st.session_state.selected_topic = topic

# ----------------------------------
# Generate Answers
# ----------------------------------
if st.session_state.selected_topic:
    topic = st.session_state.selected_topic

    st.markdown(f"### 📝 Topic Selected: **{topic}**")

    # Image upload
    st.markdown("#### 📷 Upload Image (Optional)")
    uploaded_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg","gif","bmp","tiff","webp","svg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        st.session_state.uploaded_image = uploaded_file

        if api_key and st.button("Extract Image Text"):
            client = genai.Client(api_key=api_key)
            uploaded_file.seek(0)
            img_bytes = uploaded_file.read()

            resp = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=[
                    {"image": {"data": base64.b64encode(img_bytes).decode()}},
                    "Extract all text from this image. Return only text."
                ]
            )
            st.session_state.image_text = resp.text

    img_text = st.session_state.image_text or ""

    # Templates
    preview_template = f"Short 3-marks answer on {topic}."
    context = ""
    if img_text:
        context += f"Image text: {img_text}\n"
    if st.session_state.syllabus_content:
        context += f"Syllabus: {st.session_state.syllabus_content[:500]}"

    marks_5_template = f"Generate 5-marks answer on {topic}. {context}"
    full_template = f"Generate 15-marks HTML styled answer on {topic}. {context} Use <span style='color:red;text-decoration:underline'><b>Heading</b></span> format."

    col1, col2, col3 = st.columns(3)

    # 3 Marks
    with col1:
        if st.button("Generate 3-Marks"):
            client = genai.Client(api_key=api_key)
            resp = client.models.generate_content(model="gemini-2.0-flash", contents=preview_template)
            st.markdown(resp.text)

    # 5 Marks
    with col2:
        if st.button("Generate 5-Marks"):
            client = genai.Client(api_key=api_key)
            resp = client.models.generate_content(model="gemini-2.0-flash", contents=marks_5_template)
            st.markdown(resp.text, unsafe_allow_html=True)

            if st.button("Save 5-Marks Note"):
                st.session_state.notes.append({"topic": topic+" (5)", "answer": resp.text, "plain_text": resp.text, "image_text": img_text})
                st.success("Saved!")
                st.rerun()

    # 15 Marks
    with col3:
        if st.button("Generate 15-Marks"):
            client = genai.Client(api_key=api_key)
            resp = client.models.generate_content(model="gemini-2.0-flash", contents=full_template)
            st.markdown(resp.text, unsafe_allow_html=True)

            if st.button("Save 15-Marks Note"):
                st.session_state.notes.append({"topic": topic+" (15)", "answer": resp.text, "plain_text": resp.text, "image_text": img_text})
                st.success("Saved!")
                st.rerun()

# Reset
if st.button("Reset All"):
    st.session_state.clear()
    st.rerun()
