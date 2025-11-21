import streamlit as st
import time

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] and st.session_state["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Email", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Entrar", on_click=password_entered)
        return False
    
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Email", key="username")
        st.text_input("Senha", type="password", key="password")
        st.error("😕 Usuário ou senha incorretos")
        st.button("Entrar", on_click=password_entered)
        return False
    
    else:
        # Password correct.
        return True

def login_page():
    st.title("🔐 Portal Astro IA")
    st.markdown("### Bem-vindo ao seu Portal de Autoconhecimento")
    
    if check_password():
        return True
    return False

def logout():
    st.session_state["password_correct"] = False
    st.rerun()
