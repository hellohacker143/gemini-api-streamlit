import streamlit as st
from google import genai
from fpdf import FPDF
import base64
from PIL import Image
import io
import PyPDF2

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
                
                # Display image text if exists
                if note.get("image_text"):
                    st.info(f"📝 Text from image: {note['image_text']}")
                
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
st.markdown("Generate topper-level exam answers with image support, text extraction, and syllabus upload.")

# ----------------------------------
# Syllabus Upload Section
# ----------------------------------
with st.expander("📚 Upload Syllabus (Optional)", expanded=False):
    syllabus_file = st.file_uploader("Upload syllabus PDF", type=["pdf"])
    if syllabus_file and api_key:
        if st.button("🔍 Extract Syllabus Content"):
            with st.spinner("Extracting syllabus..."):
                # Read PDF
                pdf_reader = PyPDF2.PdfReader(syllabus_file)
                syllabus_text = ""
                for page in pdf_reader.pages:
                    syllabus_text += page.extract_text()
                
                st.session_state.syllabus_content = syllabus_text
                st.success("✅ Syllabus extracted successfully!")
                st.text_area("Syllabus Content", syllabus_text, height=200)

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
    
    # Text input below image
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        st.session_state.uploaded_image = uploaded_file
        
        # Extract text from image
        if api_key and st.button("🔍 Extract Text from Image"):
            with st.spinner("Extracting text..."):
                client = genai.Client(api_key=api_key)
                uploaded_file.seek(0)
                image_bytes = uploaded_file.read()
                
                resp = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=[
                        {"image": {"data": base64.b64encode(image_bytes).decode('utf-8')}},
                        "Extract and return all text visible in this image. Return ONLY the extracted text, nothing else."
                    ]
                )
                st.session_state.image_text = resp.text
                st.success("✅ Text extracted!")
        
        # Show extracted text in text area
        if st.session_state.image_text:
            image_text_input = st.text_area("📝 Text below image:", value=st.session_state.image_text, height=150)
        else:
            image_text_input = st.text_area("📝 Add text below image (optional):", height=150)
    else:
        image_text_input = None
    
    # --- TEMPLATE: 3-marks preview ---
    preview_template = f"""
    Give a short 3-marks answer on the topic: {topic}
    with exam-oriented simple explanation.
    """
    
    # --- TEMPLATE: 5-marks answer ---
    context_info = ""
    if uploaded_file and image_text_input:
        context_info = f"\nImage context: {image_text_input}"
    if st.session_state.syllabus_content:
        context_info += f"\nSyllabus context: {st.session_state.syllabus_content[:500]}"
    
    marks_5_template = f"""
    Generate a perfect 5-marks university exam answer on the topic: "{topic}" in topper-writing style.
    {context_info}
    
    Use HTML headings like:
    <span style='color:red; text-decoration: underline;'><b>Heading</b></span>
    
    Structure:
    • Introduction (2-3 bullets)
    • Definition (clear)
    • 3 Key Points (numbered with brief explanation)
    • Conclusion
    """
    
    # --- TEMPLATE: 15-marks full answer ---
    if uploaded_file:
        full_template = f"""
        Based on the uploaded image{' and text: "' + image_text_input + '"' if image_text_input else ''} and the topic: "{topic}", generate a perfect 15-marks university exam answer in topper-writing style.
        {context_info}
        
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
        {context_info}
        
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
    col1, col2, col3 = st.columns(3)
    
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
    
    # Generate 5-marks Answer
    with col2:
        if st.button("📚 Generate 5-Marks Answer", use_container_width=True):
            if not api_key:
                st.error("⚠️ Please enter API Key")
            else:
                with st.spinner("Generating 5-marks answer..."):
                    client = genai.Client(api_key=api_key)
                    
                    # If image uploaded, include it
                    if uploaded_file:
                        uploaded_file.seek(0)
                        image_bytes = uploaded_file.read()
                        
                        resp = client.models.generate_content(
                            model="gemini-2.0-flash-exp",
                            contents=[
                                {"image": {"data": base64.b64encode(image_bytes).decode('utf-8')}},
                                marks_5_template
                            ]
                        )
                    else:
                        resp = client.models.generate_content(
                            model="gemini-2.0-flash-exp",
                            contents=marks_5_template
                        )
                    
                    marks_5_answer = resp.text
                    st.markdown("### 🟨 5-Marks Answer")
                    st.markdown(marks_5_answer, unsafe_allow_html=True)
                    
                    # Add to Book button
                    if st.button("📌 Add 5-Marks to Book", key="add_5"):
                        note_data = {
                            "topic": f"{topic} (5-Marks)",
                            "answer": marks_5_answer,
                            "plain_text": resp.text
                        }
                        
                        if uploaded_file:
                            uploaded_file.seek(0)
                            note_data["image"] = Image.open(uploaded_file)
                        if image_text_input:
                            note_data["image_text"] = image_text_input
                        
                        st.session_state.notes.append(note_data)
                        st.success("✅ Added to Notes Book!")
                        st.balloons()
                        st.rerun()
    
    # Generate Full 15 marks Answer
    with col3:
        if st.button("🏆 Generate 15-Marks Answer", use_container_width=True):
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
                    if st.button("📌 Add 15-Marks to Book", key="add_15"):
                        note_data = {
                            "topic": f"{topic} (15-Marks)",
                            "answer": full_answer,
                            "plain_text": resp.text
                        }
                        
                        # Add image if uploaded
                        if uploaded_file:
                            uploaded_file.seek(0)
                            note_data["image"] = Image.open(uploaded_file)
                        if image_text_input:
                            note_data["image_text"] = image_text_input
                        
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
