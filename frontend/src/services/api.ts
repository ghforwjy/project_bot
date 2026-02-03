import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log(`[API请求] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('[API请求错误]', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log(`[API响应] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.status)
    return response
  },
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('[API超时]', error.config?.url, error.message)
    } else if (error.response) {
      console.error('[API错误响应]', error.config?.url, error.response.status, error.response.data)
    } else if (error.request) {
      console.error('[API无响应]', error.config?.url, '服务器未响应')
    } else {
      console.error('[API错误]', error.message)
    }
    return Promise.reject(error)
  }
)

export default api
