import { BaseApiService } from './base-api.service'
import RasaIntegrationService from './rasa-integration.service'

export class ChatbotInteractionService {
  constructor() {
    this.rasaService = RasaIntegrationService
  }

  /**
   * Gửi tin nhắn đến chatbot và nhận phản hồi
   * @param {Object} data - Dữ liệu tin nhắn
   * @param {String} data.sender - ID của người gửi
   * @param {String} data.message - Nội dung tin nhắn
   * @param {String} data.session_id - ID của phiên chat (tùy chọn)
   * @returns {Promise} - Promise chứa phản hồi từ chatbot
   */
  sendMessage(data) {
    return this.rasaService.chatWithRasa(data)
  }

  /**
   * Lấy lịch sử tương tác của một người dùng
   * @param {String} userId - ID của người dùng
   * @param {Object} params - Các tham số truy vấn
   * @param {Number} params.limit - Số lượng bản ghi tối đa trả về
   * @param {Number} params.skip - Số lượng bản ghi bỏ qua
   * @returns {Promise} - Promise chứa lịch sử tương tác
   */
  getUserInteractions(userId, params = {}) {
    return this.rasaService.getUserInteractions(userId, params)
  }

  /**
   * Lấy lịch sử tương tác của một phiên chat
   * @param {String} sessionId - ID của phiên chat
   * @param {Object} params - Các tham số truy vấn
   * @param {Number} params.limit - Số lượng bản ghi tối đa trả về
   * @param {Number} params.skip - Số lượng bản ghi bỏ qua
   * @returns {Promise} - Promise chứa lịch sử tương tác
   */
  getSessionInteractions(sessionId, params = {}) {
    return this.rasaService.getSessionInteractions(sessionId, params)
  }

  /**
   * Kiểm tra trạng thái của Rasa server
   * @returns {Promise} - Promise chứa thông tin trạng thái của Rasa server
   */
  checkRasaHealth() {
    return this.rasaService.checkHealth()
  }
}

export default new ChatbotInteractionService()
