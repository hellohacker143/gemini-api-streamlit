import streamlit as st
from google import genai

# -------------------------
#  Page Configuration
# -------------------------
st.set_page_config(
    page_title="15-Marks Answer Generator",
    page_icon="📝",
    layout="centered"
)

st.title("📝 15-Marks Exam Answer Generator")
st.markdown("Generate topper-quality university exam answers using Gemini AI with styled headings.")

# -------------------------
#  Sidebar – API Key
# -------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("---")
    st.caption("Get API Key → https://aistudio.google.com/apikey")

# -------------------------
#  Subject Topics
# -------------------------
subjects = {
    "Computer Networks (CN)": [
        "OSI Model", "TCP/IP Model", "Routing Algorithms", "Network Security",
        "Subnetting", "Switching Techniques", "Transport Layer", "IP Addressing",
        "Wireless Networks", "Application Layer Protocols"
    ],
    "Operating Systems (OS)": [
        "Process Synchronization", "Deadlocks", "CPU Scheduling", "Memory Management",
        "Paging and Segmentation", "File System", "Virtual Memory",
        "Threads & Multithreading", "Disk Scheduling", "System Calls"
    ],
    "Machine Learning (ML)": [
        "Linear Regression", "Logistic Regression", "Decision Trees",
        "K-Nearest Neighbors (KNN)", "Naive Bayes", "Support Vector Machines (SVM)",
        "Neural Networks", "K-Means Clustering", "Overfitting & Underfitting",
        "Train-Test Split"
    ]
}

# -------------------------
#  NEW Prompt Template (Red + Underline Headings)
# -------------------------
exam_template = """
Generate a perfect 15-marks university exam answer on the topic: “{TOPIC}” in topper-writing style.

Formatting Rules (VERY IMPORTANT):
• Every heading must be RED and UNDERLINED.
• Use EXACT HTML style:
  <span style='color:red; text-decoration: underline;'><b>HEADING HERE</b></span>

Structure:

<span style='color:red; text-decoration: underline;'><b>Introduction</b></span>
(4–5 bullet points)

<span style='color:red; text-decoration: underline;'><b>Definition</b></span>
(4–5 bullet points)

<span style='color:red; text-decoration: underline;'><b>Neat Diagram</b></span>
(Text-based block diagram)

Now list 6 key points using numbers.
For each key point:
1. Use this heading format:
   <span style='color:red; text-decoration: underline;'><b>Heading</b></span>
2. Give 2–3 line explanation.

<span style='color:red; text-decoration: underline;'><b>Features</b></span>
(4–5 bullet points)

<span style='color:red; text-decoration: underline;'><b>Advantages</b></span>
(4–5 bullet points)

<span style='color:red; text-decoration: underline;'><b>Characteristics</b></span>
(4–5 bullet points)

<span style='color:red; text-decoration: underline;'><b>Applications</b></span>
Real-world uses

<span style='color:red; text-decoration: underline;'><b>Conclusion</b></span>
Write a strong, exam-oriented final paragraph with a proper ending.

Write clean, structured, and exam-ready content. 
Do NOT mention number of lines.
"""

# -------------------------
#  SUBJECT DROPDOWN
# -------------------------
st.subheader("📚 Select Subject")
selected_subject = st.selectbox("Choose a subject:", list(subjects.keys()))

if selected_subject:
    st.success(f"Showing trending topics for **{selected_subject}**")

    trending = subjects[selected_subject]

    # -------------------------
    #  Search Bar
    # -------------------------
    st.subheader("🔍 Search Topic")
    search_query = st.text_input("Search topics...")

    # Filter search results
    if search_query:
        filtered_topics = [t for t in trending if search_query.lower() in t.lower()]
    else:
        filtered_topics = trending

    # -------------------------
    #  Trending Topics Grid (3 per row)
    # -------------------------
    st.subheader("🔥 Trending Topics")

    cols = st.columns(3)
    i = 0
    for topic in filtered_topics:
        with cols[i % 3]:
            if st.button(topic):
                st.session_state["selected_topic"] = topic
        i += 1

    # -------------------------
    #  Suggested Topics
    # -------------------------
    st.subheader("💡 Suggested Topics")
    suggestions = filtered_topics[:5]
    st.write(", ".join(suggestions))

# -------------------------
#  GENERATE ANSWER SECTION
# -------------------------
if "selected_topic" in st.session_state:
    selected_topic = st.session_state["selected_topic"]
    st.subheader(f"📝 Generate Answer for: **{selected_topic}**")

    if st.button("Generate 15-Marks Answer"):
        if not api_key:
            st.error("Please enter your Gemini API Key!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                final_prompt = exam_template.replace("{TOPIC}", selected_topic)

                with st.spinner("Generating topper-quality answer..."):
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=final_prompt
                    )

                answer = response.text
                st.success("Answer generated successfully!")

                # ALLOW HTML RENDERING FOR RED UNDERLINED HEADINGS
                st.markdown(answer, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {str(e)}")

# -------------------------
# Clear Selection
# -------------------------
if st.button("🔄 Reset"):
    st.session_state.clear()
    st.rerun()
