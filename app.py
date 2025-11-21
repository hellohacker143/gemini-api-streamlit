import streamlit as st
from google import genai
from fpdf import FPDF

# ----------------------------------
# Page Configuration
# ----------------------------------
st.set_page_config(
    page_title="15-Marks Answer Generator",
    page_icon="📝",
    layout="wide"
)

# ----------------------------------
# Session State Initialization
# ----------------------------------
if "notes" not in st.session_state:
    st.session_state.notes = []

if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None

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
# Sidebar – API Key + Notes Book
# ----------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("---")

    st.header("📖 Notes Book")
    st.write(f"Total Saved Notes: **{len(st.session_state.notes)}**")

    for i, note in enumerate(st.session_state.notes):
        with st.expander(f"📌 {note['topic']}"):
            st.markdown(note["answer"], unsafe_allow_html=True)
            if st.button(f"Delete Note {i+1}", key=f"del_{i}"):
                st.session_state.notes.pop(i)
                st.rerun()

    st.markdown("---")

    # PDF Download Button
    if st.session_state.notes:
        if st.button("⬇️ Download Notes as PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            # HTML-styled headings → simulate red underline
            for note in st.session_state.notes:
                pdf.set_font("Arial", "B", 16)
                pdf.set_text_color(255, 0, 0)
                pdf.cell(0, 10, note["topic"], ln=True)

                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 8, note["plain_text"])
                pdf.ln(5)

            pdf.output("NotesBook.pdf")
            with open("NotesBook.pdf", "rb") as file:
                st.download_button("Download PDF", file, file_name="NotesBook.pdf")

# ----------------------------------
# Title
# ----------------------------------
st.title("📝 15-Marks Exam Answer Generator")
st.markdown("Generate topper-level exam answers with styled headings and notes saving.")

# ----------------------------------
# Subject Dropdown
# ----------------------------------
st.subheader("📚 Select Subject")
selected_subject = st.selectbox("Choose Subject:", list(st.session_state.subjects.keys()))

# ----------------------------------
# Add New Topic Section
# ----------------------------------
st.subheader("➕ Add New Topic")
new_topic = st.text_input("Enter a new topic:")
if st.button("Add Topic"):
    if new_topic.strip():
        st.session_state.subjects[selected_subject].append(new_topic.strip())
        st.success(f"Topic '{new_topic}' added under {selected_subject}")
        st.rerun()

# ----------------------------------
# Search Topic
# ----------------------------------
st.subheader("🔍 Search Topic")
search_query = st.text_input("Search topics...")

trending = st.session_state.subjects[selected_subject]
filtered_topics = [t for t in trending if search_query.lower() in t.lower()] if search_query else trending

# ----------------------------------
# Display Topics (Grid)
# ----------------------------------
st.subheader("🔥 Topics")
cols = st.columns(3)
for i, topic in enumerate(filtered_topics):
    with cols[i % 3]:
        if st.button(topic):
            st.session_state.selected_topic = topic

# ----------------------------------
# Answer Generation Section
# ----------------------------------
if st.session_state.selected_topic:
    topic = st.session_state.selected_topic
    st.subheader(f"📝 Selected Topic: **{topic}**")

    # --- TEMPLATE: 3-marks preview ---
    preview_template = f"""
    Give a short 3-marks answer on the topic: {topic}
    with exam-oriented simple explanation.
    """

    # --- TEMPLATE: 15-marks full answer ---
    full_template = """
    Generate a perfect 15-marks university exam answer on the topic: “{TOPIC}” in topper-writing style.

    Use HTML headings like:
    <span style='color:red; text-decoration: underline;'><b>Heading</b></span>

    Structure:
    • Introduction (bullets)
    • Definition (bullets)
    • Neat Diagram (text)
    • 6 Key Points (numbered + explanation)
    • Features
    • Advantages
    • Characteristics
    • Applications
    • Conclusion
    """.replace("{TOPIC}", topic)

    # Generate Preview (3 marks)
    if st.button("✨ Generate 3-Marks Preview"):
        if not api_key:
            st.error("Please enter API Key")
        else:
            client = genai.Client(api_key=api_key)
            resp = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=preview_template
            )
            preview_answer = resp.text
            st.markdown("### 🟩 3-Marks Preview")
            st.write(preview_answer)

    # Generate Full 15 marks Answer
    if st.button("🏆 Generate Full 15-Marks Answer"):
        if not api_key:
            st.error("Enter Gemini API Key!")
        else:
            client = genai.Client(api_key=api_key)
            resp = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_template
            )
            full_answer = resp.text

            st.markdown("### 🟥 15-Marks Answer")
            st.markdown(full_answer, unsafe_allow_html=True)

            # Save plain text for PDF
            plain = st.session_state.get("plain_text", "")

            # Add to Book button
            if st.button("📌 Add to Book"):
                st.session_state.notes.append({
                    "topic": topic,
                    "answer": full_answer,
                    "plain_text": resp.text
                })
                st.success("Added to Notes Book!")
                st.rerun()

# ----------------------------------
# Reset Button
# ----------------------------------
if st.button("🔄 Reset All"):
    st.session_state.clear()
    st.rerun()
