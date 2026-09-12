import { createContext, useEffect, useMemo, useState } from 'react'
import api, { getCurrentUser, setAccessToken, clearAccessToken } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const bootstrap = async () => {
      try {
        const response = await getCurrentUser()
        setUser(response.data.user)
      } catch (error) {
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    bootstrap()
  }, [])

  const login = async (userData, accessToken) => {
    setAccessToken(accessToken)
    api.defaults.headers.common.Authorization = `Bearer ${accessToken}`
    setUser(userData)
  }

  const logout = () => {
    clearAccessToken()
    delete api.defaults.headers.common.Authorization
    setUser(null)
  }

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      logout,
      setUser,
    }),
    [user, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export default AuthContext
