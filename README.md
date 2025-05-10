# Chatbot Tuyển Sinh Thạc Sĩ UIT

Chatbot hỗ trợ tư vấn tuyển sinh thạc sĩ Trường Đại học CNTT (UIT) – Đại học Quốc gia TP.HCM. Hệ thống sử dụng Rasa và giao diện web thân thiện, có thể chạy hoàn toàn trên máy cá nhân hoặc chia sẻ qua internet.

## 1. Yêu cầu hệ thống
- Python 3.8+
- pip, venv (quản lý môi trường ảo)
- SSH client (có sẵn trên macOS/Linux)

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
pip install -r requirements.txt
```

### Bước 3: Train mô hình Rasa
```bash
rasa train
```

---

## 3. Chạy chatbot và chia sẻ qua internet (serveo.net)

Bạn cần mở **4 terminal riêng biệt** (mỗi lệnh chạy ở một terminal khác nhau):

**1. Khởi động Rasa Action Server (port 5055)**  
(Mở terminal **thứ nhất**)
```bash
rasa run actions --cors "*"
```

**2. Khởi động Rasa Server (port 5005)**  
(Mở terminal **thứ hai**)
```bash
rasa run --enable-api --cors "*"
```

**3. Khởi động proxy phục vụ cả UI và API trên cùng một domain (port 5006)**  
(Mở terminal **thứ ba**)
```bash
python cors_proxy.py
```

**4. Mở tunnel chia sẻ ra internet với serveo.net**  
(Mở terminal **thứ tư**)
```bash
ssh -R mychatbot:80:localhost:5006 serveo.net
```
Bạn có thể thay `mychatbot` bằng tên bất kỳ hoặc bỏ qua để serveo tự sinh.

---

## 4. Truy cập và chia sẻ chatbot
- Mở trình duyệt và truy cập:
  ```
  https://mychatbot.serveo.net
  ```
- Giao diện web và API đều cùng domain, không bị CORS, có thể chia sẻ link này cho team hoặc người dùng từ xa.

---

## 5. Cấu trúc thư mục chính & mô tả các file Rasa

```
chatbot/
├── actions.py           # Custom actions cho Rasa (Python code logic động)
├── config.yml           # Cấu hình pipeline NLU, policy hội thoại
├── credentials.yml      # Cấu hình kênh giao tiếp (REST, Telegram...)
├── data/                # Dữ liệu huấn luyện và điều khiển hội thoại
│   ├── nlu.yml          # Dữ liệu huấn luyện NLU (intent, entity, ví dụ)
│   ├── rules.yml        # Quy tắc hội thoại (rule-based)
│   ├── stories.yml      # Kịch bản hội thoại nhiều bước (story-based)
│   └── ...              # Có thể có thêm: test_stories.yml, lookup tables, synonyms...
├── domain.yml           # Định nghĩa intent, entity, slot, response, action, form...
├── endpoints.yml        # Cấu hình endpoint cho action server, tracker store, ...
├── requirements.txt     # Thư viện Python cần thiết
├── cors_proxy.py        # Proxy phục vụ cả UI và API (giao tiếp 1 domain)
├── static/              # Thư mục chứa UI: index.html, script.js, style.css
├── models/              # File mô hình đã train (.tar.gz)
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

**Lưu ý:**
- Thư mục `data/` có thể chứa thêm các file như `lookup_tables.yml`, `synonyms.yml`, `test_stories.yml` tuỳ nhu cầu phát triển.
- Các file/thư mục như `.venv/`, `logs/`, `.gitignore`, `.rasa/`, `.idea/`... là file hệ thống/phát triển, không bắt buộc.

---

## 6. Một số lưu ý & troubleshooting
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
