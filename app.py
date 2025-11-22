
# ---------------------------------------------------
# ON-PAGE AI AGENT (CHAT PANEL)
# ---------------------------------------------------
st.markdown("---")
st.header("🤖 On-Page AI Agent")

agent_query = st.text_input(
    "Ask anything (AI Agent):",
    placeholder="Ask doubts, generate summary, rewrite content, SEO keywords..."
)

agent_submit = st.button("💬 Ask Agent")

if agent_submit:
    if not api_key:
        st.error("❌ Please enter your API key first in the sidebar!")
    elif not agent_query.strip():
        st.error("❌ Please type something to ask!")
    else:
        with st.spinner("Thinking..."):
            try:
                agent_client = genai.Client(api_key=api_key)
                agent_response = agent_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=agent_query
                )

                reply = agent_response.text

                st.subheader("🧠 Agent Response")
                st.markdown(reply)

                st.code(reply)
                st.button("📋 Copy Response", key="copy_agent_reply")

            except Exception as e:
                st.error(f"Error: {e}")
