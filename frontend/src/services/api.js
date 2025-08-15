import axios from 'axios'

const RAW_API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'
const API_URL = RAW_API_URL.endsWith('/') ? RAW_API_URL.slice(0, -1) : RAW_API_URL

let isRefreshing = false
let refreshQueue = []

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res,
  async err => {
    const originalRequest = err.config

    if (err.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      if (!isRefreshing) {
        isRefreshing = true
        try {
          const refreshToken = localStorage.getItem('refresh_token')
          if (!refreshToken) throw new Error('No refresh token found')

          const res = await axios.post(`${API_URL}/auth/refresh`, { refresh_token: refreshToken })
          const newToken = res.data.access_token

          localStorage.setItem('token', newToken)
          refreshQueue.forEach(cb => cb(newToken))
          refreshQueue = []

          return api(originalRequest)
        } catch (refreshErr) {
          localStorage.removeItem('token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          return Promise.reject(refreshErr)
        } finally {
          isRefreshing = false
        }
      }

      return new Promise(resolve => {
        refreshQueue.push(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          resolve(api(originalRequest))
        })
      })
    }

    return Promise.reject(err)
  }
)

export const authAPI = {
  login: async (email, password) => {
    const res = await api.post('/auth/login', { email, password })
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    return res.data
  },

  register: async (email, full_name, password) => {
    const res = await api.post('/auth/register', { email, full_name, password })
    return res.data
  },
  getCurrentUser: async () => (await api.get('/auth/me')).data
}

export const searchAPI = {
  search: async (query, maxResults = 10) => (await api.post('/search/', { query, max_results: maxResults })).data,
  getHistory: async (skip = 0, limit = 10) => (await api.get(`/search/history?skip=${skip}&limit=${limit}`)).data
}

export const imageAPI = {
  generate: async (prompt, width = 512, height = 512, steps = 20) => (await api.post('/image/generate', { prompt, width, height, steps })).data,
  getHistory: async (skip = 0, limit = 10) => (await api.get(`/image/history?skip=${skip}&limit=${limit}`)).data
}

export const dashboardAPI = {
  getSearches: async (skip = 0, limit = 20, search = '') => {
    const params = new URLSearchParams({ skip, limit })
    if (search) params.append('search', search)
    return (await api.get(`/dashboard/search?${params}`)).data
  },
  getImages: async (skip = 0, limit = 20, search = '') => {
    const params = new URLSearchParams({ skip, limit })
    if (search) params.append('search', search)
    return (await api.get(`/dashboard/images?${params}`)).data
  },
  deleteSearch: async id => (await api.delete(`/dashboard/search/${id}`)).data,
  deleteImage: async id => (await api.delete(`/dashboard/image/${id}`)).data,
  exportCSV: async (type = 'all') => (await api.get(`/dashboard/export/csv?data_type=${type}`, { responseType: 'blob' })).data,
  exportPDF: async (type = 'all') => (await api.get(`/dashboard/export/pdf?data_type=${type}`, { responseType: 'blob' })).data
}

export default api
