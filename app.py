import streamlit as st
import requests
import time

# Your BypassGPT API key
API_KEY = "api_key_7283c200036946fa8a5af3cc016fc157"

GENERATE_URL = "https://api.bypassgpt.ai/generate"
RETRIEVE_URL = "https://api.bypassgpt.ai/retrieve"

st.title("BypassGPT Humanizer with Streamlit")

# User input text area
text = st.text_area("Enter AI-generated text to humanize:", height=200)

if st.button("Humanize Text"):
    if not text.strip():
        st.warning("Please enter some text to humanize.")
    else:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "language": "en",
            "bypass_mode": "standard"
        }

        # Step 1: Send text to generate humanization task
        response = requests.post(GENERATE_URL, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            task_id = data.get("task_id")

            if task_id:
                st.info("Processing... Please wait a moment.")

                # Polling to check if task is done
                for _ in range(10):
                    retrieve_response = requests.get(f"{RETRIEVE_URL}?task_id={task_id}", headers=headers)
                    if retrieve_response.status_code == 200:
                        result_data = retrieve_response.json()
                        humanized_text = result_data.get("humanized_text")
                        if humanized_text:
                            st.success("Humanized Text:")
                            st.write(humanized_text)
                            break
                        else:
                            time.sleep(2)
                    else:
                        st.error("Error retrieving humanized text.")
                        break
                else:
                    st.error("Timeout: Unable to retrieve humanized text. Try again later.")
            else:
                st.error("Failed to receive task ID from API.")
        else:
            st.error(f"API request failed with status code {response.status_code}.\nDetails: {response.text}")
