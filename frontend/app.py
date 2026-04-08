import streamlit as st
import requests
import os
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# ─── Page Config ─────────────────────────────────────────────────────────────── #
st.set_page_config(
    page_title="中文语音助手",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────── #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="collapsedControl"] { visibility: visible !important; display: flex !important; }

/* Login card */
.login-card {
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 40px 36px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5);
}

/* Sidebar session buttons */
[data-testid="stSidebar"] button[kind="secondary"] {
    text-align: left !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
    width: 100% !important;
    font-size: 0.87rem !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] button[kind="primary"] {
    text-align: left !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
    width: 100% !important;
    font-size: 0.87rem !important;
    margin-bottom: 2px !important;
}

/* Chat container */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
    border-color: #2a2a2a !important;
}

/* Audio player */
audio { height: 36px !important; width: 100% !important; margin-top: 4px !important; }

/* Buttons */
button[kind="primary"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: transform 0.1s !important;
}
button[kind="primary"]:hover { transform: scale(1.02) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Helper Functions ─────────────────────────────────────────────────────────── #

def auth_headers() -> dict:
    token = st.session_state.get("auth_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def handle_401(res):
    """If API returns 401, log out and rerun."""
    if res.status_code == 401:
        st.session_state.auth_token = None
        st.session_state.auth_user = None
        st.session_state.app_initialized = False
        st.warning("⚠️ Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.")
        st.rerun()


def api_load_sessions():
    try:
        res = requests.get(f"{BACKEND_URL}/sessions", headers=auth_headers(), timeout=30)
        handle_401(res)
        return res.json() if res.ok else []
    except Exception:
        return []


def api_create_session(name: str):
    try:
        res = requests.post(
            f"{BACKEND_URL}/sessions",
            params={"name": name},
            headers=auth_headers(),
            timeout=30,
        )
        handle_401(res)
        return res.json() if res.ok else None
    except Exception:
        return None


def api_load_chats(session_id: str):
    try:
        res = requests.get(
            f"{BACKEND_URL}/chats",
            params={"session_id": session_id},
            headers=auth_headers(),
            timeout=30,
        )
        handle_401(res)
        return res.json() if res.ok else []
    except Exception:
        return []


# Sentinel: audio was checked but not found (404/deleted). Cached to avoid re-requests.
_AUDIO_NOT_FOUND = b"NOT_FOUND"
# How many recent messages get an audio player (older ones: text only)
AUDIO_PLAYER_LIMIT = 10


def get_audio_bytes(audio_path: str) -> bytes | None:
    """Fetch audio with in-memory cache.
    - Caches 404 results as sentinel so we never re-request a missing file.
    - Returns None (silently skip audio) if file not found or any error.
    """
    if not audio_path:
        return None
    cache = st.session_state.setdefault("audio_cache", {})
    cached = cache.get(audio_path)
    if cached is _AUDIO_NOT_FOUND:
        return None  # Already checked — file doesn't exist, skip
    if cached:  # Has real bytes
        return cached
    # Not in cache — fetch
    try:
        url = audio_path if audio_path.startswith("http") else f"{BACKEND_URL}/{audio_path}"
        resp = requests.get(url, headers=auth_headers(), timeout=8)
        if resp.ok and resp.content:
            cache[audio_path] = resp.content
            return resp.content
        # File missing (404 / cleared on restart) — cache sentinel to stop retrying
        cache[audio_path] = _AUDIO_NOT_FOUND
        return None
    except Exception:
        cache[audio_path] = _AUDIO_NOT_FOUND  # Network error also cached as not-found
        return None


def fmt_time(dt_str: str) -> str:
    try:
        clean = str(dt_str).replace("Z", "").split(".")[0]
        return datetime.fromisoformat(clean).strftime("%d/%m %H:%M")
    except Exception:
        return ""


def backend_is_online() -> bool:
    """Quick check — short timeout, don't block the UI."""
    try:
        return requests.get(f"{BACKEND_URL}/", timeout=3).ok
    except Exception:
        return False


def call_api(method: str, url: str, spinner_msg: str = "Đang kết nối...",
             timeout: int = 65, **kwargs):
    """
    Wrapper for API calls with a spinner and cold-start-aware error messages.
    Render free tier needs up to 60s to wake from sleep.
    Returns (response | None, error_string | None)
    """
    try:
        with st.spinner(spinner_msg):
            res = requests.request(method, url, timeout=timeout, **kwargs)
        return res, None
    except requests.exceptions.ReadTimeout:
        return None, (
            "⏳ Server đang khởi động (Render cold start)... "
            "Thường mất 30-60 giây. Vui lòng thử lại!"
        )
    except requests.exceptions.ConnectionError:
        return None, "❌ Không kết nối được backend. Kiểm tra BACKEND_URL."
    except Exception as e:
        return None, f"❌ Lỗi: {e}"


# ─── Session State Init ───────────────────────────────────────────────────────── #
for key, default in [
    ("auth_token", None),
    ("auth_user", None),
    ("app_initialized", False),
    ("sessions", []),
    ("chat_histories", {}),
    ("audio_cache", {}),
    ("current_session_id", None),
    ("pending_bytes", None),
    ("pending_filename", None),
    ("pending_mimetype", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ════════════════════════════════════════════════════════════════════════════════ #
#  AUTH PAGE
# ════════════════════════════════════════════════════════════════════════════════ #
if not st.session_state.auth_token:
    _, center, _ = st.columns([1, 1.4, 1])
    with center:
        st.markdown("""
        <div style="text-align:center;margin:40px 0 32px 0">
            <div style="font-size:3rem">🎤</div>
            <h1 style="margin:8px 0 4px">中文语音助手</h1>
            <p style="color:#888;margin:0">AI Voice Chat</p>
        </div>
        """, unsafe_allow_html=True)

        mode = st.radio(
            "mode",
            ["🔐  Đăng nhập", "📝  Đăng ký tài khoản"],
            horizontal=True,
            key="auth_mode",
            label_visibility="collapsed",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        username = st.text_input(
            "👤 Tên đăng nhập",
            placeholder="Nhập username (ít nhất 3 ký tự)...",
            key="auth_username",
        )
        password = st.text_input(
            "🔑 Mật khẩu",
            type="password",
            placeholder="Nhập mật khẩu (ít nhất 6 ký tự)...",
            key="auth_password",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if mode == "🔐  Đăng nhập":
            if st.button("Đăng nhập", type="primary", use_container_width=True):
                if not username or not password:
                    st.error("Vui lòng nhập đầy đủ thông tin!")
                else:
                    res, err = call_api(
                        "POST",
                        f"{BACKEND_URL}/auth/login",
                        spinner_msg="🔐 Đang đăng nhập... (server có thể mất 30-60 giây để khởi động)",
                        timeout=65,
                        json={"username": username, "password": password},
                    )
                    if err:
                        st.warning(err)
                    elif res.ok:
                        data = res.json()
                        st.session_state.auth_token = data["token"]
                        st.session_state.auth_user = data["username"]
                        st.success(f"✅ Chào mừng, {data['username']}!")
                        st.rerun()
                    else:
                        try:
                            detail = res.json().get("detail", f"Lỗi {res.status_code}")
                        except Exception:
                            detail = f"Server lỗi {res.status_code}"
                        st.error(f"❌ {detail}")
        else:
            if st.button("Tạo tài khoản & Đăng nhập", type="primary", use_container_width=True):
                if not username or not password:
                    st.error("Vui lòng nhập đầy đủ thông tin!")
                else:
                    res, err = call_api(
                        "POST",
                        f"{BACKEND_URL}/auth/register",
                        spinner_msg="📝 Đang tạo tài khoản... (server có thể mất 30-60 giây để khởi động)",
                        timeout=65,
                        json={"username": username, "password": password},
                    )
                    if err:
                        st.warning(err)
                    elif res.ok:
                        data = res.json()
                        st.session_state.auth_token = data["token"]
                        st.session_state.auth_user = data["username"]
                        st.success(f"✅ Tài khoản '{data['username']}' đã được tạo!")
                        st.rerun()
                    else:
                        try:
                            detail = res.json().get("detail", f"Lỗi {res.status_code}")
                        except Exception:
                            detail = f"Server lỗi {res.status_code}"
                        st.error(f"❌ {detail}")

        st.markdown("""
        <div style="text-align:center;margin-top:24px;color:#555;font-size:12px">
            Dữ liệu chat được mã hóa và riêng tư theo từng tài khoản - By tientho201
        </div>
        """, unsafe_allow_html=True)

    st.stop()  # Don't render anything below this if not logged in


# ════════════════════════════════════════════════════════════════════════════════ #
#  MAIN APP (only reached when logged in)
# ════════════════════════════════════════════════════════════════════════════════ #

# Init app data after login
if not st.session_state.app_initialized:
    st.session_state.sessions = api_load_sessions()
    st.session_state.chat_histories = {}
    st.session_state.audio_cache = {}
    st.session_state.current_session_id = None
    st.session_state.app_initialized = True

# Auto-create first session
if not st.session_state.sessions:
    first = api_create_session("对话 1")
    if first:
        st.session_state.sessions = [first]
        st.session_state.current_session_id = first["id"]

if not st.session_state.current_session_id and st.session_state.sessions:
    st.session_state.current_session_id = st.session_state.sessions[0]["id"]

current_sid = st.session_state.current_session_id

if current_sid and current_sid not in st.session_state.chat_histories:
    st.session_state.chat_histories[current_sid] = api_load_chats(current_sid)

current_chats = st.session_state.chat_histories.get(current_sid, [])


# ─── Sidebar ─────────────────────────────────────────────────────────────────── #
with st.sidebar:
    st.markdown(f"## 🎤 中文语音助手")
    st.caption(f"👤 {st.session_state.auth_user}")
    st.divider()

    if st.button("➕  Cuộc trò chuyện mới", use_container_width=True, type="primary", key="btn_new_chat"):
        count = len(st.session_state.sessions) + 1
        new_sess = api_create_session(f"对话 {count}")
        if new_sess:
            st.session_state.sessions.insert(0, new_sess)
            st.session_state.current_session_id = new_sess["id"]
            st.session_state.chat_histories[new_sess["id"]] = []
            st.session_state.pending_bytes = None
            st.rerun()

    st.markdown("**💬 Lịch sử**")

    for sess in st.session_state.sessions:
        is_active = sess["id"] == current_sid
        time_str = fmt_time(str(sess.get("created_at", "")))
        label = f"{'▶  ' if is_active else ''}{sess['name']}  {time_str}"
        if st.button(label, key=f"sess_{sess['id']}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            if sess["id"] != current_sid:
                st.session_state.current_session_id = sess["id"]
                st.session_state.pending_bytes = None
                st.rerun()

    st.divider()
    if st.button("🚪 Đăng xuất", use_container_width=True, key="btn_logout"):
        for k in ["auth_token", "auth_user", "app_initialized", "sessions",
                  "chat_histories", "audio_cache", "current_session_id"]:
            st.session_state[k] = None if "token" in k or "user" in k else ([] if k == "sessions" else ({} if "hist" in k or "cache" in k else False))
        st.rerun()

    st.caption("🟢 Backend online" if backend_is_online() else "🔴 Backend offline")


# ─── Main Header ─────────────────────────────────────────────────────────────── #
current_session_name = next(
    (s["name"] for s in st.session_state.sessions if s["id"] == current_sid), "对话"
)
col_h1, col_h2 = st.columns([6, 1])
with col_h1:
    st.markdown(f"### {current_session_name}")
with col_h2:
    st.markdown(
        f"<div style='text-align:right;color:#888;font-size:12px;padding-top:14px'>"
        f"{len(current_chats)} tin nhắn</div>", unsafe_allow_html=True,
    )


# ─── Scrollable Chat Area ─────────────────────────────────────────────────────── #
chat_box = st.container(height=520, border=True)

with chat_box:
    if not current_chats and not st.session_state.get("pending_bytes"):
        st.markdown("""
            <div style="display:flex;flex-direction:column;align-items:center;
                        justify-content:center;height:420px;text-align:center;opacity:.5;">
                <div style="font-size:3rem">🎙️</div>
                <div style="font-size:1.1rem;margin-top:10px;font-weight:600">Bắt đầu cuộc trò chuyện</div>
                <div style="font-size:0.82rem;margin-top:6px">
                    Ghi âm hoặc tải file âm thanh bên dưới.<br>
                    AI phản hồi bằng <strong>tiếng Trung</strong> và nhớ lịch sử hội thoại.
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Only show audio for the last AUDIO_PLAYER_LIMIT messages.
        # Older messages: text only (avoids N sequential HTTP requests on every render)
        audio_start_idx = max(0, len(current_chats) - AUDIO_PLAYER_LIMIT)

        for idx, chat in enumerate(current_chats):
            with st.chat_message("user"):
                st.markdown(chat["user_text"])
            with st.chat_message("assistant"):
                st.markdown(chat["bot_text"])
                # Fetch audio only for recent messages
                if idx >= audio_start_idx:
                    audio_bytes = get_audio_bytes(chat["audio_path"])
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")

        if st.session_state.get("pending_bytes"):
            with st.chat_message("user"):
                st.markdown("🎙️ _Đã nhận giọng nói — đang phân tích..._")
            with st.chat_message("assistant"):
                with st.spinner("🧠 AI đang suy nghĩ bằng tiếng Trung..."):
                    try:
                        files = {
                            "audio": (
                                st.session_state.pending_filename,
                                BytesIO(st.session_state.pending_bytes),
                                st.session_state.pending_mimetype,
                            )
                        }
                        form_data = {"session_id": current_sid} if current_sid else {}
                        res = requests.post(
                            f"{BACKEND_URL}/chat",
                            files=files,
                            data=form_data,
                            headers=auth_headers(),
                            timeout=120,
                        )
                        if res.ok:
                            result = res.json()
                            st.session_state.chat_histories[current_sid].append(result)
                            audio_url = (result["audio_path"] if result["audio_path"].startswith("http")
                                         else f"{BACKEND_URL}/{result['audio_path']}")
                            try:
                                ar = requests.get(audio_url, timeout=8)
                                if ar.ok:
                                    st.session_state.audio_cache[result["audio_path"]] = ar.content
                            except Exception:
                                pass
                        else:
                            handle_401(res)
                            st.error(f"❌ {res.json().get('detail', res.text)}")
                    except Exception as e:
                        st.error(f"❌ Không kết nối backend: {e}")
                    finally:
                        st.session_state.pending_bytes = None
                        st.session_state.pending_filename = None
                        st.session_state.pending_mimetype = None
                    st.rerun()


# ─── Input Bar ───────────────────────────────────────────────────────────────── #
st.divider()
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    audio_value = st.audio_input("🎙️ Ghi âm giọng nói", key="recorder")
with col2:
    uploaded_file = st.file_uploader("📎 Tải lên file âm thanh", type=["wav", "mp3", "m4a"], key="uploader")
with col3:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    is_busy = bool(st.session_state.get("pending_bytes"))
    send_clicked = st.button(
        "⏳ Đang xử lý..." if is_busy else "➤ Gửi",
        type="primary", use_container_width=True, disabled=is_busy, key="btn_send",
    )

if send_clicked:
    audio_bytes_data, filename, mimetype = None, None, None
    if audio_value:
        audio_bytes_data = audio_value.read()
        filename, mimetype = "audio.wav", "audio/wav"
    elif uploaded_file:
        audio_bytes_data = uploaded_file.read()
        filename = uploaded_file.name
        mimetype = uploaded_file.type or "audio/mpeg"

    if audio_bytes_data:
        st.session_state.pending_bytes = audio_bytes_data
        st.session_state.pending_filename = filename
        st.session_state.pending_mimetype = mimetype
        st.rerun()
    else:
        st.warning("⚠️ Vui lòng ghi âm hoặc tải lên file âm thanh trước!")
