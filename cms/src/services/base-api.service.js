import ApiUtil from '@/utils/api.util.js'

export class BaseApiService {
    constructor({ urlPrefix = null, apiVersion = 'v1' } = {}) {
        this.apiUtil = ApiUtil
        this.urlPrefix = urlPrefix
        this.apiVersion = apiVersion
        this.baseUrl = '' // Đã được cấu hình trong axios client
    }

    #setUrlPrefix(urlPrefix) {
        this.urlPrefix = urlPrefix
    }

    #getUrlPrefix() {
        return this.urlPrefix ? `${this.urlPrefix}` : ''
    }

    index({params = {}, configs = {}}) {
        return this.apiUtil.get({
          url: this.#getUrlPrefix(),
          params,
          configs
        })
    }

    filter({params, config = {}} = {}) {
        return this.apiUtil.get({
            url: this.#getUrlPrefix(),
            params,
            config
        })
    }

    store({data, config = {}}) {
        return this.apiUtil.post({
            url: this.#getUrlPrefix(),
            data,
            config
        })
    }

    show({id, config = {}}) {
        return this.apiUtil.get({
            url: `${this.#getUrlPrefix()}/${id}`,
            config
        })
    }

    update({id, data, config = {}}) {
        return this.apiUtil.put({
            url: `${this.#getUrlPrefix()}/${id}`,
            data,
            config,
        })
    }

    delete({id, config = {}}) {
        return this.apiUtil.delete({
            url: `${this.#getUrlPrefix()}/${id}`,
            config,
        })
    }
}
