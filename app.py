import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import requests

# 1. Load the Patient Database
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# 2. Setup the Authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# 3. Create Tabs for Login and Register
tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

with tab2:
    try:
        if authenticator.register_user('Register User', preauthorization=False):
            st.success('User registered successfully! You can now login.')
            # Save the new user to the YAML file immediately
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)

with tab1:
    name, authentication_status, username = authenticator.login('Login', 'main')

    if authentication_status:
        authenticator.logout('Logout', 'sidebar')
        st.title(f"🧬 Welcome, {name}")
        
        # Patient ID is now tied to the logged-in username
        PATIENT_ID = username 
        API_URL = "http://localhost:8000/chat"

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("How are you feeling today?"):
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
        st.warning('Please enter your username and password')s