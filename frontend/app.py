import streamlit as st
import requests
import os
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# ─── Bilingual UI Text ────────────────────────────────────────────────────────── #
LANG_UI = {
    "zh": {
        "app_title":       "中文语音助手",
        "app_subtitle":    "AI Voice Chat",
        "new_chat":        "➕  新建对话",
        "history":         "**💬 历史记录**",
        "logout":          "🚪 退出登录",
        "online":          "🟢 服务器在线",
        "offline":         "🔴 服务器离线",
        "empty_title":     "开始对话",
        "empty_sub":       "录音或上传音频文件，AI 将用<strong>中文</strong>回答并记住对话历史。",
        "user_thinking":   "🎙️ _已录音，正在分析..._",
        "bot_thinking":    "🧠 AI 正在用中文思考...",
        "input_mic":       "🎙️ 录音",
        "input_upload":    "📎 上传音频",
        "send":            "➤ 发送",
        "processing":      "⏳ 处理中...",
        "warn_no_audio":   "⚠️ 请先录音或上传音频文件！",
        "session_default": "对话",
        "session_prefix":  "对话",
        "lang_label":      "🌐 语言",
        "login_title":     "中文语音助手",
        "login_sub":       "AI Voice Chat",
        "tab_login":       "🔐  登录",
        "tab_register":    "📝  注册账户",
        "field_user":      "👤 用户名",
        "field_pass":      "🔑 密码",
        "placeholder_user":"输入用户名（至少3个字符）...",
        "placeholder_pass":"输入密码（至少6个字符）...",
        "btn_login":       "登录",
        "btn_register":    "注册并登录",
        "spin_login":      "🔐 正在登录...（服务器可能需要30-60秒启动）",
        "spin_register":   "📝 正在注册...（服务器可能需要30-60秒启动）",
        "footer_text":     "数据加密，每个账户独立隔离 - By tientho201",
        "welcome":         "✅ 欢迎，{username}！",
        "registered":      "✅ 账户 '{username}' 创建成功！",
        "err_fill":        "请填写完整信息！",
        "msgs":            "条消息",
    },
    "vi": {
        "app_title":       "Trợ Lý Giọng Nói AI",
        "app_subtitle":    "AI Voice Chat",
        "new_chat":        "➕  Cuộc trò chuyện mới",
        "history":         "**💬 Lịch sử**",
        "logout":          "🚪 Đăng xuất",
        "online":          "🟢 Backend online",
        "offline":         "🔴 Backend offline",
        "empty_title":     "Bắt đầu cuộc trò chuyện",
        "empty_sub":       "Ghi âm hoặc tải file âm thanh bên dưới, AI trả lời bằng <strong>tiếng Việt</strong> và nhớ lịch sử hội thoại.",
        "user_thinking":   "🎙️ _Đã nhận giọng nói — đang phân tích..._",
        "bot_thinking":    "🧠 AI đang suy nghĩ bằng tiếng Việt...",
        "input_mic":       "🎙️ Ghi âm giọng nói",
        "input_upload":    "📎 Tải lên file âm thanh",
        "send":            "➤ Gửi",
        "processing":      "⏳ Đang xử lý...",
        "warn_no_audio":   "⚠️ Vui lòng ghi âm hoặc tải lên file âm thanh trước!",
        "session_default": "Hội thoại",
        "session_prefix":  "Hội thoại",
        "lang_label":      "🌐 Ngôn ngữ",
        "login_title":     "Trợ Lý Giọng Nói AI",
        "login_sub":       "AI Voice Chat",
        "tab_login":       "🔐  Đăng nhập",
        "tab_register":    "📝  Đăng ký tài khoản",
        "field_user":      "👤 Tên đăng nhập",
        "field_pass":      "🔑 Mật khẩu",
        "placeholder_user":"Nhập username (ít nhất 3 ký tự)...",
        "placeholder_pass":"Nhập mật khẩu (ít nhất 6 ký tự)...",
        "btn_login":       "Đăng nhập",
        "btn_register":    "Tạo tài khoản & Đăng nhập",
        "spin_login":      "🔐 Đang đăng nhập... (server có thể mất 30-60 giây để khởi động)",
        "spin_register":   "📝 Đang tạo tài khoản... (server có thể mất 30-60 giây để khởi động)",
        "footer_text":     "Dữ liệu chat được mã hóa và riêng tư theo từng tài khoản - By tientho201",
        "welcome":         "✅ Chào mừng, {username}!",
        "registered":      "✅ Tài khoản '{username}' đã được tạo!",
        "err_fill":        "Vui lòng nhập đầy đủ thông tin!",
        "msgs":            "tin nhắn",
    },
}


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
    ("lang", "vi"),  # Default language: Vietnamese
    ("stt_warning", None),  # Persistent STT error message across reruns
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Shortcut helper
def T(key: str) -> str:
    return LANG_UI.get(st.session_state.lang, LANG_UI["vi"]).get(key, key)


import re as _re

def display_session_name(name: str) -> str:
    """Translate default session names on-the-fly (display only, no DB write).
    '\u5bf9\u8bdd N' <-> 'H\u1ed9i tho\u1ea1i N' depending on current language.
    """
    lang = st.session_state.lang
    if lang == "vi":
        m = _re.match(r"\u5bf9\u8bdd\s*(\d+)", name)
        if m:
            return f"H\u1ed9i tho\u1ea1i {m.group(1)}"
    elif lang == "zh":
        m = _re.match(r"H\u1ed9i tho\u1ea1i\s*(\d+)", name)
        if m:
            return f"\u5bf9\u8bdd {m.group(1)}"
    return name


# ════════════════════════════════════════════════════════════════════════════════ #
#  AUTH PAGE
# ════════════════════════════════════════════════════════════════════════════════ #
if not st.session_state.auth_token:
    # Language switcher on login page
    _, _sw, _ = st.columns([2, 1, 2])
    with _sw:
        lang_choice = st.radio(
            "🌐 Language",
            ["🇻🇳 Việt", "🇨🇳 中文"],
            horizontal=True,
            key="login_lang_radio",
            label_visibility="collapsed",
            index=0 if st.session_state.lang == "vi" else 1,
        )
        new_lang = "vi" if "Việt" in lang_choice else "zh"
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun()

    _, center, _ = st.columns([1, 1.4, 1])
    with center:
        st.markdown(f"""
        <div style="text-align:center;margin:20px 0 32px 0">
            <div style="font-size:3rem">🎤</div>
            <h1 style="margin:8px 0 4px">{T('login_title')}</h1>
            <p style="color:#888;margin:0">{T('login_sub')}</p>
        </div>
        """, unsafe_allow_html=True)

        mode = st.radio(
            "mode",
            [T("tab_login"), T("tab_register")],
            horizontal=True,
            key="auth_mode",
            label_visibility="collapsed",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        username = st.text_input(
            T("field_user"),
            placeholder=T("placeholder_user"),
            key="auth_username",
        )
        password = st.text_input(
            T("field_pass"),
            type="password",
            placeholder=T("placeholder_pass"),
            key="auth_password",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if mode == T("tab_login"):
            if st.button(T("btn_login"), type="primary", use_container_width=True):
                if not username or not password:
                    st.error(T("err_fill"))
                else:
                    res, err = call_api(
                        "POST",
                        f"{BACKEND_URL}/auth/login",
                        spinner_msg=T("spin_login"),
                        timeout=65,
                        json={"username": username, "password": password},
                    )
                    if err:
                        st.warning(err)
                    elif res.ok:
                        data = res.json()
                        st.session_state.auth_token = data["token"]
                        st.session_state.auth_user = data["username"]
                        st.success(T("welcome").format(username=data["username"]))
                        st.rerun()
                    else:
                        try:
                            detail = res.json().get("detail", f"Error {res.status_code}")
                        except Exception:
                            detail = f"Server error {res.status_code}"
                        st.error(f"❌ {detail}")
        else:
            if st.button(T("btn_register"), type="primary", use_container_width=True):
                if not username or not password:
                    st.error(T("err_fill"))
                else:
                    res, err = call_api(
                        "POST",
                        f"{BACKEND_URL}/auth/register",
                        spinner_msg=T("spin_register"),
                        timeout=65,
                        json={"username": username, "password": password},
                    )
                    if err:
                        st.warning(err)
                    elif res.ok:
                        data = res.json()
                        st.session_state.auth_token = data["token"]
                        st.session_state.auth_user = data["username"]
                        st.success(T("registered").format(username=data["username"]))
                        st.rerun()
                    else:
                        try:
                            detail = res.json().get("detail", f"Error {res.status_code}")
                        except Exception:
                            detail = f"Server error {res.status_code}"
                        st.error(f"❌ {detail}")

        st.markdown(f"""
        <div style="text-align:center;margin-top:24px;color:#555;font-size:12px">
            {T('footer_text')}
        </div>
        """, unsafe_allow_html=True)

    st.stop()


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
    first = api_create_session(f"{T('session_prefix')} 1")
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
    st.markdown(f"## 🎤 {T('app_title')}")
    st.caption(f"👤 {st.session_state.auth_user}")
    st.divider()

    # ── Language switcher ──
    lang_choice = st.radio(
        T("lang_label"),
        ["🇻🇳 Tiếng Việt", "🇨🇳 中文"],
        horizontal=True,
        key="sidebar_lang",
        index=0 if st.session_state.lang == "vi" else 1,
    )
    new_lang = "vi" if "Việt" in lang_choice else "zh"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    st.divider()

    if st.button(T("new_chat"), use_container_width=True, type="primary", key="btn_new_chat"):
        count = len(st.session_state.sessions) + 1
        new_sess = api_create_session(f"{T('session_prefix')} {count}")
        if new_sess:
            st.session_state.sessions.insert(0, new_sess)
            st.session_state.current_session_id = new_sess["id"]
            st.session_state.chat_histories[new_sess["id"]] = []
            st.session_state.pending_bytes = None
            st.rerun()

    st.markdown(T("history"))

    for sess in st.session_state.sessions:
        is_active = sess["id"] == current_sid
        time_str = fmt_time(str(sess.get("created_at", "")))
        disp_name = display_session_name(sess["name"])
        label = f"{'▶  ' if is_active else ''}{disp_name}  {time_str}"
        if st.button(label, key=f"sess_{sess['id']}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            if sess["id"] != current_sid:
                st.session_state.current_session_id = sess["id"]
                st.session_state.pending_bytes = None
                st.session_state.stt_warning = None  # Clear warning on session switch
                st.rerun()

    st.divider()
    if st.button(T("logout"), use_container_width=True, key="btn_logout"):
        for k in ["auth_token", "auth_user", "app_initialized", "sessions",
                  "chat_histories", "audio_cache", "current_session_id"]:
            st.session_state[k] = None if "token" in k or "user" in k else (
                [] if k == "sessions" else ({} if "hist" in k or "cache" in k else False))
        st.rerun()

    st.caption(T("online") if backend_is_online() else T("offline"))


# ─── Main Header ─────────────────────────────────────────────────────────────── #
_raw_session_name = next(
    (s["name"] for s in st.session_state.sessions if s["id"] == current_sid),
    T("session_default")
)
current_session_name = display_session_name(_raw_session_name)
col_h1, col_h2 = st.columns([6, 1])
with col_h1:
    st.markdown(f"### {current_session_name}")
with col_h2:
    st.markdown(
        f"<div style='text-align:right;color:#888;font-size:12px;padding-top:14px'>"
        f"{len(current_chats)} {T('msgs')}</div>", unsafe_allow_html=True,
    )


# ─── Scrollable Chat Area ─────────────────────────────────────────────────────── #
chat_box = st.container(height=520, border=True)

with chat_box:
    if not current_chats and not st.session_state.get("pending_bytes"):
        st.markdown(f"""
            <div style="display:flex;flex-direction:column;align-items:center;
                        justify-content:center;height:420px;text-align:center;opacity:.5;">
                <div style="font-size:3rem">🎙️</div>
                <div style="font-size:1.1rem;margin-top:10px;font-weight:600">{T('empty_title')}</div>
                <div style="font-size:0.82rem;margin-top:6px">
                    {T('empty_sub')}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        audio_start_idx = max(0, len(current_chats) - AUDIO_PLAYER_LIMIT)

        for idx, chat in enumerate(current_chats):
            with st.chat_message("user"):
                st.markdown(chat["user_text"])
            with st.chat_message("assistant"):
                st.markdown(chat["bot_text"])
                if idx >= audio_start_idx:
                    audio_bytes = get_audio_bytes(chat["audio_path"])
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")

        if st.session_state.get("pending_bytes"):
            with st.chat_message("user"):
                st.markdown(T("user_thinking"))
            with st.chat_message("assistant"):
                with st.spinner(T("bot_thinking")):
                    try:
                        files = {
                            "audio": (
                                st.session_state.pending_filename,
                                BytesIO(st.session_state.pending_bytes),
                                st.session_state.pending_mimetype,
                            )
                        }
                        form_data = {"session_id": current_sid,
                                     "language": st.session_state.lang}
                        res = requests.post(
                            f"{BACKEND_URL}/chat",
                            files=files,
                            data=form_data,
                            headers=auth_headers(),
                            timeout=120,
                        )
                        if res.ok:
                            result = res.json()
                            st.session_state.stt_warning = None  # Clear warning on success
                            st.session_state.chat_histories[current_sid].append(result)
                            audio_url = (result["audio_path"] if result["audio_path"].startswith("http")
                                         else f"{BACKEND_URL}/{result['audio_path']}")
                            try:
                                ar = requests.get(audio_url, timeout=8)
                                if ar.ok:
                                    st.session_state.audio_cache[result["audio_path"]] = ar.content
                            except Exception:
                                pass
                        elif res.status_code == 400:
                            # STT hallucination / no speech — persist warning across rerun
                            try:
                                msg = res.json().get("detail", "Không nhận diện được giọng nói.")
                            except Exception:
                                msg = "Không nhận diện được giọng nói."
                            st.session_state.stt_warning = msg  # Saved → survives rerun
                        else:
                            handle_401(res)
                            try:
                                st.error(f"❌ {res.json().get('detail', res.text)}")
                            except Exception:
                                st.error(f"❌ Lỗi {res.status_code}")
                    except Exception as e:
                        st.error(f"❌ {e}")
                    finally:
                        st.session_state.pending_bytes = None
                        st.session_state.pending_filename = None
                        st.session_state.pending_mimetype = None
                    st.rerun()


# ─── Persistent STT Warning Banner ───────────────────────────────────────────── #
if st.session_state.get("stt_warning"):
    col_w, col_x = st.columns([10, 1])
    with col_w:
        st.warning(f"🎙️ {st.session_state.stt_warning}")
    with col_x:
        if st.button("✕", key="dismiss_stt_warn", help="Đóng"):
            st.session_state.stt_warning = None
            st.rerun()


# ─── Input Bar ───────────────────────────────────────────────────────────────── #
st.divider()
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    audio_value = st.audio_input(T("input_mic"), key="recorder")
with col2:
    uploaded_file = st.file_uploader(T("input_upload"), type=["wav", "mp3", "m4a"], key="uploader")
with col3:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    is_busy = bool(st.session_state.get("pending_bytes"))
    send_clicked = st.button(
        T("processing") if is_busy else T("send"),
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
        st.warning(T("warn_no_audio"))

