import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import requests

# 1. Load the Patient Database (the YAML file)
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# 2. Setup the Authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# 3. Render the Login UI
name, authentication_status, username = authenticator.login(location='main')

if authentication_status:
    # --- IF LOGIN SUCCESSFUL: SHOW THE CHAT ---
    authenticator.logout('Logout', 'sidebar')
    st.write(f'Welcome *{name}*')
    st.title("🧬 GlycoTwin Live Patient Portal")
    
    # Use the logged-in username as the Patient ID
    # This ensures John Smith's data doesn't mix with Sonali's data
    PATIENT_ID = username 
    API_URL = "http://localhost:8000/chat"

    # (Your existing Chat Logic here...)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Log your meal or symptom..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = requests.post(API_URL, params={"patient_id": PATIENT_ID, "message": prompt})
        if response.status_code == 200:
            res_data = response.json()
            full_response = res_data["glycotwin_response"].replace('\\n', '\n')
            with st.chat_message("assistant"):
                st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')