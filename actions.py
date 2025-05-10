from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionTimThongTinNganh(Action):
    def name(self) -> Text:
        return "action_tim_thong_tin_nganh"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Lấy thông tin ngành từ slot
        nganh = tracker.get_slot("nganh")
        
        # Cơ sở dữ liệu thông tin ngành
        nganh_info = {
            "An toàn thông tin": {
                "ma_nganh": "8480202",
                "chi_tieu": 21,
                "dieu_kien": "Tốt nghiệp đại học ngành An toàn thông tin hoặc ngành gần"
            },
            "Công nghệ thông tin": {
                "ma_nganh": "8480201",
                "chi_tieu": 49,
                "dieu_kien": "Tốt nghiệp đại học ngành CNTT hoặc ngành gần"
            },
            "Hệ thống thông tin": {
                "ma_nganh": "8480104",
                "chi_tieu": 35,
                "dieu_kien": "Tốt nghiệp đại học ngành HTTT hoặc ngành gần"
            },
            "Khoa học máy tính": {
                "ma_nganh": "8480101",
                "chi_tieu": 63,
                "dieu_kien": "Tốt nghiệp đại học ngành KHMT hoặc ngành gần"
            },
            "Kỹ thuật máy tính": {
                "ma_nganh": "8480106",
                "chi_tieu": 21,
                "dieu_kien": "Tốt nghiệp đại học ngành KTMT hoặc ngành gần"
            }
        }
        
        if nganh and nganh in nganh_info:
            info = nganh_info[nganh]
            response = f"Thông tin về ngành {nganh}:\n"
            response += f"- Mã ngành: {info['ma_nganh']}\n"
            response += f"- Chỉ tiêu: {info['chi_tieu']}\n"
            response += f"- Điều kiện: {info['dieu_kien']}"
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_message(text="Tôi không tìm thấy thông tin về ngành bạn yêu cầu. "
                                     "Các ngành tuyển sinh gồm: An toàn thông tin, Công nghệ thông tin, "
                                     "Hệ thống thông tin, Khoa học máy tính, Kỹ thuật máy tính.")
        
        return [SlotSet("nganh", nganh)]

class ActionTimThongTinChungChi(Action):
    def name(self) -> Text:
        return "action_tim_thong_tin_chung_chi"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Lấy thông tin chứng chỉ từ slot
        chung_chi = tracker.get_slot("chung_chi")
        
        # Cơ sở dữ liệu thông tin chứng chỉ
        chung_chi_info = {
            "IELTS": "IELTS 4.5 trở lên",
            "TOEFL": "TOEFL iBT 45 trở lên",
            "TOEIC": "TOEIC 450 trở lên",
            "B1": "Chứng chỉ B1 theo khung tham chiếu châu Âu",
            "Cambridge": "Cambridge English 140 trở lên"
        }
        
        if chung_chi and chung_chi in chung_chi_info:
            response = f"Thông tin về chứng chỉ {chung_chi}: {chung_chi_info[chung_chi]}"
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_message(text="Các chứng chỉ ngoại ngữ được công nhận: IELTS, TOEFL, TOEIC, B1, Cambridge. "
                                     "Bạn cần đạt mức tối thiểu theo quy định để được miễn thi ngoại ngữ.")
        
        return [SlotSet("chung_chi", chung_chi)]

class ActionTimThongTinLePhi(Action):
    def name(self) -> Text:
        return "action_tim_thong_tin_le_phi"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Cơ sở dữ liệu thông tin lệ phí
        le_phi_info = {
            "xet_tuyen": "260.000 đồng/hồ sơ",
            "thi_tieng_anh": "200.000 đồng",
            "on_tap_tieng_anh": "1.000.000 đồng",
            "nhap_hoc": "Theo quy định của trường"
        }
        
        response = "Thông tin lệ phí tuyển sinh thạc sĩ:\n"
        response += f"- Lệ phí xét tuyển: {le_phi_info['xet_tuyen']}\n"
        response += f"- Lệ phí thi tiếng Anh: {le_phi_info['thi_tieng_anh']}\n"
        response += f"- Lệ phí ôn tập tiếng Anh (nếu đăng ký): {le_phi_info['on_tap_tieng_anh']}\n"
        response += f"- Lệ phí nhập học: {le_phi_info['nhap_hoc']}"
        
        dispatcher.utter_message(text=response)
        
        return []

class ActionTimThongTinLichTrinh(Action):
    def name(self) -> Text:
        return "action_tim_thong_tin_lich_trinh"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Cơ sở dữ liệu thông tin lịch trình
        lich_trinh_info = {
            "nop_ho_so": "01/4/2025 - 30/5/2025",
            "on_tap_tieng_anh": "10/4/2025 - 20/5/2025",
            "thi_tieng_anh": "25/5/2025",
            "phong_van": "05/6/2025 - 10/6/2025",
            "cong_bo_ket_qua": "15/6/2025",
            "nhap_hoc": "01/7/2025 - 15/7/2025",
            "khai_giang": "01/8/2025"
        }
        
        response = "Lịch trình tuyển sinh thạc sĩ năm 2025:\n"
        response += f"- Thời gian nhận hồ sơ: {lich_trinh_info['nop_ho_so']}\n"
        response += f"- Thời gian ôn tập tiếng Anh: {lich_trinh_info['on_tap_tieng_anh']}\n"
        response += f"- Thi đánh giá năng lực tiếng Anh: {lich_trinh_info['thi_tieng_anh']}\n"
        response += f"- Phỏng vấn chuyên môn: {lich_trinh_info['phong_van']}\n"
        response += f"- Công bố kết quả: {lich_trinh_info['cong_bo_ket_qua']}\n"
        response += f"- Nhập học: {lich_trinh_info['nhap_hoc']}\n"
        response += f"- Khai giảng: {lich_trinh_info['khai_giang']}"
        
        dispatcher.utter_message(text=response)
        
        return []
