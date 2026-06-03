# Hướng Dẫn Chạy Travel Chatbot

---

## ⚡ Chạy nhanh — 1 lệnh duy nhất (Backend + Frontend)

> Yêu cầu: Python 3.11+ và Node.js 18+

```powershell
cd "C:\Users\Admin\Downloads\Batch02-Day05-AI-Product-Labs"
.\start.ps1
```

Script sẽ tự động:
1. Tạo `.env` nếu chưa có (copy từ `.env.example`)
2. Tạo virtualenv Python và cài `requirements.txt`
3. Cài `npm install` nếu chưa có `node_modules`
4. Mở **2 terminal riêng** chạy backend và frontend song song

> Lần đầu chạy: mở `.env`, điền API key, rồi chạy lại `.\start.ps1`

---

## Yêu cầu
- **Docker Desktop** → [tải tại đây](https://www.docker.com/products/docker-desktop/) *(Cách 1)*
- **hoặc** Python 3.11+ & Node.js 18+ *(Cách 2)*
- **hoặc** Ollama *(Cách 3 — không cần API key)*

---

## Cách 1: Docker (khuyến nghị)

**Bước 1 — Tạo file `.env` từ template:**
```powershell
cd "C:\Users\Admin\Downloads\Batch02-Day05-AI-Product-Labs"
Copy-Item .env.example .env
```

**Bước 2 — Mở `.env`, điền API key của provider muốn dùng** (chỉ cần 1):
```env
OPENAI_API_KEY=sk-...          # GPT
GEMINI_API_KEY=AIzaSy...       # Gemini (có free tier)
CLAUDE_API_KEY=sk-ant-...      # Claude
OPENROUTER_API_KEY=sk-or-...   # OpenRouter (nhiều model qua 1 key)

# Hoặc không điền gì → tự fallback về Ollama local (xem Cách 3)
```

**Bước 3 — Build & chạy:**
```powershell
docker-compose up --build
```

**Truy cập:**
| URL | Mô tả |
|---|---|
| http://localhost:3000 | Frontend (giao diện chat) |
| http://localhost:8000 | Backend API |
| http://localhost:8000/docs | API Docs (Swagger) |
| http://localhost:8000/health | Kiểm tra provider đang dùng |

**Dừng ứng dụng:**
```powershell
docker-compose down
```

---

## Cách 2: Chạy thủ công (không Docker)

### Backend
```powershell
cd backend

# Tạo virtual environment
python -m venv venv
.\venv\Scripts\activate

# Cài dependencies
pip install -r requirements.txt

# Tạo file .env
Copy-Item ..\.env.example .env
# Mở .env và điền API key

# Chạy server
uvicorn main:app --reload --port 8000
```

### Frontend *(mở terminal mới)*
```powershell
cd frontend
npm install
npm run dev
```

---

## Cách 3: Dùng Ollama (chạy local, miễn phí, không cần API key)

**Bước 1 — Cài Ollama:** https://ollama.com/download

**Bước 2 — Pull model về máy:**
```powershell
ollama pull llama3       # ~4.7GB — recommended
# hoặc các model nhẹ hơn:
ollama pull phi3         # ~2.3GB — nhẹ nhất
ollama pull mistral      # ~4.1GB
ollama pull gemma2       # ~5.4GB
```

**Bước 3 — Cấu hình `.env`:**
```env
AI_PROVIDER=ollama
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

**Bước 4 — Chạy backend & frontend** như Cách 2.

---

## Kiểm tra provider đang dùng

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Kết quả mẫu:
```json
{
  "status": "ok",
  "service": "Travel Chatbot API",
  "ai_provider": "gemini",
  "model": "gemini-1.5-flash"
}
```

---

## Logic auto-detect provider

Nếu không set `AI_PROVIDER` trong `.env`, backend tự chọn theo thứ tự:

```
OPENAI_API_KEY có giá trị  →  dùng OpenAI (GPT)
        ↓ không có
GEMINI_API_KEY có giá trị  →  dùng Gemini
        ↓ không có
CLAUDE_API_KEY có giá trị  →  dùng Claude
        ↓ không có
OPENROUTER_API_KEY có giá trị  →  dùng OpenRouter
        ↓ không có
              →  fallback Ollama local (http://localhost:11434)
                      ↓ Ollama cũng fail
              →  rule-based replies (không cần internet)
```

---

## Danh sách model theo provider

| Provider | Model mặc định | Các model khác |
|---|---|---|
| OpenAI | `gpt-3.5-turbo` | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` |
| Gemini | `gemini-1.5-flash` | `gemini-1.5-pro`, `gemini-2.0-flash` |
| Claude | `claude-3-haiku-20240307` | `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229` |
| OpenRouter | `openai/gpt-3.5-turbo` | `anthropic/claude-3.5-sonnet`, `meta-llama/llama-3.1-8b-instruct:free` |
| Ollama | `llama3` | `mistral`, `phi3`, `gemma2`, `qwen2` |

Đổi model bằng cách thêm vào `.env`, ví dụ:
```env
GEMINI_MODEL=gemini-1.5-pro
```

---

## Lấy API key miễn phí

| Provider | Link | Ghi chú |
|---|---|---|
| Gemini | https://aistudio.google.com/app/apikey | Free tier rộng rãi nhất |
| OpenRouter | https://openrouter.ai/keys | Có model miễn phí (`:free`) |
| OpenAI | https://platform.openai.com/api-keys | Cần nạp credit |
| Claude | https://console.anthropic.com/ | Cần nạp credit |
