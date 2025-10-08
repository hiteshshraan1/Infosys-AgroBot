import streamlit as st
from utils.auth_utils import login, signup

st.set_page_config(page_title="AgroScribe", page_icon="🌾", layout="wide")

def hide_pages(page_names_to_hide: list[str]):
    """Injects CSS to hide sidebar pages."""
    hide_css = "<style>"
    for page_name in page_names_to_hide:
        hide_css += f"""
            div[data-testid="stSidebarNav"] ul li a[href*="{page_name}"] {{
                display: none;
            }}
        """
    hide_css += "</style>"
    st.markdown(hide_css, unsafe_allow_html=True)


is_logged_in = "username" in st.session_state

if not is_logged_in:
    hide_pages(["farmer_dashboard", "admin_dashboard"])
    st.title("🌾 AgroScribe Portal")
else:
    role = st.session_state.get("role")
    st.title(f"🌾 Welcome, {st.session_state['username']}!")

    if role == "Farmer":
        hide_pages(["admin_dashboard"])


if not is_logged_in:
    menu = st.sidebar.selectbox("Select Option", ["Login", "Signup"], key="auth_menu")
    
    if menu == "Signup":
        st.subheader("Create an Account")
        username = st.text_input("Enter Username")
        password = st.text_input("Enter Password", type="password")
        role = st.selectbox("Select Role", ["Farmer", "Admin"])

        if st.button("Create Account"):
            if username and password:
                success, msg = signup(username, password, role)
                st.success(msg) if success else st.error(msg)
            else:
                st.warning("Please fill in all fields.")

    elif menu == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username and password:
                success, role = login(username, password)
                if success:
                    st.session_state["username"] = username
                    st.session_state["role"] = role
                    st.rerun() 
                else:
                    st.error(role)
            else:
                st.warning("Please enter both username and password.")
else:
    st.sidebar.write(f"Logged in as **{st.session_state['role']}**")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()