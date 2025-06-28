import { BaseApiService } from './base-api.service'

export class RasaIntegrationService extends BaseApiService {
  constructor() {
    super({ urlPrefix: 'rasa/' })
  }

  /**
   * Gửi tin nhắn đến webhook của Rasa
   * @param {Object} data - Dữ liệu tin nhắn
   * @param {String} data.sender - ID của người gửi
   * @param {String} data.message - Nội dung tin nhắn
   * @returns {Promise} - Promise chứa phản hồi từ Rasa
   */
  sendWebhookMessage(data) {
    return this.apiUtil.post({
      url: `${this.urlPrefix}webhook/`,
      data
    })
  }

  /**
   * Chat với Rasa và lưu lịch sử trò chuyện
   * @param {Object} data - Dữ liệu tin nhắn
   * @param {String} data.sender - ID của người gửi
   * @param {String} data.message - Nội dung tin nhắn
   * @param {String} data.session_id - ID của phiên chat (tùy chọn)
   * @returns {Promise} - Promise chứa phản hồi từ Rasa và thông tin phiên chat
   */
  chatWithRasa(data) {
    return this.apiUtil.post({
      url: `${this.urlPrefix}chat/`,
      data
    })
  }

  /**
   * Kiểm tra trạng thái của Rasa server
   * @returns {Promise} - Promise chứa thông tin trạng thái của Rasa server
   */
  checkHealth() {
    return this.apiUtil.get({
      url: `${this.urlPrefix}health/`
    })
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
    return this.apiUtil.get({
      url: `${this.urlPrefix}user-interactions/${userId}/`,
      params
    })
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
    return this.apiUtil.get({
      url: `${this.urlPrefix}session-interactions/${sessionId}/`,
      params
    })
  }

  /**
   * Huấn luyện lại mô hình Rasa với dữ liệu từ cơ sở dữ liệu
   * @returns {Promise} - Promise chứa kết quả huấn luyện
   */
  trainModel() {
    return this.apiUtil.post({
      url: `${this.urlPrefix}train/`,
      data: {}
    })
  }
}

export default new RasaIntegrationService()
