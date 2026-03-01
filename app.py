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
    config['cookie']['expiry_days']
)

# 3. Create Tabs for Login and Register
tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

with tab2:
    try:
        # Call it with NO arguments at all. The library will use defaults.
        if authenticator.register_user():
            st.success('User registered successfully! You can now login.')
            # Save the new user to the YAML file
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(f"Registratio~n Error: {e}")

with tab1:
    authenticator.login(location='main')
    
    if st.session_state.get("authentication_status"):
        authenticator.logout('Logout', 'sidebar')
        name = st.session_state["name"]
        username = st.session_state["username"]
        st.write(f'Welcome *{name}*')
        st.title("🧬 GlycoTwin Live Patient Portal")
        
        # Use the logged-in username as the Patient ID
        PATIENT_ID = username 
        API_URL = "http://localhost:8000/chat"

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

    elif st.session_state.get("authentication_status") is False:
        st.error('Username/password is incorrect')
    elif st.session_state.get("authentication_status") is None:
        st.warning('Please enter your username and password')