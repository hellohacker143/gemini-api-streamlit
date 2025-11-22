# ---------------------------------------------------
# ON-PAGE AI AGENT (CHAT PANEL)
# ---------------------------------------------------
st.markdown("---")
st.header("🤖 On-Page AI Agent")

agent_input = st.text_input(
    "Ask anything (AI Agent):",
    placeholder="Explain topic… Summarize… Create SEO keywords… Rewrite answer…"
)

agent_btn = st.button("💬 Ask Agent")

if agent_btn:
    if not api_key:
        st.error("Please enter your Gemini API key first!")
        st.stop()

    if not agent_input.strip():
        st.error("Please type something for the agent!")
        st.stop()

    with st.spinner("Agent thinking…"):
        try:
            agent_client = genai.Client(api_key=api_key)

            agent_response = agent_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=agent_input
            )

            st.subheader("🧠 Agent Response")
            st.markdown(agent_response.text)

            # Copy button for agent answer
            st.code(agent_response.text)
            st.button("📋 Copy Response", key=f"copy_agent")

        except Exception as e:
            st.error(f"Error: {e}")
