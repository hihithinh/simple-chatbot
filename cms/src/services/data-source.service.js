import { BaseApiService } from './base-api.service'

class DataSourceService extends BaseApiService {
  constructor() {
    super({
      urlPrefix: 'data-sources'
    })
  }

  crawlUrl(url, name = '', description = '') {
    return this.apiUtil.post({
      url: `${this.urlPrefix}/crawl/`,
      data: { url, name, description }
    })
  }

  getWithContent(id) {
    return this.apiUtil.get({
      url: `${this.urlPrefix}/${id}/content/`
    })
  }
}

export default new DataSourceService()
