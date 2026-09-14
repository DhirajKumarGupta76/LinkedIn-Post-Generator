import axios from 'axios'

let accessToken = null
let isRefreshing = false
let refreshSubscribers = []

const onRefreshSuccess = (token) => {
  refreshSubscribers.forEach((callback) => callback(token))
  refreshSubscribers = []
}

const onRefreshError = (error) => {
  refreshSubscribers.forEach((callback) => callback(error))
  refreshSubscribers = []
}

export const setAccessToken = (token) => {
  accessToken = token
}

export const clearAccessToken = () => {
  accessToken = null
  delete api.defaults.headers.common.Authorization
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 10000,
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config || {}

    if (error.response?.status === 429) {
      return Promise.reject(error)
    }

    if (originalRequest.url?.includes('/auth/refresh') || originalRequest.url?.includes('/auth/login')) {
      return Promise.reject(error)
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshSubscribers.push((tokenOrError) => {
            if (tokenOrError instanceof Error || (tokenOrError && tokenOrError.response)) {
              reject(tokenOrError)
            } else {
              originalRequest.headers = originalRequest.headers || {}
              originalRequest.headers.Authorization = `Bearer ${tokenOrError}`
              resolve(api(originalRequest))
            }
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const response = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'}/auth/refresh`,
          {},
          { withCredentials: true },
        )

        const nextAccessToken = response.data.access_token
        setAccessToken(nextAccessToken)
        api.defaults.headers.common.Authorization = `Bearer ${nextAccessToken}`
        onRefreshSuccess(nextAccessToken)
        originalRequest.headers = originalRequest.headers || {}
        originalRequest.headers.Authorization = `Bearer ${nextAccessToken}`
        return api(originalRequest)
      } catch (refreshError) {
        onRefreshError(refreshError)
        clearAccessToken()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  },
)

export const healthCheck = async () => api.get('/health')
export const loginUser = async (payload) => api.post('/auth/login', payload)
export const registerUser = async (payload) => api.post('/auth/register', payload)
export const getGoogleLoginUrl = async () => api.get('/auth/google/login-url')
export const verifyEmail = async (token) => api.get(`/auth/verify-email?token=${encodeURIComponent(token)}`)
export const resendVerification = async (email) => api.post('/auth/resend-verification', { email })
export const logoutUser = async () => api.post('/auth/logout')
export const getCurrentUser = async () => api.get('/users/me')
export const updateCurrentUser = async (payload) => api.put('/users/me', payload)
export const changePassword = async (payload) => api.post('/auth/change-password', payload)

export default api
