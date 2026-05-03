import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
})

// Request interceptor for adding auth token (when Keycloak is implemented)
api.interceptors.request.use(
  (config) => {
    // TODO: Add Keycloak token to headers
    // const token = getKeycloakToken()
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      // Import dynamically to avoid circular dependency
      import('../stores/auth').then(({ useAuthStore }) => {
        const authStore = useAuthStore()
        authStore.logout()
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      })
    }
    return Promise.reject(error)
  }
)

export default api
