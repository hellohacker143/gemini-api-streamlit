import streamlit as st
from google import genai
from fpdf import FPDF
import base64
from PIL import Image
import io

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

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

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
    
    if st.session_state.notes:
        for i, note in enumerate(st.session_state.notes):
            with st.expander(f"📌 {note['topic']}", expanded=False):
                # Display image if exists
                if note.get("image"):
                    st.image(note["image"], caption=f"Image for {note['topic']}", use_container_width=True)
                
                # Display answer
                st.markdown(note["answer"], unsafe_allow_html=True)
                
                # Delete button
                if st.button(f"🗑️ Delete Note {i+1}", key=f"del_{i}"):
                    st.session_state.notes.pop(i)
                    st.rerun()
    else:
        st.info("No notes saved yet. Generate answers and add them to your book!")
    
    st.markdown("---")
    
    # PDF Download Button
    if st.session_state.notes:
        if st.button("⬇️ Download Notes as PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
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
                st.download_button("📥 Download PDF", file, file_name="NotesBook.pdf")

# ----------------------------------
# Title
# ----------------------------------
st.title("📝 15-Marks Exam Answer Generator")
st.markdown("Generate topper-level exam answers with styled headings, image support, and notes saving.")

# ----------------------------------
# Subject Dropdown
# ----------------------------------
st.subheader("📚 Select Subject")
selected_subject = st.selectbox("Choose Subject:", list(st.session_state.subjects.keys()))

# ----------------------------------
# Add New Topic Section
# ----------------------------------
st.subheader("➕ Add New Topic")
col1, col2 = st.columns([3, 1])
with col1:
    new_topic = st.text_input("Enter a new topic:")
with col2:
    st.write("")
    st.write("")
    if st.button("Add Topic", use_container_width=True):
        if new_topic.strip():
            st.session_state.subjects[selected_subject].append(new_topic.strip())
            st.success(f"✅ Topic '{new_topic}' added")
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
        if st.button(topic, use_container_width=True):
            st.session_state.selected_topic = topic

# ----------------------------------
# Answer Generation Section
# ----------------------------------
if st.session_state.selected_topic:
    topic = st.session_state.selected_topic
    st.markdown("---")
    st.subheader(f"📝 Selected Topic: **{topic}**")
    
    # Image Upload Section
    st.markdown("#### 📷 Upload Image (Optional)")
    uploaded_file = st.file_uploader("Upload an image related to the topic", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        st.session_state.uploaded_image = uploaded_file
    
    # --- TEMPLATE: 3-marks preview ---
    preview_template = f"""
    Give a short 3-marks answer on the topic: {topic}
    with exam-oriented simple explanation.
    """
    
    # --- TEMPLATE: 15-marks full answer ---
    if uploaded_file:
        full_template = f"""
        Based on the uploaded image and the topic: "{topic}", generate a perfect 15-marks university exam answer in topper-writing style.
        
        Analyze the image first, then create a comprehensive answer.
        
        Use HTML headings like:
        <span style='color:red; text-decoration: underline;'><b>Heading</b></span>
        
        Structure:
        • Introduction (4-5 bullets)
        • Definition (clear explanation)
        • Image Analysis (describe what's shown)
        • 6 Key Points (numbered + detailed explanation)
        • Features
        • Advantages
        • Characteristics
        • Applications
        • Conclusion
        """
    else:
        full_template = f"""
        Generate a perfect 15-marks university exam answer on the topic: "{topic}" in topper-writing style.
        
        Use HTML headings like:
        <span style='color:red; text-decoration: underline;'><b>Heading</b></span>
        
        Structure:
        • Introduction (4-5 bullets)
        • Definition (clear explanation)
        • Neat Diagram (describe in text)
        • 6 Key Points (numbered + detailed explanation)
        • Features
        • Advantages
        • Characteristics
        • Applications
        • Conclusion
        """
    
    # Generate Preview (3 marks)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ Generate 3-Marks Preview", use_container_width=True):
            if not api_key:
                st.error("⚠️ Please enter API Key")
            else:
                with st.spinner("Generating preview..."):
                    client = genai.Client(api_key=api_key)
                    resp = client.models.generate_content(
                        model="gemini-2.0-flash-exp",
                        contents=preview_template
                    )
                    preview_answer = resp.text
                    st.markdown("### 🟩 3-Marks Preview")
                    st.write(preview_answer)
    
    # Generate Full 15 marks Answer
    with col2:
        if st.button("🏆 Generate Full 15-Marks Answer", use_container_width=True):
            if not api_key:
                st.error("⚠️ Enter Gemini API Key!")
            else:
                with st.spinner("Generating full answer..."):
                    client = genai.Client(api_key=api_key)
                    
                    # If image uploaded, include it in the API call
                    if uploaded_file:
                        uploaded_file.seek(0)
                        image_bytes = uploaded_file.read()
                        
                        resp = client.models.generate_content(
                            model="gemini-2.0-flash-exp",
                            contents=[
                                {"image": {"data": base64.b64encode(image_bytes).decode('utf-8')}},
                                full_template
                            ]
                        )
                    else:
                        resp = client.models.generate_content(
                            model="gemini-2.0-flash-exp",
                            contents=full_template
                        )
                    
                    full_answer = resp.text
                    st.markdown("### 🟥 15-Marks Answer")
                    st.markdown(full_answer, unsafe_allow_html=True)
                    
                    # Add to Book button
                    if st.button("📌 Add to Notes Book"):
                        note_data = {
                            "topic": topic,
                            "answer": full_answer,
                            "plain_text": resp.text
                        }
                        
                        # Add image if uploaded
                        if uploaded_file:
                            uploaded_file.seek(0)
                            note_data["image"] = Image.open(uploaded_file)
                        
                        st.session_state.notes.append(note_data)
                        st.success("✅ Added to Notes Book!")
                        st.balloons()
                        st.rerun()

# ----------------------------------
# Reset Button
# ----------------------------------
st.markdown("---")
if st.button("🔄 Reset All"):
    st.session_state.clear()
    st.rerun()
