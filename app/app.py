import streamlit as st
import requests

# FastAPI Backend URL
API_URL = "http://127.0.0.1:8000"  # Update if deployed

# Set Page Config
st.set_page_config(page_title="AI Document Intelligence Hub", layout="centered")

# Initialize session state
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Function to Register
def register_user(username, email, password, role):
    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "base_role": role
    }
    try:
        response = requests.post(f"{API_URL}/user_create", json=user_data)
        if response.status_code == 200:
            st.success("Registration successful! Please log in.")
            st.session_state.auth_mode = "login"
            st.rerun()
        else:
            st.error(f"{response.json().get('detail', 'Registration failed!')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")

# Function to Login User
def login_user(username, password):
    try:
        response = requests.post(
            f"{API_URL}/login_token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data.get("access_token")
            st.session_state.authenticated = True
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Invalid username or password!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")

# Function to Get Current User
def get_current_user():
    if not st.session_state.access_token:
        st.error("No access token found. Please log in.")
        return None
    
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.get(f"{API_URL}/users/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch user info: {response.status_code} - {response.text}")
            st.session_state.access_token = None
            st.session_state.authenticated = False
            st.rerun()
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None

# Function to Logout User
def logout_user():
    st.session_state.access_token = None
    st.session_state.authenticated = False
    st.success("Logged out successfully!")
    st.rerun()

# Function to Upload File
def upload_file(uploaded_file, question, access_token):
    if not access_token:
        st.error("No access token found. Please log in again.")
        return None

    headers = {"Authorization": f"Bearer {access_token}"}
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    data = {"question": question}

    try:
        response = requests.post(f"{API_URL}/upload/", files=files, data=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            st.success("File uploaded successfully!")
            return result
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            st.error(f"Upload failed: {error_msg}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None

# UI Layout
def main_app():
    st.markdown(
        """
        <h1 style='text-align: center; font-size: 2.5rem;'>AI-Powered Document Intelligence Hub</h1>
        <p style='text-align: center; font-size: 1.1rem; color: gray;'>
        Upload documents (PDFs, images, audio files, etc.), ask questions, search for information, and get AI-generated insights.
        </p>
        <hr style="border: 0.5px solid gray;">
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Check authentication status
    if st.session_state.access_token and st.session_state.authenticated:
        user_info = get_current_user()
        
        if user_info:  # Only proceed if user_info is valid
            st.write(f"Welcome, **{user_info['username']}**! ")
            
            # Logout Button
            if st.button("Logout", use_container_width=True):
                logout_user()
        
            # Upload Section (only shown if authenticated)
            st.markdown("### Upload a Document")

            uploaded_file = st.file_uploader(
                "Choose a document (PDF, Image, Audio)", 
                type=["pdf", "png", "jpg", "jpeg", "mp3", "wav"]
            )

            if uploaded_file:
                question = st.text_input("Ask a question related to the document:")
                
                if st.button("Upload & Process", use_container_width=True):
                    result = upload_file(uploaded_file, question, st.session_state.access_token)
                    if result:
                        st.write(f"**AI-Generated Answer:** {result.get('generated_answer', 'No answer provided.')}")
        else:
            # If user_info is None, redirect to login
            st.session_state.auth_mode = "login"
            st.session_state.authenticated = False
            st.rerun()
    else:
        # Authentication UI
        if st.session_state.auth_mode == "login":
            st.markdown("### 🔑 Login")

            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")

            if st.button("Sign In", use_container_width=True):
                login_user(username, password)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Go to Sign Up", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()

        elif st.session_state.auth_mode == "signup":
            st.markdown("### Create an Account")

            new_username = st.text_input("👤 Username", placeholder="Choose a username")
            new_email = st.text_input("Email", placeholder="Enter your email")
            new_password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
            user_role = st.selectbox("🛠️ Select Role", ["lawyer", "student", "enterprise", "banker"])

            if st.button("Register", use_container_width=True):
                register_user(new_username, new_email, new_password, user_role)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Go to Login", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

# Run the app
if __name__ == "__main__":
    main_app()