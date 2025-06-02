from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionTimThongTinNganh(Action):
    NGANH_CANONICAL_MAP = {
        # Khoa học máy tính
        "khoa học máy tính": "Khoa học máy tính",
        "khmt": "Khoa học máy tính",
        "khoa hoc may tinh": "Khoa học máy tính",
        # An toàn thông tin
        "an toàn thông tin": "An toàn thông tin",
        "attt": "An toàn thông tin",
        "at": "An toàn thông tin",
        "an toan thong tin": "An toàn thông tin",
        # Công nghệ thông tin
        "công nghệ thông tin": "Công nghệ thông tin",
        "cntt": "Công nghệ thông tin",
        "cnt": "Công nghệ thông tin",
        "cong nghe thong tin": "Công nghệ thông tin",
        # Hệ thống thông tin
        "hệ thống thông tin": "Hệ thống thông tin",
        "httt": "Hệ thống thông tin",
        "ht": "Hệ thống thông tin",
        "he thong thong tin": "Hệ thống thông tin",
        # Kỹ thuật máy tính
        "kỹ thuật máy tính": "Kỹ thuật máy tính",
        "ktmt": "Kỹ thuật máy tính",
        "ky thuat may tinh": "Kỹ thuật máy tính",
    }

    def name(self) -> Text:
        return "action_tim_thong_tin_nganh"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        nganh_entity_original = tracker.get_slot("nganh") # Giữ lại tên gốc
        intent_name = tracker.latest_message['intent'].get('name')

        canonical_nganh_name = None
        if nganh_entity_original:
            normalized_entity = nganh_entity_original.lower()
            canonical_nganh_name = self.NGANH_CANONICAL_MAP.get(normalized_entity)
        
        nganh_info_db = {
            "An toàn thông tin": {
                "ma_nganh": "8480202",
                "chi_tieu": 21,
                "thong_tin_chung": "Ngành An toàn thông tin đào tạo chuyên sâu về bảo vệ hệ thống thông tin, dữ liệu và ứng phó với các tấn công mạng.",
                "dieu_kien": "Tốt nghiệp đại học ngành An toàn thông tin hoặc ngành gần"
            },
            "Công nghệ thông tin": {
                "ma_nganh": "8480201",
                "chi_tieu": 49,
                "thong_tin_chung": "Ngành Công nghệ thông tin cung cấp kiến thức về phát triển phần mềm, quản lý hệ thống và các công nghệ mới.",
                "dieu_kien": "Tốt nghiệp đại học ngành CNTT hoặc ngành gần"
            },
            "Hệ thống thông tin": {
                "ma_nganh": "8480104",
                "chi_tieu": 35,
                "thong_tin_chung": "Ngành Hệ thống thông tin tập trung vào việc phân tích, thiết kế và quản lý các hệ thống thông tin trong doanh nghiệp.",
                "dieu_kien": "Tốt nghiệp đại học ngành HTTT hoặc ngành gần"
            },
            "Khoa học máy tính": {
                "ma_nganh": "8480101",
                "chi_tieu": 63,
                "thong_tin_chung": "Ngành Khoa học máy tính nghiên cứu các cơ sở lý thuyết của thông tin và tính toán, cũng như ứng dụng của chúng.",
                "dieu_kien": "Tốt nghiệp đại học ngành KHMT hoặc ngành gần"
            },
            "Kỹ thuật máy tính": {
                "ma_nganh": "8480106",
                "chi_tieu": 21,
                "thong_tin_chung": "Ngành Kỹ thuật máy tính kết hợp kiến thức của cả phần cứng và phần mềm máy tính.",
                "dieu_kien": "Tốt nghiệp đại học ngành KTMT hoặc ngành gần"
            }
        }
        
        response = "Tôi không tìm thấy thông tin về ngành bạn yêu cầu cho đợt 1 năm 2025. " \
                   "Các ngành tuyển sinh Thạc sĩ đợt 1 năm 2025 (tham khảo) gồm: An toàn thông tin, Công nghệ thông tin, " \
                   "Hệ thống thông tin, Khoa học máy tính, Kỹ thuật máy tính. Vui lòng kiểm tra thông báo tuyển sinh chính thức."

        # Sử dụng canonical_nganh_name để tra cứu
        if canonical_nganh_name and canonical_nganh_name in nganh_info_db:
            info = nganh_info_db[canonical_nganh_name]
            display_name = canonical_nganh_name # Sử dụng tên chuẩn để hiển thị
            
            if intent_name == "hoi_ma_nganh":
                response = f"Mã ngành của {display_name} là: {info['ma_nganh']}."
            elif intent_name == "hoi_chi_tieu_nganh":
                response = f"Chỉ tiêu dự kiến cho ngành {display_name} đợt 1 năm 2025 là: {info['chi_tieu']}."
            elif intent_name == "hoi_thong_tin_chi_tiet_nganh":
                response = f"Thông tin chung về ngành {display_name} (tham khảo cho đợt 1 năm 2025):\n"
                response += f"- Mô tả: {info.get('thong_tin_chung', 'Chưa có thông tin mô tả chi tiết.')}\n"
                response += f"- Mã ngành: {info['ma_nganh']}\n"
                response += f"- Chỉ tiêu dự kiến: {info['chi_tieu']}\n"
                response += f"- Điều kiện chung: {info['dieu_kien']}. (Lưu ý: Đây là thông tin tham khảo, vui lòng xem điều kiện chi tiết và các yêu cầu bổ sung trong thông báo tuyển sinh chính thức đợt 1 năm 2025)."
            # Fallback nếu intent không khớp rõ ràng nhưng slot nganh có giá trị
            else: 
                response = f"Thông tin tuyển sinh Thạc sĩ đợt 1 năm 2025 cho ngành {display_name}:\n"
                response += f"- Mã ngành: {info['ma_nganh']}\n"
                response += f"- Chỉ tiêu dự kiến: {info['chi_tieu']}\n"
                response += f"- Điều kiện chung: {info['dieu_kien']}. (Lưu ý: Đây là thông tin tham khảo, vui lòng xem điều kiện chi tiết và các yêu cầu bổ sung trong thông báo tuyển sinh chính thức đợt 1 năm 2025)."
        elif nganh_entity_original: # Nếu có entity gốc nhưng không map được hoặc không có trong db
            response = f"Tôi không tìm thấy thông tin chi tiết về ngành '{nganh_entity_original}' bạn yêu cầu cho đợt 1 năm 2025. " \
                       f"Các ngành tuyển sinh Thạc sĩ đợt 1 năm 2025 (tham khảo) gồm: An toàn thông tin, Công nghệ thông tin, " \
                       f"Hệ thống thông tin, Khoa học máy tính, Kỹ thuật máy tính. Vui lòng kiểm tra thông báo tuyển sinh chính thức."

        dispatcher.utter_message(text=response)
        
        # Giữ lại slot 'nganh' là tên đã được chuẩn hóa nếu có, nếu không thì giữ tên gốc hoặc None
        # Điều này quan trọng cho các lượt hội thoại tiếp theo
        slot_to_set = canonical_nganh_name if canonical_nganh_name else nganh_entity_original
        return [SlotSet("nganh", slot_to_set)]

class ActionTimThongTinChungChi(Action):
    def name(self) -> Text:
        return "action_tim_thong_tin_chung_chi"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        chung_chi = tracker.get_slot("chung_chi")
        
        chung_chi_info = {
            "IELTS": "IELTS 4.5",
            "TOEFL": "TOEFL iBT 45",
            "TOEIC": "TOEIC Nghe & Đọc 450, Nói 120, Viết 120 (hình thức 4 kỹ năng)",
            "B1": "Chứng chỉ B1 VSTEP (Khung NLNN 6 bậc VN) hoặc tương đương theo quy định của Bộ GD&ĐT",
            "Cambridge": "Cambridge B1 Preliminary (PET) 140 điểm trở lên (hoặc các chứng chỉ Cambridge English tương đương khác theo quy định)"
        }
        
        if chung_chi and chung_chi in chung_chi_info:
            response = f"Điều kiện tham khảo về chứng chỉ {chung_chi} để miễn thi tiếng Anh đầu vào Thạc sĩ đợt 1 năm 2025: {chung_chi_info[chung_chi]}. (Lưu ý: Chứng chỉ cần còn thời hạn 2 năm tính đến ngày đăng ký dự tuyển. Vui lòng kiểm tra danh mục chứng chỉ được chấp nhận và các điều kiện chi tiết trong thông báo tuyển sinh chính thức đợt 1 năm 2025)."
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_message(text="Các chứng chỉ ngoại ngữ thường được xem xét để miễn thi đầu vào Thạc sĩ đợt 1 năm 2025 (tham khảo và cần còn hạn 2 năm): IELTS, TOEFL iBT, TOEIC (4 kỹ năng), B1 VSTEP, Cambridge English. "
                                     "Bạn cần đạt mức điểm tối thiểu theo quy định. Vui lòng xem thông báo tuyển sinh chính thức đợt 1 năm 2025 để biết chi tiết các loại chứng chỉ được chấp nhận và yêu cầu cụ thể.")
        
        return [SlotSet("chung_chi", chung_chi)]

class ActionTimThongTinLePhi(Action):
    def name(self) -> Text:
        return "action_tim_thong_tin_le_phi"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        le_phi_info = {
            "xet_tuyen": "260.000 đồng/hồ sơ",
            "thi_tieng_anh": "200.000 đồng (nếu ứng viên không được miễn ngoại ngữ)",
            "on_tap_tieng_anh": "Khoảng 1.000.000 đồng (tham khảo, chi tiết và đăng ký theo link trong thông báo tuyển sinh)",
            "nhap_hoc": "Theo quy định của trường tại thời điểm nhập học"
        }
        
        response = "Thông tin lệ phí dự kiến cho tuyển sinh Thạc sĩ đợt 1 năm 2025:\n"
        response += f"- Lệ phí xét tuyển: {le_phi_info['xet_tuyen']}\n"
        response += f"- Lệ phí thi tiếng Anh: {le_phi_info['thi_tieng_anh']}\n"
        response += f"- Lệ phí ôn tập tiếng Anh: {le_phi_info['on_tap_tieng_anh']}\n"
        response += f"- Lệ phí nhập học: {le_phi_info['nhap_hoc']}. (Lưu ý: Các mức lệ phí này là tham khảo, vui lòng xem thông báo tuyển sinh chính thức đợt 1 năm 2025 để biết thông tin chính xác và chi tiết nhất)."
        
        dispatcher.utter_message(text=response)
        
        return []

class ActionTimThongTinLichTrinh(Action):
    def name(self) -> Text:
        return "action_tim_thong_tin_lich_trinh"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        lich_trinh_info = {
            "nop_ho_so_lan_1": "Hạn nộp đến 05/5/2025",
            "nop_ho_so_lan_2": "Hạn nộp đến 30/5/2025 (đối với ứng viên đã có văn bằng/chứng chỉ ngoại ngữ)",
            "on_tap_tieng_anh": "14/3/2025 - 03/5/2025",
            "thi_tieng_anh": "Dự kiến 25/5/2025",
            "xet_tuyen_ho_so": "Dự kiến từ 09-13/6/2025",
            "phong_van": "Dự kiến từ 23-27/6/2025",
            "cong_bo_ket_qua": "Dự kiến tháng 7/2025",
            "nhap_hoc": "Dự kiến tháng 8/2025",
            "khai_giang": "Dự kiến tháng 8/2025"
        }
        
        response = "Lịch trình dự kiến tuyển sinh Thạc sĩ đợt 1 năm 2025:\n"
        response += f"- Thời gian nhận hồ sơ (lần 1): {lich_trinh_info['nop_ho_so_lan_1']}\n"
        response += f"- Thời gian nhận hồ sơ (lần 2, có CC ngoại ngữ): {lich_trinh_info['nop_ho_so_lan_2']}\n"
        response += f"- Thời gian ôn tập tiếng Anh: {lich_trinh_info['on_tap_tieng_anh']}\n"
        response += f"- Thi đánh giá năng lực tiếng Anh: {lich_trinh_info['thi_tieng_anh']}\n"
        response += f"- Xét tuyển hồ sơ: {lich_trinh_info['xet_tuyen_ho_so']}\n"
        response += f"- Phỏng vấn chuyên môn: {lich_trinh_info['phong_van']}\n"
        response += f"- Công bố kết quả: {lich_trinh_info['cong_bo_ket_qua']}\n"
        response += f"- Nhập học: {lich_trinh_info['nhap_hoc']}\n"
        response += f"- Khai giảng: {lich_trinh_info['khai_giang']}. (Lưu ý: Đây là lịch trình dự kiến, vui lòng theo dõi thông báo tuyển sinh chính thức đợt 1 năm 2025 để biết thông tin chính xác và cập nhật nhất)."
        
        dispatcher.utter_message(text=response)
        
        return []
