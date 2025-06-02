Mục tiêu: Xây dựng một cơ sở dữ liệu đơn giản, đủ để quản lý dữ liệu cào từ một vài nguồn, lưu trữ nội dung trích xuất, và quản lý dữ liệu cơ bản để sinh "kịch bản" cho một chatbot RASA duy nhất, phục vụ công tác tuyển sinh thạc sĩ của trường UIT.
1. Bảng data_sources
* Mô tả: Quản lý các nguồn dữ liệu đầu vào (URLs, PDFs) cho chatbot.
    * id (SERIAL PRIMARY KEY): Mã định danh duy nhất của nguồn dữ liệu.
    * source_type (VARCHAR(50) NOT NULL): Loại nguồn dữ liệu. Các giá trị hợp lệ: 'web_url', 'pdf_file'.
    * source_identifier (TEXT NOT NULL): URL hoặc tên file (hoặc đường dẫn tới file đã lưu).
    * description (TEXT): Mô tả chi tiết hơn về nguồn dữ liệu.
    * crawl_status (VARCHAR(50) DEFAULT 'pending'): Trạng thái của quá trình thu thập dữ liệu từ nguồn này. Các giá trị hợp lệ: 'pending', 'crawling', 'completed', 'failed'.
    * last_crawled_at (TIMESTAMP WITH TIME ZONE): Thời điểm cuối cùng mà dữ liệu từ nguồn này được thu thập/xử lý.
    * created_at (TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP): Thời điểm nguồn dữ liệu được thêm vào hệ thống.
* Đề Xuất Index:
    * source_type
    * crawl_status
2. Bảng crawled_content
* Mô tả: Lưu trữ nội dung văn bản đã được trích xuất từ các data_sources.
    * id (SERIAL PRIMARY KEY): Mã định danh duy nhất của nội dung đã cào.
    * data_source_id (INTEGER NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE): Khóa ngoại, liên kết đến nguồn dữ liệu mà nội dung này được trích xuất từ đó.
    * extracted_text (TEXT): Toàn bộ nội dung văn bản đã được trích xuất từ nguồn.
    * extracted_at (TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP): Thời điểm văn bản được trích xuất.
    * processing_status_rasa (VARCHAR(50) DEFAULT 'pending'): Trạng thái của quá trình xử lý nội dung này để gợi ý hoặc chuẩn bị dữ liệu huấn luyện cho RASA. Các giá trị hợp lệ: 'pending', 'processed'.
* Đề Xuất Index:
    * data_source_id
    * processing_status_rasa
3. Bảng rasa_intents
* Mô tả: Định nghĩa các ý định (intent) của người dùng mà chatbot cần hiểu.
    * id (SERIAL PRIMARY KEY): Mã định danh duy nhất của intent.
    * name (VARCHAR(255) NOT NULL UNIQUE): Tên của intent (ví dụ: hoi_thong_tin_tuyen_sinh_ths, hoi_hoc_phi). Tên này là duy nhất.
    * description (TEXT): Mô tả chi tiết về ý nghĩa và mục đích của intent.
* Đề Xuất Index:
    * name (Ràng buộc UNIQUE tự động tạo index)
4. Bảng rasa_nlu_examples
* Mô tả: Lưu trữ các câu ví dụ (utterances) mà người dùng có thể nói, dùng để huấn luyện mô hình NLU của RASA.
    * id (SERIAL PRIMARY KEY): Mã định danh duy nhất của ví dụ NLU.
    * intent_id (INTEGER REFERENCES rasa_intents(id) ON DELETE SET NULL): Khóa ngoại, liên kết đến intent mà câu ví dụ này minh họa. Có thể NULL nếu ví dụ chỉ dùng để trích xuất entity hoặc chưa được phân loại intent.
    * text (TEXT NOT NULL): Nội dung câu ví dụ của người dùng.
    * entities_json (JSONB): Mảng các đối tượng JSON mô tả các thực thể được đánh dấu trong text. Ví dụ: [{"entity": "program_name", "value": "Thạc sĩ CNTT", "start": 10, "end": 22}]. (Ban đầu có thể không cần bảng rasa_entities riêng, tên entity được định nghĩa ở đây và tổng hợp vào domain).
    * source_type (VARCHAR(50) DEFAULT 'manual'): Nguồn gốc của ví dụ. Các giá trị có thể: 'manual' (nhập tay), 'suggested_from_crawl' (gợi ý từ dữ liệu cào).
    * review_status (VARCHAR(50) DEFAULT 'pending'): Trạng thái duyệt của ví dụ, quan trọng cho quy trình quản lý dữ liệu. Các giá trị hợp lệ: 'pending', 'approved'.
* Đề Xuất Index:
    * intent_id
    * review_status
    * entities_json (GIN index nếu cần truy vấn sâu vào nội dung JSON, ví dụ tìm các example có chứa một entity cụ thể)
5. Bảng rasa_responses
* Mô tả: Định nghĩa các câu trả lời (utterances) mà chatbot có thể sử dụng.
    * id (SERIAL PRIMARY KEY): Mã định danh duy nhất của response.
    * name (VARCHAR(255) NOT NULL UNIQUE): Tên của response (ví dụ: utter_tra_loi_hoc_phi_ths, utter_chao_hoi). Tên này là duy nhất.
    * text_variations_json (JSONB NOT NULL): Mảng các đối tượng JSON, mỗi đối tượng đại diện cho một biến thể của câu trả lời. Ví dụ: [{"text": "Học phí chương trình Thạc sĩ là X triệu đồng mỗi học kỳ."}].
* Đề Xuất Index:
    * name (Ràng buộc UNIQUE tự động tạo index)
6. Bảng rasa_stories
* Mô tả: Định nghĩa các kịch bản hội thoại mẫu (stories) để huấn luyện mô hình quản lý hội thoại của RASA.
    * id (SERIAL PRIMARY KEY): Mã định danh duy nhất của story.
    * name (VARCHAR(255) NOT NULL UNIQUE): Tên của story. Tên này là duy nhất.
    * steps_json (JSONB NOT NULL): Mảng các đối tượng JSON mô tả các bước trong story. Mỗi bước có thể là một intent của người dùng hoặc một action (response) của bot. Ví dụ: [{"intent": "hoi_hoc_phi_ths"}, {"action": "utter_tra_loi_hoc_phi_ths"}].
    * review_status (VARCHAR(50) DEFAULT 'pending'): Trạng thái duyệt của story. Các giá trị hợp lệ: 'pending', 'approved'.
* Đề Xuất Index:
    * name (Ràng buộc UNIQUE tự động tạo index)
    * review_status
    * steps_json (GIN index nếu cần tìm kiếm trong các bước của story)
7. Bảng rasa_rules 
* Mô tả: Định nghĩa các quy tắc (rules) xử lý hội thoại, thường dùng cho các tình huống đơn giản, có điều kiện và không cần học máy.
    * id (SERIAL PRIMARY KEY): Mã định danh duy nhất của rule.
    * name (VARCHAR(255) NOT NULL UNIQUE): Tên của rule. Tên này là duy nhất.
    * steps_json (JSONB NOT NULL): Mảng các đối tượng JSON mô tả các bước (thường là action của bot) sẽ được thực hiện khi rule được kích hoạt.
* Đề Xuất Index:
    * name (Ràng buộc UNIQUE tự động tạo index)
8. Bảng rasa_entities 
* Mô tả: Định nghĩa các thực thể (entity) mà chatbot cần nhận diện cho một dự án RASA cụ thể.
    * id (SERIAL PRIMARY KEY): Mã định danh.
    * name (VARCHAR(255) NOT NULL): Tên entity.
    * description (TEXT): Mô tả.
    * created_at, updated_at.
9. Bảng rasa_domain_elements
* Mô tả: Quản lý các thành phần khác trong file domain của RASA như slots, forms, khai báo tên actions, và cấu hình session cho một dự án cụ thể.
    * id (SERIAL PRIMARY KEY): Mã định danh.
    * element_type (VARCHAR(50) NOT NULL): Loại thành phần (ví dụ: 'slot', 'form', 'action', 'session_config').
    * name (VARCHAR(255) NOT NULL): Tên của slot, form, action, hoặc khóa cấu hình.
    * config_json (JSONB NOT NULL): Cấu hình chi tiết của thành phần dưới dạng JSON.
    * is_active (BOOLEAN DEFAULT TRUE): Cho biết thành phần có đang được sử dụng hay không.
    * created_at, updated_at.
* Đề Xuất Index:
    * is_active
    * UNIQUE (element_type, name)
10. Bảng chatbot_interactions_log 
* Mô tả: Ghi lại lịch sử các cuộc hội thoại giữa người dùng và chatbot của từng dự án.
    * id (SERIAL PRIMARY KEY): Mã định danh.
    * session_id (VARCHAR(255) NOT NULL): Mã định danh phiên hội thoại.
    * user_message (TEXT): Tin nhắn của người dùng.
    * bot_response_json (JSONB): Phản hồi đầy đủ của bot (text, buttons, custom payloads).
    * intent_name (VARCHAR(255)): Intent được RASA NLU nhận diện.
    * entities_json (JSONB): Entities được RASA NLU trích xuất.
    * confidence_score (FLOAT): Độ tin cậy nhận diện intent.
    * timestamp (TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP): Thời điểm tương tác.
* Đề Xuất Index:
    * session_id
    * timestamp
    * intent_name
Ghi chú cho Giai đoạn 1:
* Thiết kế này tập trung vào sự đơn giản và các bảng cốt lõi để chatbot RASA cho đồ án có thể hoạt động.
* Các cột *_json sẽ lưu trữ cấu trúc dữ liệu cần thiết cho RASA.
* Bảng rasa_entities có thể được thêm vào nếu việc quản lý tập trung các loại thực thể là cần thiết ngay từ đầu cho đồ án. Nếu không, thông tin entity có thể được quản lý trong rasa_nlu_examples.entities_json và được tổng hợp khi sinh file domain.
* Các bảng phức tạp hơn như rasa_domain_elements (cho slots, forms, actions), rasa_training_jobs, chatbot_interactions_log, pdf_extracted_elements sẽ được xem xét ở Giai đoạn 2.

