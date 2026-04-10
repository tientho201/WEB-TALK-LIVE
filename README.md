# 🎤 WEB-TALK-LIVE — Chinese AI Voice Chat

> Ứng dụng voice chat tiếng Trung full-stack: **Giọng nói → Groq Whisper STT → GPT-4o-mini → Edge TTS → Âm thanh**

[![CI](https://github.com/tientho201/WEB-TALK-LIVE/actions/workflows/ci.yml/badge.svg)](https://github.com/tientho201/WEB-TALK-LIVE/actions)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.37+-red)

---

## 📋 Mục lục

- [Tính năng](#-tính-năng)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [Tech Stack](#-tech-stack)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Cài đặt local](#-cài-đặt-local)
- [Biến môi trường](#-biến-môi-trường)
- [Chạy với Docker](#-chạy-với-docker)
- [Deploy Production](#-deploy-production)
- [Audio Storage trên Production](#-audio-storage-trên-production)
- [API Endpoints](#-api-endpoints)
- [Bảo mật](#-bảo-mật)

---

## ✨ Tính năng

- 🔐 **Xác thực người dùng** — Đăng ký / đăng nhập bằng JWT, dữ liệu chat riêng biệt theo tài khoản
- 🎙️ **Voice Input** — Ghi âm trực tiếp trình duyệt hoặc upload file (WAV, MP3, M4A)
- 🈶 **STT tiếng Trung** — Groq Whisper Large V3 Turbo, độ chính xác cao
- 🧠 **LLM có bộ nhớ** — GPT-4o-mini ghi nhớ toàn bộ lịch sử hội thoại trong session
- 🔊 **TTS tiếng Trung** — Microsoft Edge TTS (`zh-CN-XiaoxiaoNeural`), fallback OpenAI TTS
- 💬 **Quản lý session** — Tạo nhiều cuộc trò chuyện, lưu lịch sử lâu dài trong DB
- 🐳 **Docker ready** — `docker-compose up` là xong
- ☁️ **Production ready** — Supabase (DB + Storage), CI/CD GitHub Actions

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  Login/Register → Chat UI → Audio Player → Session Manager  │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP + Bearer JWT
┌──────────────────────────▼──────────────────────────────────┐
│                      FastAPI Backend                         │
│                                                              │
│  POST /auth/register   POST /auth/login                     │
│  GET  /sessions        POST /sessions                       │
│  POST /chat            GET  /chats                          │
│                                                              │
│  Pipeline:                                                   │
│  Audio → Groq Whisper STT → GPT-4o-mini → Edge TTS → MP3   │
└──────────┬──────────────────────────────┬────────────────────┘
           │                              │
    ┌──────▼──────┐              ┌────────▼────────┐
    │  PostgreSQL  │              │  Audio Storage   │
    │  (Supabase)  │              │ Local / Supabase │
    └─────────────┘              └─────────────────┘
```

---

## 🛠️ Tech Stack

| Layer         | Công nghệ                                            |
| ------------- | ---------------------------------------------------- |
| **Frontend**  | Streamlit                                            |
| **Backend**   | FastAPI + Uvicorn                                    |
| **Database**  | PostgreSQL (Supabase) + SQLAlchemy ORM               |
| **Auth**      | JWT (PyJWT) + bcrypt                                 |
| **STT**       | Groq Whisper Large V3 Turbo                          |
| **LLM**       | OpenAI GPT-4o-mini                                   |
| **TTS**       | Microsoft Edge TTS (primary) + OpenAI TTS (fallback) |
| **Container** | Docker + Docker Compose                              |
| **CI/CD**     | GitHub Actions                                       |

---

## 📁 Cấu trúc dự án

```
WEB-TALK-LIVE/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── routes/
│   │   ├── auth.py              # POST /auth/register, /auth/login
│   │   └── chat.py              # POST /chat, GET /sessions, GET /chats
│   ├── services/
│   │   ├── auth.py              # JWT + bcrypt password hashing
│   │   ├── stt_groq.py          # Groq Whisper transcription
│   │   ├── llm_openai.py        # GPT-4o-mini với chat history
│   │   ├── tts_edge.py          # Microsoft Edge TTS (primary)
│   │   ├── tts_openai.py        # OpenAI TTS (fallback)
│   │   └── storage.py           # Local / Supabase Storage abstraction
│   ├── models/
│   │   └── chat.py              # Pydantic response models
│   └── database/
│       └── db.py                # SQLAlchemy models + init_db migrations
│
├── frontend/
│   └── app.py                   # Streamlit UI
│
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
│
├── .streamlit/
│   └── config.toml              # Dark theme config
│
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI
│
├── audio_files/                 # Local audio storage (git-ignored)
├── .env                         # Biến môi trường (git-ignored)
├── .gitignore
├── docker-compose.yml
└── requirements.txt
```

---

## 🚀 Cài đặt local

### Yêu cầu

- Python 3.11+
- PostgreSQL (hoặc dùng Supabase miễn phí)
- FFmpeg (để xử lý audio)

### Bước 1 — Clone & tạo môi trường ảo

```bash
git clone https://github.com/YOUR_USERNAME/WEB-TALK-LIVE.git
cd WEB-TALK-LIVE

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### Bước 2 — Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 3 — Tạo file `.env`

```bash
cp .env.example .env
# Rồi điền các giá trị thực vào .env
```

### Bước 4 — Chạy Backend

```bash
# Windows (.venv)
.venv\Scripts\uvicorn.exe backend.main:app --host 0.0.0.0 --port 8000

# Linux/Mac
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Backend tự động:

- Tạo bảng `users`, `chat_sessions`, `chats` trong DB
- Chạy migrations an toàn nếu bảng đã tồn tại

### Bước 5 — Chạy Frontend

```bash
streamlit run frontend/app.py
```

Mở trình duyệt: **http://localhost:8501**

---

## 🔑 Biến môi trường

Tạo file `.env` ở thư mục gốc với nội dung sau:

```env
# ── API Keys ──────────────────────────────────────────────────
# OpenAI: https://platform.openai.com/api-keys
OPENAI_API_KEY="sk-proj-..."

# Groq: https://console.groq.com/keys
GROQ_API_KEY="gsk_..."

# ── Database ──────────────────────────────────────────────────
# Supabase: Project → Settings → Database → Connection string (URI)
# Chú ý: ký tự '@' trong password phải encode thành '%40'
DATABASE_URL="postgresql://postgres.xxxxx:password%40here@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres"

# ── Backend URL ───────────────────────────────────────────────
# Local dev
BACKEND_URL="http://localhost:8000"
# Docker / Production: đổi thành domain thực
# BACKEND_URL="https://api.yourdomain.com"

# ── JWT Secret ────────────────────────────────────────────────
# Tự tạo bằng: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY="your-super-secret-key-minimum-32-chars"

# ── Audio Storage (Production) ───────────────────────────────
# Mặc định: lưu local (phù hợp Docker với volume)
STORAGE_BACKEND="local"

# Nếu deploy trên Heroku/Railway (filesystem tạm thời), dùng Supabase Storage:
# STORAGE_BACKEND="supabase"
# SUPABASE_URL="https://xxxxx.supabase.co"
# SUPABASE_SERVICE_KEY="eyJhbGci..."   # Service Role key (không phải anon key!)
# SUPABASE_BUCKET="audio-files"        # Tên bucket đã tạo trong Supabase Storage
```

### Tạo SECRET_KEY mạnh

```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Ví dụ output: a3f8e2c1d4b6...
```

---

## 🐳 Chạy với Docker

```bash
# Tạo file .env trước (xem phần trên)
# Sau đó:
docker-compose up --build
```

Dịch vụ sẽ chạy tại:

- Frontend: **http://localhost:8501**
- Backend API: **http://localhost:8000**
- PostgreSQL: **localhost:5432**

### Dừng và xóa containers

```bash
docker-compose down
# Xóa cả data volumes:
docker-compose down -v
```

> **Lưu ý:** `docker-compose.yml` đã mount `./audio_files:/app/audio_files` nên audio files được lưu lâu dài trên máy host.

---

## ☁️ Deploy Production

### Option A: Docker trên VPS (DigitalOcean, Hetzner, Linode...)

```bash
# Trên server
git clone https://github.com/tientho201/WEB-TALK-LIVE.git
cd WEB-TALK-LIVE
cp .env.example .env
nano .env   # Điền API keys thực

docker-compose up -d --build
```

Cài Nginx reverse proxy:

```nginx
# /etc/nginx/sites-available/webtalk
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend Streamlit
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Backend API
    location /api/ {
        rewrite ^/api/(.*)$ /$1 break;
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

### Option B: Railway / Render

1. Push code lên GitHub
2. Tạo project mới trên Railway/Render
3. Thêm **environment variables** từ `.env` vào dashboard
4. Deploy backend (Dockerfile: `docker/backend.Dockerfile`)
5. Deploy frontend (Dockerfile: `docker/frontend.Dockerfile`)
6. Set `BACKEND_URL` của frontend = URL của backend service

### Option C: Supabase + Fly.io

- Database: **Supabase** (PostgreSQL miễn phí)
- Backend: **Fly.io** (FastAPI container)
- Frontend: **Streamlit Community Cloud** (miễn phí)

---

## 🔊 Audio Storage trên Production

| Môi trường         | `STORAGE_BACKEND`  | Mô tả                                            |
| ------------------ | ------------------ | ------------------------------------------------ |
| **Local / Docker** | `local` (mặc định) | Lưu vào `audio_files/`, serve qua FastAPI static |
| **VPS với Docker** | `local`            | Volume mount đảm bảo không mất file              |
| **Heroku/Railway** | `supabase`         | Upload lên Supabase Storage, trả public URL      |

### Cài đặt Supabase Storage

1. Vào **Supabase Dashboard** → **Storage** → **New Bucket**
2. Đặt tên bucket: `audio-files`, bật **Public bucket**
3. Vào **Settings** → **API** → lấy **Service Role Key** (không phải `anon` key)
4. Thêm vào `.env`:

```env
STORAGE_BACKEND="supabase"
SUPABASE_URL="https://xxxxx.supabase.co"
SUPABASE_SERVICE_KEY="eyJhbGci..."
SUPABASE_BUCKET="audio-files"
```

---

## 📡 API Endpoints

### Auth (công khai)

| Method | Endpoint         | Body                                     | Mô tả                     |
| ------ | ---------------- | ---------------------------------------- | ------------------------- |
| `POST` | `/auth/register` | `{"username": "...", "password": "..."}` | Tạo tài khoản             |
| `POST` | `/auth/login`    | `{"username": "...", "password": "..."}` | Đăng nhập, nhận JWT token |

### Chat (cần JWT token trong header)

Header: `Authorization: Bearer <token>`

| Method | Endpoint    | Params / Body                        | Mô tả                           |
| ------ | ----------- | ------------------------------------ | ------------------------------- |
| `GET`  | `/sessions` | —                                    | Lấy danh sách sessions của user |
| `POST` | `/sessions` | `?name=...`                          | Tạo session mới                 |
| `POST` | `/chat`     | `audio` (file) + `session_id` (form) | Xử lý voice → text → AI → audio |
| `GET`  | `/chats`    | `?session_id=...`                    | Lấy lịch sử chat của session    |
| `GET`  | `/`         | —                                    | Health check                    |

### Response mẫu — `POST /chat`

```json
{
  "user_text": "今天天气怎么样？",
  "bot_text": "今天天气很好，阳光明媚，适合出门散步。",
  "audio_path": "audio_files/uuid_output.mp3"
}
```

---

## 🔒 Bảo mật

| Vấn đề                | Cách xử lý                                                   |
| --------------------- | ------------------------------------------------------------ |
| **Password**          | Hashed bằng `bcrypt` (cost factor 12), không lưu plain text  |
| **JWT Token**         | Ký bằng `HS256` + `SECRET_KEY`, hết hạn sau 7 ngày           |
| **Session isolation** | Mỗi user chỉ thấy sessions/chats của mình (`user_id` filter) |
| **API Keys**          | Lưu trong `.env`, không commit lên Git                       |
| **`.gitignore`**      | Loại trừ `.env`, `audio_files/`, `*.mp3`, `*.wav`            |

### Checklist trước khi deploy production

- [ ] Đổi `SECRET_KEY` thành chuỗi ngẫu nhiên 32+ ký tự
- [ ] `.env` đã được thêm vào `.gitignore`
- [ ] `DATABASE_URL` trỏ đúng đến production database
- [ ] Đã cấu hình HTTPS (SSL certificate)
- [ ] Supabase Storage đã setup (nếu không dùng Docker volume)
- [ ] GitHub Secrets đã có `OPENAI_API_KEY`, `GROQ_API_KEY` cho CI/CD

---

## 🔄 GitHub Actions CI

File `.github/workflows/ci.yml` tự động chạy khi push lên `main`:

1. Build Docker image backend
2. Build Docker image frontend
3. Start docker-compose stack để validate

### Thêm GitHub Secrets

Vào `GitHub repo` → `Settings` → `Secrets and variables` → `Actions`:

| Secret           | Giá trị           |
| ---------------- | ----------------- |
| `OPENAI_API_KEY` | Key từ OpenAI     |
| `GROQ_API_KEY`   | Key từ Groq       |
| `SECRET_KEY`     | JWT secret        |
| `DATABASE_URL`   | Production DB URL |

---

## 🐛 Troubleshooting

### Lỗi kết nối database

```
could not translate host name "db" to address
```

→ Đang chạy local nhưng `DATABASE_URL` trỏ vào hostname Docker. Sửa `DATABASE_URL` trong `.env` thành `localhost`.

### Audio không phát được

```
Audio playback unavailable
```

→ Backend không serve được file audio. Kiểm tra `audio_files/` có tồn tại không, và FastAPI static mount hoạt động.

### JWT token hết hạn

```
Token đã hết hạn, vui lòng đăng nhập lại
```

→ Đăng xuất và đăng nhập lại. Token mặc định sống 7 ngày.

### Bcrypt error

```
(trapped) error reading bcrypt version
```

→ Xung đột `passlib` + `bcrypt >= 4.0`. Đã được fix bằng cách dùng `bcrypt` trực tiếp (không qua passlib).

### Port đã bị chiếm

```
[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

→ Có process khác dùng port 8000. Chạy `netstat -ano | findstr :8000` để tìm PID, sau đó `taskkill /PID <pid> /F`.

---

## 📄 License

MIT License — Sử dụng tự do cho mục đích cá nhân và thương mại.

---

<div align="center">
Built with ❤️ using FastAPI + Streamlit + GPT-4o-mini
</div>
