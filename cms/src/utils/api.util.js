import axiosInstance from '@/plugins/axios.js'

class ApiUtil {
  constructor() {
  }

  get({url, params = {}, configs = {}}) {
    return axiosInstance.get(`${url}`, {...configs, params})
  }

  post({url, data, config = {}}) {
    return axiosInstance.post(`${url}`, data, config)
  }

  put({url, data, params = {}}) {
    return axiosInstance.put(`${url}`, data, {params})
  }

  delete({url, data, params = {}}) {
    if (data) {
      params.data = data
    }

    return axiosInstance.delete(url, params)
  }

  parseErrorForForm(error) {
    const result = {
      message: null,
      errors: {}
    }

    result.message = error?.response?.data?.message ?? error?.response?.data?.error?.message ?? error?.message

    const errors = error?.response?.data?.errors
    if (errors?.length) {
      errors.forEach((error) => {
        result.errors[error.field] = error.message
      })
    }

    return result;
  }
}

const util = new ApiUtil()

export default util
