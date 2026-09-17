import axios from 'axios'

let accessToken = null
let isRefreshing = false
let refreshFailed = false
let refreshSubscribers = []

const AUTH_PUBLIC_PATHS = ['/login', '/register', '/verify-email', '/']

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
  refreshFailed = false
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
  }
}

export const clearAccessToken = () => {
  accessToken = null
  delete api.defaults.headers.common.Authorization
}

export const getAccessToken = () => accessToken

const redirectToLogin = () => {
  const path = window.location.pathname
  if (AUTH_PUBLIC_PATHS.some((publicPath) => path === publicPath || path.startsWith(`${publicPath}?`))) {
    return
  }
  if (path.startsWith('/login') || path.startsWith('/register') || path.startsWith('/verify-email')) {
    return
  }
  window.location.href = '/login'
}

const resolveApiBaseUrl = () => {
  const configured = (import.meta.env.VITE_API_BASE_URL || '').trim()

  // Production must never call localhost — even if a Vercel env var was mis-set.
  if (import.meta.env.PROD && configured && /localhost|127\.0\.0\.1/i.test(configured)) {
    console.error(
      '[PostGen AI] Ignoring VITE_API_BASE_URL pointing at localhost in production. Using same-origin /api.',
    )
    return '/api'
  }

  if (configured) {
    return configured.replace(/\/$/, '')
  }

  // Same-origin `/api` works for:
  // - local Vite (proxied to Flask in vite.config.js)
  // - Vercel (rewritten to the Flask backend service)
  return '/api'
}

export const API_BASE_URL = resolveApiBaseUrl()

const api = axios.create({
  baseURL: API_BASE_URL,
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
    const requestUrl = originalRequest.url || ''

    if (error.response?.status === 429) {
      return Promise.reject(error)
    }

    if (requestUrl.includes('/auth/refresh') || requestUrl.includes('/auth/login') || requestUrl.includes('/auth/register')) {
      return Promise.reject(error)
    }

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error)
    }

    if (refreshFailed) {
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        refreshSubscribers.push((tokenOrError) => {
          if (tokenOrError instanceof Error || (tokenOrError && tokenOrError.isAxiosError) || (tokenOrError && tokenOrError.response)) {
            reject(tokenOrError)
          } else if (!tokenOrError) {
            reject(error)
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
     const response = await api.post(
  '/auth/refresh',
  {},
  { withCredentials: true },
)

      const nextAccessToken = response.data?.access_token
      if (!nextAccessToken) {
        throw new Error('Refresh response missing access token')
      }

      setAccessToken(nextAccessToken)
      onRefreshSuccess(nextAccessToken)
      originalRequest.headers = originalRequest.headers || {}
      originalRequest.headers.Authorization = `Bearer ${nextAccessToken}`
      return api(originalRequest)
    } catch (refreshError) {
      refreshFailed = true
      onRefreshError(refreshError)
      clearAccessToken()
      redirectToLogin()
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  },
)

export const healthCheck = async () => api.get('/health')
export const loginUser = async (payload) => api.post('/auth/login', payload)
export const registerUser = async (payload) => api.post('/auth/register', payload)
export const getGoogleLoginUrl = async () => api.get('/auth/google/login-url')
export const verifyEmail = async (token) => api.get(`/auth/verify-email?token=${encodeURIComponent(token)}`)
export const resendVerification = async (email) => api.post('/auth/resend-verification', { email })
export const logoutUser = async () => api.post('/auth/logout')
export const refreshSession = async () => api.post('/auth/refresh', {})
export const getCurrentUser = async () => api.get('/users/me')
export const updateCurrentUser = async (payload) => api.put('/users/me', payload)
export const changePassword = async (payload) => api.post('/auth/change-password', payload)

export default api
