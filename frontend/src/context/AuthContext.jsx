import { createContext, useCallback, useEffect, useMemo, useState } from 'react'
import api, {
  clearAccessToken,
  getAccessToken,
  getCurrentUser,
  logoutUser,
  refreshSession,
  setAccessToken,
} from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    const bootstrap = async () => {
      try {
        if (!getAccessToken()) {
          const refreshResponse = await refreshSession()
          const nextToken = refreshResponse.data?.access_token
          if (!nextToken) {
            throw new Error('No access token from refresh')
          }
          setAccessToken(nextToken)
        }

        const response = await getCurrentUser()
        if (!cancelled) {
          setUser(response.data.user)
        }
      } catch {
        clearAccessToken()
        if (!cancelled) {
          setUser(null)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    bootstrap()
    return () => {
      cancelled = true
    }
  }, [])

  const login = useCallback(async (userData, nextAccessToken) => {
    setAccessToken(nextAccessToken)
    setUser(userData)
  }, [])

  const logout = useCallback(async () => {
    try {
      if (getAccessToken()) {
        await logoutUser()
      }
    } catch {
      // Ignore logout API failures and clear local state anyway.
    } finally {
      clearAccessToken()
      delete api.defaults.headers.common.Authorization
      setUser(null)
    }
  }, [])

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      logout,
      setUser,
    }),
    [user, loading, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export default AuthContext
