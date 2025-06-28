import { BaseApiService } from './base-api.service'

class QAGeneratorService extends BaseApiService {
  constructor() {
    super({
      urlPrefix: 'qa-generator/'
    })
  }

  extractKeyPoints(dataSourceId, previousPoints = []) {
    return this.apiUtil.post({
      url: `${this.urlPrefix}extract-key-points/${dataSourceId}/`,
      data: { previous_points: previousPoints }
    })
  }

  createIntents(dataSourceId, keyPoints) {
    return this.apiUtil.post({
      url: `${this.urlPrefix}create-intents/${dataSourceId}/`,
      data: keyPoints
    })
  }

  generateNluExamples(intentId) {
    return this.apiUtil.post({
      url: `${this.urlPrefix}generate-nlu-examples/`,
      data: { intent_id: intentId }
    })
  }

  bulkGenerateNluExamples(intentIds) {
    return this.apiUtil.post({
      url: `${this.urlPrefix}bulk-generate-nlu-examples/`,
      data: { intent_ids: intentIds }
    })
  }

  getIntentsForDataSource(dataSourceId) {
    return this.apiUtil.get({
      url: `${this.urlPrefix}intents/${dataSourceId}/`
    })
  }
}

export default new QAGeneratorService()
