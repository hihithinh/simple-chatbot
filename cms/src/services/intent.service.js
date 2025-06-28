import { BaseApiService } from './base-api.service'

export class IntentService extends BaseApiService {
  constructor() {
    super({ urlPrefix: 'intents' })
  }

  /**
   * Lấy danh sách các intent
   * @param {Object} params - Các tham số truy vấn
   * @param {Number} params.skip - Số lượng bản ghi bỏ qua
   * @param {Number} params.limit - Số lượng bản ghi tối đa trả về
   * @param {Boolean} params.is_active - Lọc theo trạng thái active
   * @returns {Promise} - Promise chứa danh sách intent
   */
  getIntents(params = {}) {
    return this.index({ params })
  }

  /**
   * Tạo intent mới
   * @param {Object} data - Dữ liệu intent cần tạo
   * @returns {Promise} - Promise chứa intent đã tạo
   */
  createIntent(data) {
    return this.store({ data })
  }

  /**
   * Lấy thông tin chi tiết của một intent
   * @param {Number} id - ID của intent
   * @returns {Promise} - Promise chứa thông tin intent
   */
  getIntent(id) {
    return this.show({ id })
  }

  /**
   * Cập nhật intent
   * @param {Number} id - ID của intent
   * @param {Object} data - Dữ liệu cần cập nhật
   * @returns {Promise} - Promise chứa intent đã cập nhật
   */
  updateIntent(id, data) {
    return this.update({ id, data })
  }

  /**
   * Xóa intent
   * @param {Number} id - ID của intent
   * @returns {Promise} - Promise chứa kết quả xóa
   */
  deleteIntent(id) {
    return this.delete({ id })
  }
}

export default new IntentService()
