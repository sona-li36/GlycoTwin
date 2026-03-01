import streamlit as st
import requests

st.set_page_config(page_title="GlycoTwin Patient Portal", page_icon="🧬")

st.title("🧬 GlycoTwin AI Multi-Agent Portal")
st.markdown("---")

# Configuration
API_URL = "http://localhost:8000/chat"
PATIENT_ID = "a1111111-1111-1111-1111-111111111111"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How are you feeling today?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Send request to your FastAPI server
    try:
        response = requests.post(API_URL, params={"patient_id": PATIENT_ID, "message": prompt})
        if response.status_code == 200:
            res_data = response.json()
            full_response = res_data["glycotwin_response"].replace('\\n', '\n')
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        else:
            st.error("Server Error: Check if main.py is running.")
    except Exception as e:
        st.error(f"Connection Error: {e}")