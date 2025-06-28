import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8003/api/v1',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: false,
  maxRedirects: 5 // Cho phép tự động redirect
})

// Interceptor để xử lý request
apiClient.interceptors.request.use(
  config => {
    // Đảm bảo URL kết thúc bằng dấu / nếu không có tham số query
    if (!config.url.endsWith('/') && !config.url.includes('?') && !config.url.includes('=')) {
      config.url = `${config.url}/`;
    }
    console.log('Request:', config.url)
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Interceptor để xử lý response
apiClient.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // Xử lý lỗi response
    let errorMessage = 'Đã xảy ra lỗi không xác định';

    if (error.response) {
      // Lỗi server trả về (status code không phải 2xx)
      console.error('API Error:', error.response.data);

      // Xử lý thông báo lỗi từ backend
      if (error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response.data && error.response.data.message) {
        errorMessage = error.response.data.message;
      } else if (typeof error.response.data === 'string') {
        errorMessage = error.response.data;
      } else {
        // Xử lý theo status code
        switch (error.response.status) {
          case 400:
            errorMessage = 'Yêu cầu không hợp lệ';
            break;
          case 401:
            errorMessage = 'Không được phép truy cập';
            break;
          case 403:
            errorMessage = 'Bạn không có quyền thực hiện hành động này';
            break;
          case 404:
            errorMessage = 'Không tìm thấy tài nguyên yêu cầu';
            break;
          case 429:
            errorMessage = 'Quá nhiều yêu cầu. Vui lòng thử lại sau';
            break;
          case 500:
            errorMessage = 'Lỗi máy chủ nội bộ';
            break;
          default:
            errorMessage = `Lỗi ${error.response.status}: Vui lòng thử lại sau`;
        }
      }
    } else if (error.request) {
      // Không nhận được response
      console.error('Network Error:', error.request);
      errorMessage = 'Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng của bạn';
    } else {
      // Lỗi khi thiết lập request
      console.error('Request Error:', error.message);
      errorMessage = `Lỗi khi gửi yêu cầu: ${error.message}`;
    }

    // Hiển thị toast thông báo lỗi
    alert(errorMessage);

    // Gán thông báo lỗi vào error để component có thể truy cập dễ dàng
    error.userMessage = errorMessage;

    return Promise.reject(error);
  }
)

export default apiClient
