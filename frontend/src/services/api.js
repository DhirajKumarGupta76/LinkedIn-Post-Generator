import axios from 'axios'

let accessToken = null

export const setAccessToken = (token) => {
  accessToken = token
}

export const clearAccessToken = () => {
  accessToken = null
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
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const response = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'}/auth/refresh`,
          {},
          { withCredentials: true },
        )

        const nextAccessToken = response.data.access_token
        setAccessToken(nextAccessToken)
        originalRequest.headers.Authorization = `Bearer ${nextAccessToken}`
        return api(originalRequest)
      } catch (refreshError) {
        clearAccessToken()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  },
)

export const healthCheck = async () => api.get('/health')
export const loginUser = async (payload) => api.post('/auth/login', payload)
export const registerUser = async (payload) => api.post('/auth/register', payload)
export const logoutUser = async () => api.post('/auth/logout')
export const getCurrentUser = async () => api.get('/users/me')
export const updateCurrentUser = async (payload) => api.put('/users/me', payload)
export const changePassword = async (payload) => api.post('/auth/change-password', payload)

export default api
