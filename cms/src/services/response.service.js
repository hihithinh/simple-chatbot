import { BaseApiService } from './base-api.service'

export class ResponseService extends BaseApiService {
  constructor() {
    super({ urlPrefix: 'responses' })
  }

  /**
   * Lấy danh sách các response
   * @param {Object} params - Các tham số truy vấn
   * @param {Number} params.skip - Số lượng bản ghi bỏ qua
   * @param {Number} params.limit - Số lượng bản ghi tối đa trả về
   * @param {Number} params.intent_id - Lọc theo intent_id
   * @param {Boolean} params.is_active - Lọc theo trạng thái active
   * @returns {Promise} - Promise chứa danh sách response
   */
  getResponses(params = {}) {
    return this.index({ params })
  }

  /**
   * Tạo response mới
   * @param {Object} data - Dữ liệu response cần tạo
   * @returns {Promise} - Promise chứa response đã tạo
   */
  createResponse(data) {
    return this.store({ data })
  }

  /**
   * Lấy thông tin chi tiết của một response
   * @param {Number} id - ID của response
   * @returns {Promise} - Promise chứa thông tin response
   */
  getResponse(id) {
    return this.show({ id })
  }

  /**
   * Cập nhật response
   * @param {Number} id - ID của response
   * @param {Object} data - Dữ liệu cần cập nhật
   * @returns {Promise} - Promise chứa response đã cập nhật
   */
  updateResponse(id, data) {
    return this.update({ id, data })
  }

  /**
   * Xóa response
   * @param {Number} id - ID của response
   * @returns {Promise} - Promise chứa kết quả xóa
   */
  deleteResponse(id) {
    return this.delete({ id })
  }
}

export default new ResponseService()
