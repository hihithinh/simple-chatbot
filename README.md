# Chatbot Tuyển Sinh Thạc Sĩ UIT

Chatbot hỗ trợ tư vấn tuyển sinh thạc sĩ Trường Đại học CNTT (UIT) – Đại học Quốc gia TP.HCM. Hệ thống sử dụng Rasa và giao diện web thân thiện, có thể chạy hoàn toàn trên máy cá nhân hoặc chia sẻ qua internet.

## 1. Yêu cầu hệ thống
- Python 3.8+
- pip, venv (quản lý môi trường ảo)
- SSH client (có sẵn trên macOS/Linux)
- PostgreSQL (cho CMS và backend)

## 2. Cài đặt

### Bước 1: Clone và tạo môi trường ảo
```bash
git clone <repo-url>
cd chatbot
python3 -m venv .venv
source .venv/bin/activate
```

### Bước 2: Cài đặt các thư viện Python
```bash
source .venv/bin/activate && pip install -r requirements.txt
```

### Bước 3: Cấu hình biến môi trường
```bash
# Sao chép file .env.example thành .env
source .venv/bin/activate && cp .env.example .env

# Chỉnh sửa file .env theo môi trường của bạn
nano .env

# Tải biến môi trường và cập nhật cấu hình Rasa
source .venv/bin/activate && python load_env.py --update-rasa
```

### Bước 4: Train mô hình Rasa
```bash
source .venv/bin/activate && cd rasa && rasa train
```

---

## 3. Chạy chatbot và chia sẻ qua internet (serveo.net)

Bạn cần mở **4 terminal riêng biệt** (mỗi lệnh chạy ở một terminal khác nhau):

**1. Khởi động Rasa Action Server (port 5055)**  
(Mở terminal **thứ nhất**)
```bash
source .venv/bin/activate && cd rasa && rasa run actions --cors "*"
```

**2. Khởi động Rasa Server (port 5005)**  
(Mở terminal **thứ hai**)
```bash
source .venv/bin/activate && cd rasa && rasa run --enable-api --cors "*"
```

**3. Khởi động proxy phục vụ cả UI và API trên cùng một domain (port 5006)**  
(Mở terminal **thứ ba**)
```bash
source .venv/bin/activate && cd rasa && python cors_proxy.py
```

**4. Mở tunnel chia sẻ ra internet với serveo.net**  
(Mở terminal **thứ tư**)
```bash
ssh -R mychatbot:80:localhost:5006 serveo.net
```
Bạn có thể thay `mychatbot` bằng tên bất kỳ hoặc bỏ qua để serveo tự sinh.

---

## 4. Chạy FastAPI Backend và CMS

**1. Khởi động FastAPI Backend (port 8000)**  
(Mở terminal mới)
```bash
source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**2. Truy cập API Documentation**  
Mở trình duyệt và truy cập:
```
http://localhost:8000/docs
```

**3. Truy cập API Redoc**  
Mở trình duyệt và truy cập:
```
http://localhost:8000/redoc
```

---

## 5. Chạy Rasa server
```bash
source .venv/bin/activate && cd rasa && rasa run --enable-api
```

## 6. Chạy Rasa Action server (trong terminal khác)
```bash
source .venv/bin/activate && cd rasa && rasa run actions
```

## 7. Chạy FastAPI backend (trong terminal khác)
```bash
source .venv/bin/activate && uvicorn app.main:app --reload
```

---

## 8. Truy cập và chia sẻ chatbot
- Mở trình duyệt và truy cập:
  ```
  https://mychatbot.serveo.net
  ```
- Giao diện web và API đều cùng domain, không bị CORS, có thể chia sẻ link này cho team hoặc người dùng từ xa.

---

## 9. Cấu trúc thư mục chính & mô tả các file Rasa

```
chatbot/
├── app/                # Thư mục chứa mã nguồn FastAPI Backend
│   ├── api/            # API endpoints
│   │   ├── api_v1/     # API version 1
│   │   │   ├── endpoints/  # Các endpoint cụ thể
│   ├── core/           # Cấu hình core
│   ├── db/             # Database models và migrations
│   │   ├── migrations/ # Alembic migrations
│   │   ├── models/     # SQLModel models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── main.py         # Entry point cho FastAPI
├── rasa/                # Thư mục chứa mã nguồn Rasa
│   ├── actions/         # Custom actions cho Rasa
│   │   ├── __init__.py
│   │   ├── actions.py   # Python code logic động
│   ├── config.yml       # Cấu hình pipeline NLU, policy hội thoại
│   ├── credentials.yml  # Cấu hình kênh giao tiếp (REST, Telegram...)
│   ├── custom_components/# Các thành phần tùy chỉnh
│   ├── data/            # Dữ liệu huấn luyện và điều khiển hội thoại
│   │   ├── nlu.yml      # Dữ liệu huấn luyện NLU (intent, entity, ví dụ)
│   │   ├── rules.yml    # Quy tắc hội thoại (rule-based)
│   │   ├── stories.yml  # Kịch bản hội thoại nhiều bước (story-based)
│   │   └── ...          # Có thể có thêm: test_stories.yml, lookup tables, synonyms...
│   ├── domain.yml       # Định nghĩa intent, entity, slot, response, action, form...
│   ├── endpoints.yml    # Cấu hình endpoint cho action server, tracker store, ...
│   ├── cors_proxy.py    # Proxy phục vụ cả UI và API (giao tiếp 1 domain)
│   ├── static/          # Thư mục chứa UI: index.html, script.js, style.css
│   └── models/          # File mô hình đã train (.tar.gz)
├── alembic.ini          # Cấu hình Alembic
├── .venv/               # Môi trường ảo Python
├── requirements.txt     # Thư viện Python cần thiết
└── README.md            # Hướng dẫn sử dụng, cấu trúc, lưu ý
```

### Giải thích chi tiết các file chính của Rasa:

- **domain.yml:** Trái tim của chatbot, định nghĩa intent, entity, slot, response, action, form.
- **data/nlu.yml:** Dữ liệu huấn luyện NLU (ý định, thực thể, ví dụ câu hỏi thực tế).
- **data/rules.yml:** Quy tắc hội thoại ngắn, phản xạ nhanh (rule-based).
- **data/stories.yml:** Kịch bản hội thoại phức tạp, nhiều bước (story-based).
- **data/test_stories.yml:** (tuỳ chọn) Kịch bản kiểm thử hội thoại tự động.
- **config.yml:** Cấu hình pipeline xử lý ngôn ngữ, policy hội thoại.
- **actions.py:** Custom actions (Python), xử lý logic phức tạp, truy vấn DB, sinh câu trả lời động.
- **credentials.yml:** Cấu hình kênh giao tiếp (REST, Facebook, Telegram, ...).
- **endpoints.yml:** Cấu hình endpoint cho action server, tracker store, event broker.
- **requirements.txt:** Danh sách thư viện Python cần thiết cho project.
- **models/:** Chứa mô hình đã train (`rasa train` sinh ra file .tar.gz tại đây).
- **static/:** (Nếu có UI web) Chứa file giao diện web (HTML, JS, CSS).
- **cors_proxy.py:** Proxy giúp truy cập UI & API cùng domain, tránh lỗi CORS khi chia sẻ internet.

### Giải thích chi tiết các file chính của FastAPI Backend:

- **app/main.py:** Entry point cho FastAPI application.
- **app/core/config.py:** Cấu hình cho application, database, etc.
- **app/db/models/:** SQLModel models cho database.
- **app/db/migrations/:** Alembic migrations cho database.
- **app/schemas/:** Pydantic schemas cho API.
- **app/api/api_v1/endpoints/:** API endpoints.

**Lưu ý:**
- Thư mục `data/` có thể chứa thêm các file như `lookup_tables.yml`, `synonyms.yml`, `test_stories.yml` tuỳ nhu cầu phát triển.
- Các file/thư mục như `.venv/`, `logs/`, `.gitignore`, `.rasa/`, `.idea/`... là file hệ thống/phát triển, không bắt buộc.

---

## 10. Quản lý dữ liệu Rasa

### Nhập dữ liệu Rasa vào Database

Dự án sử dụng một seeder script để nhập dữ liệu từ các file YAML của Rasa vào database. Các file YAML được lưu trữ trong thư mục `app/db/seeders/rasa_data`.

Để chạy seeder và nhập dữ liệu vào database:

```bash
source .venv/bin/activate && python -m app.db.seeders.rasa_seeder
```

Script này sẽ:
- Đọc dữ liệu từ các file `nlu.yml`, `domain.yml`, `rules.yml`, `stories.yml`
- Xóa dữ liệu cũ trong database (nếu có)
- Nhập dữ liệu mới vào các bảng tương ứng

### Xuất dữ liệu từ Database thành file Rasa

Để xuất dữ liệu từ database thành các file YAML cho Rasa:

```bash
source .venv/bin/activate && python -m app.db.exporters.rasa_exporter
```

Script này sẽ:
- Đọc dữ liệu từ database
- Tạo các file YAML tương ứng trong thư mục `rasa` và `rasa/data`
- Các file được tạo ra bao gồm: `domain.yml`, `data/nlu.yml`, `data/rules.yml`, `data/stories.yml`

Sau khi xuất dữ liệu, bạn có thể sử dụng các file này để train lại mô hình Rasa.

---

## 11. Một số lưu ý & troubleshooting
- **Mỗi lệnh cần chạy ở một terminal riêng biệt** để dễ quản lý và dừng tiến trình.
- Đảm bảo cả 4 tiến trình đều đang chạy trước khi truy cập chatbot.
- Nếu gặp lỗi CORS, kiểm tra lại proxy và URL truy cập.
- Nếu gặp lỗi port đã dùng, hãy kiểm tra và dừng các tiến trình cũ.
- Để dừng server, chỉ cần nhấn `Ctrl+C` tại terminal tương ứng.
- Nếu muốn chạy local, chỉ cần truy cập `http://localhost:5006` (bỏ qua bước 4).
- Nếu gặp lỗi khi push lên git, kiểm tra branch và commit đúng.
- Để loại trừ file không cần thiết khỏi git, đã có sẵn `.gitignore`.

---

Nếu cần bổ sung hướng dẫn chi tiết hoặc gặp vấn đề khi chạy, hãy liên hệ để được hỗ trợ!
