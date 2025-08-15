import os
import time
import json
import io
import requests
import streamlit as st

# ----------------------------
# Configuration
# ----------------------------
DEFAULT_BACKEND = "http://localhost:8000"
BACKEND_URL = os.getenv("BACKEND_URL", DEFAULT_BACKEND).rstrip("/")

# Token storage in Streamlit session
def get_tokens():
    return st.session_state.get("access_token"), st.session_state.get("refresh_token")

def set_tokens(access_token=None, refresh_token=None):
    if access_token is not None:
        st.session_state["access_token"] = access_token
    if refresh_token is not None:
        st.session_state["refresh_token"] = refresh_token

def clear_tokens():
    for k in ["access_token", "refresh_token", "user"]:
        if k in st.session_state:
            del st.session_state[k]

def auth_headers():
    access, _ = get_tokens()
    return {"Authorization": f"Bearer {access}"} if access else {}

def api_get(path, params=None, stream=False):
    url = f"{BACKEND_URL}{path}"
    return requests.get(url, params=params, headers=auth_headers(), stream=stream, timeout=60)

def api_post(path, payload=None, files=None):
    url = f"{BACKEND_URL}{path}"
    headers = auth_headers()
    # If files are provided, let requests set multipart headers
    if files:
        return requests.post(url, data=payload, files=files, headers=headers, timeout=120)
    else:
        headers["Content-Type"] = "application/json"
        return requests.post(url, data=json.dumps(payload or {}), headers=headers, timeout=120)

def api_delete(path):
    url = f"{BACKEND_URL}{path}"
    return requests.delete(url, headers=auth_headers(), timeout=60)

# ----------------------------
# Authentication helpers
# ----------------------------
def login(username: str, password: str):
    resp = api_post("/auth/login", {"username": username, "password": password})
    if resp.ok:
        data = resp.json()
        set_tokens(data.get("access_token"), data.get("refresh_token"))
        # Fetch current user
        me = api_get("/auth/me")
        if me.ok:
            st.session_state["user"] = me.json()
        return True, "Login successful."
    return False, resp.text

def register(username: str, email: str, password: str):
    resp = api_post("/auth/register", {"username": username, "email": email, "password": password})
    if resp.ok:
        return True, "Registration successful. Please login."
    return False, resp.text

def refresh_token():
    _, rtoken = get_tokens()
    if not rtoken:
        return False, "No refresh token."
    resp = api_post("/auth/refresh", {"refresh_token": rtoken})
    if resp.ok:
        data = resp.json()
        set_tokens(data.get("access_token"), data.get("refresh_token"))
        return True, "Token refreshed."
    return False, resp.text

def ensure_auth():
    # Try a simple /auth/me; if 401, attempt refresh once
    me = api_get("/auth/me")
    if me.status_code == 401:
        ok, _ = refresh_token()
        if not ok:
            clear_tokens()
            return False
        me = api_get("/auth/me")
    if me.ok:
        st.session_state["user"] = me.json()
        return True
    return False

# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title="MindCanvas (Streamlit)", layout="wide")
st.sidebar.title("MindCanvas")
st.sidebar.caption("Streamlit UI for the FastAPI backend")

with st.sidebar.expander("Settings", expanded=False):
    st.write("Backend URL")
    current = st.text_input("BACKEND_URL", value=BACKEND_URL)
    if st.button("Apply URL"):
        st.session_state["pending_backend_url"] = current

if "pending_backend_url" in st.session_state:
    # Prompt restart notice
    st.warning("Please restart the app with BACKEND_URL environment variable set to: " + st.session_state["pending_backend_url"])

# Auth panel
auth_area = st.sidebar.container()
access_token, refresh_token_value = get_tokens()

if not access_token:
    tab_login, tab_register = auth_area.tabs(["Login", "Register"])
    with tab_login:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            ok, msg = login(u, p)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    with tab_register:
        ru = st.text_input("New Username", key="reg_user")
        re = st.text_input("Email", key="reg_email")
        rp = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            ok, msg = register(ru, re, rp)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
else:
    user_box = auth_area.container()
    user_box.write(f"Logged in as: {st.session_state.get('user', {}).get('username', 'Unknown')}")
    colA, colB = user_box.columns(2)
    if colA.button("Refresh Token"):
        ok, msg = refresh_token()
        if ok:
            st.success(msg)
        else:
            st.error(msg)
    if colB.button("Logout"):
        clear_tokens()
        st.success("Logged out.")
        st.rerun()

st.markdown("## MindCanvas Dashboard (Streamlit)")
if access_token and ensure_auth():
    tabs = st.tabs(["Search", "Image Generation", "History", "Dashboard Exports", "Admin"])
else:
    tabs = st.tabs(["Search (logged-out demo)", "Image Generation (logged-out demo)"])

# ----------------------------
# Search tab(s)
# ----------------------------
def render_search(logged_in: bool):
    st.subheader("Web Search")
    q = st.text_input("Query", placeholder="e.g., 'latest AI research trends'")
    do_search = st.button("Run Search")
    if do_search:
        payload = {"query": q}
        resp = api_post("/search/", payload)
        if resp.ok:
            data = resp.json()
            st.success("Search completed.")
            st.json(data)
        else:
            st.error(f"Search failed: {resp.status_code} {resp.text}")

# ----------------------------
# Image Generation
# ----------------------------
def render_image_gen(logged_in: bool):
    st.subheader("AI Image Generation")
    prompt = st.text_area("Prompt", placeholder="A cat wearing a strawberry hat sitting on a dragon throne")
    cols = st.columns(3)
    num_images = cols[0].number_input("Number of images", min_value=1, max_value=4, value=1, step=1)
    size = cols[1].selectbox("Size", ["512x512", "768x768", "1024x1024"], index=0)
    seed = cols[2].number_input("Seed (optional)", min_value=0, value=0, step=1)
    if st.button("Generate"):
        payload = {"prompt": prompt, "num_images": int(num_images), "size": size}
        if seed:
            payload["seed"] = int(seed)
        resp = api_post("/image/generate", payload)
        if resp.ok:
            data = resp.json()
            st.success("Image generation triggered.")
            # Expecting a structure with images or URLs. Adapt to actual backend schema if different.
            images = data.get("images") or data.get("results") or []
            if not images:
                st.info("No images returned (mock mode or generation pending).")
            for idx, item in enumerate(images, start=1):
                url = item.get("url") or item.get("image_url")
                if url:
                    st.image(url, caption=f"Image {idx}", use_container_width=True)
                else:
                    # If base64 or bytes, handle accordingly
                    if "b64" in item:
                        import base64
                        img_bytes = base64.b64decode(item["b64"])
                        st.image(img_bytes, caption=f"Image {idx}", use_container_width=True)
                    else:
                        st.write(item)
        else:
            st.error(f"Generation failed: {resp.status_code} {resp.text}")

# ----------------------------
# History
# ----------------------------
def render_history():
    st.subheader("History")
    col1, col2 = st.columns(2)
    if col1.button("Fetch Search History"):
        resp = api_get("/search/history")
        if resp.ok:
            st.json(resp.json())
        else:
            st.error(resp.text)
    if col2.button("Fetch Image History"):
        resp = api_get("/image/history")
        if resp.ok:
            st.json(resp.json())
        else:
            st.error(resp.text)

# ----------------------------
# Dashboard exports and deletion
# ----------------------------
def render_dashboard_exports():
    st.subheader("Dashboard")
    col1, col2 = st.columns(2)
    if col1.button("Export CSV"):
        resp = api_get("/dashboard/export/csv", stream=True)
        if resp.ok:
            content = resp.content
            st.download_button("Download CSV", data=content, file_name="mindcanvas_export.csv", mime="text/csv")
        else:
            st.error(resp.text)
    if col2.button("Export PDF"):
        resp = api_get("/dashboard/export/pdf", stream=True)
        if resp.ok:
            content = resp.content
            st.download_button("Download PDF", data=content, file_name="mindcanvas_export.pdf", mime="application/pdf")
        else:
            st.error(resp.text)

    st.markdown("---")
    st.caption("Delete individual entries by ID")
    delete_type = st.selectbox("Type", ["search", "image"])
    delete_id = st.text_input("ID to delete", placeholder="UUID or numeric ID")
    if st.button("Delete"):
        if not delete_id.strip():
            st.warning("Provide an ID.")
        else:
            path = f"/dashboard/{'search' if delete_type=='search' else 'image'}/{delete_id.strip()}"
            resp = api_delete(path)
            if resp.ok:
                st.success("Deleted.")
            else:
                st.error(resp.text)

# ----------------------------
# Admin: Whoami and raw calls
# ----------------------------
def render_admin():
    st.subheader("Admin")
    if st.button("Who am I?"):
        resp = api_get("/auth/me")
        if resp.ok:
            st.json(resp.json())
        else:
            st.error(resp.text)

    st.markdown("### Raw API test")
    raw_path = st.text_input("Path (e.g., /docs or /search/history)")
    raw_method = st.selectbox("Method", ["GET", "POST", "DELETE"])
    raw_payload = st.text_area("JSON payload (for POST)", value="")
    if st.button("Send"):
        try:
            if raw_method == "GET":
                r = api_get(raw_path if raw_path.startswith("/") else "/" + raw_path)
            elif raw_method == "POST":
                payload = json.loads(raw_payload) if raw_payload.strip() else {}
                r = api_post(raw_path if raw_path.startswith("/") else "/" + raw_path, payload)
            else:
                r = api_delete(raw_path if raw_path.startswith("/") else "/" + raw_path)
            st.code(f"Status: {r.status_code}")
            try:
                st.json(r.json())
            except Exception:
                st.text(r.text)
        except Exception as e:
            st.error(str(e))

# ----------------------------
# Render tabs
# ----------------------------
if access_token and ensure_auth():
    with tabs[0]:
        render_search(logged_in=True)
    with tabs[1]:
        render_image_gen(logged_in=True)
    with tabs[2]:
        render_history()
    with tabs[3]:
        render_dashboard_exports()
    with tabs[4]:
        render_admin()
else:
    with tabs:
        st.info("Logged-out demo: search will work only if backend allows anonymous or mock mode.")
        render_search(logged_in=False)
    with tabs[1]:
        st.info("Logged-out demo: image generation may require auth or keys; mock mode may return placeholders.")
        render_image_gen(logged_in=False)
