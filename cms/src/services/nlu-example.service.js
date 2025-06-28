import { BaseApiService } from './base-api.service'

export class NluExampleService extends BaseApiService {
  constructor() {
    super({ urlPrefix: 'nlu-examples' })
  }

  /**
   * Lấy danh sách các NLU examples
   * @param {Object} params - Các tham số truy vấn
   * @param {Number} params.skip - Số lượng bản ghi bỏ qua
   * @param {Number} params.limit - Số lượng bản ghi tối đa trả về
   * @param {Number} params.intent_id - Lọc theo intent_id
   * @param {Boolean} params.is_active - Lọc theo trạng thái active
   * @returns {Promise} - Promise chứa danh sách NLU examples
   */
  getNluExamples(params = {}) {
    return this.index({ params })
  }

  /**
   * Tạo NLU example mới
   * @param {Object} data - Dữ liệu NLU example cần tạo
   * @returns {Promise} - Promise chứa NLU example đã tạo
   */
  createNluExample(data) {
    return this.store({ data })
  }

  /**
   * Lấy thông tin chi tiết của một NLU example
   * @param {Number} id - ID của NLU example
   * @returns {Promise} - Promise chứa thông tin NLU example
   */
  getNluExample(id) {
    return this.show({ id })
  }

  /**
   * Cập nhật NLU example
   * @param {Number} id - ID của NLU example
   * @param {Object} data - Dữ liệu cần cập nhật
   * @returns {Promise} - Promise chứa NLU example đã cập nhật
   */
  updateNluExample(id, data) {
    return this.update({ id, data })
  }

  /**
   * Xóa NLU example
   * @param {Number} id - ID của NLU example
   * @returns {Promise} - Promise chứa kết quả xóa
   */
  deleteNluExample(id) {
    return this.delete({ id })
  }
}

export default new NluExampleService()
