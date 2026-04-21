import streamlit as st
from api import BackendAPIError, clear_api_caches, get_api
from state import clear_chat, logout, set_authenticated_user
from utils import mask_token

st.title("Auth")
st.caption("User registration, API key release, account login.")

api = get_api(st.session_state.api_url)

if st.session_state.last_issued_token:
    st.info("New API key is generated. It wont be shown twice.")
    st.code(st.session_state.last_issued_token)


register_tab, login_tab, keys_tab = st.tabs(["Register", "Login", "API keys"])

with register_tab:
    with st.form("register_user_form", clear_on_submit=False):
        username = st.text_input("Username")
        email = st.text_input("User email")
        key_name = st.text_input("Initial API key name", value="primary-key")
        submit_register = st.form_submit_button("Create user and issue a key.")

    if submit_register:
        try:
            with st.spinner("Creating user and API key.."):
                user = api.create_user(username=username, email=email)
                api_key = api.create_api_key(user["id"], key_name)
        except BackendAPIError as exc:
            st.error(str(exc))
        else:
            set_authenticated_user(user, api_key["token"])
            st.session_state.last_issued_token = None
            clear_api_caches()
            st.success("Authenticated.")
            st.rerun()

with login_tab:
    with st.form("login_form", clear_on_submit=False):
        user_id = st.text_input("User ID", value=st.session_state.user_id or "")
        api_key = st.text_input("API key", type="password")
        submit_login = st.form_submit_button("Login")

    if submit_login:
        try:
            with st.spinner("Checking credentials..."):
                user = api.validate_auth(user_id=user_id, api_key=api_key)
        except BackendAPIError as exc:
            st.error(str(exc))
        else:
            set_authenticated_user(user, api_key)
            st.session_state.last_issued_token = None
            clear_api_caches()
            st.success("Authenticated.")
            st.rerun()


with keys_tab:
    if not st.session_state.auth or not st.session_state.user_id:
        st.info("Login first to manage tokens.")
    else:
        st.markdown(f"Current user: `{username}`")
        st.markdown(f"Masked key: `{mask_token(st.session_state.api_key)}`")

        with st.form("new_key_form", clear_on_submit=True):
            extra_key_name = st.text_input("New API key name", value="extra-key")
            submit_new_key = st.form_submit_button("Issue additional key.")

        if submit_new_key:
            try:
                with st.spinner("Issuing additional API key.."):
                    new_key = api.create_api_key(
                        st.session_state.user_id, extra_key_name
                    )
            except BackendAPIError as exc:
                st.error(str(exc))
            else:
                st.session_state.last_issued_token = new_key["token"]
                clear_api_caches()
                st.success("Additional API key issued successfully.")
                st.rerun()

        try:
            keys = api.list_api_keys(st.session_state.user_id)
        except BackendAPIError as exc:
            st.error(str(exc))
        else:
            if keys:
                st.dataframe(keys, use_container_width=True)
            else:
                st.caption("No API keys yet.")


col_left, col_right = st.columns([1, 1])

with col_left:
    if st.session_state.auth:
        st.success("Authenticated")
        st.caption(f"User ID: `{st.session_state.user_id}`")
    else:
        st.warning("Not authenticated")


with col_left:
    if st.session_state.auth and st.button("Logout.", use_container_width=True):
        logout()
        clear_api_caches()
        st.rerun()
