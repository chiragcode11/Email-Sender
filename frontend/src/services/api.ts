import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Auth API
export const authAPI = {
    login: async (username: string, password: string) => {
        const formData = new FormData()
        formData.append('username', username)
        formData.append('password', password)

        const response = await axios.post(`${API_BASE_URL}/auth/login`, formData)
        return response.data
    },

    register: async (email: string, username: string, password: string) => {
        const response = await api.post('/auth/register', { email, username, password })
        return response.data
    },

    getMe: async () => {
        const response = await api.get('/auth/me')
        return response.data
    },
}

// Campaign API
export const campaignAPI = {
    list: async () => {
        const response = await api.get('/campaigns')
        return response.data
    },

    get: async (id: number) => {
        const response = await api.get(`/campaigns/${id}`)
        return response.data
    },

    create: async (data: any) => {
        const response = await api.post('/campaigns', data)
        return response.data
    },

    update: async (id: number, data: any) => {
        const response = await api.patch(`/campaigns/${id}`, data)
        return response.data
    },

    delete: async (id: number) => {
        const response = await api.delete(`/campaigns/${id}`)
        return response.data
    },

    getStats: async (id: number) => {
        const response = await api.get(`/campaigns/${id}/stats`)
        return response.data
    },

    send: async (id: number) => {
        const response = await api.post(`/campaigns/${id}/send`)
        return response.data
    },

    cancel: async (id: number) => {
        const response = await api.post(`/campaigns/${id}/cancel`)
        return response.data
    },

    getRecipients: async (id: number) => {
        const response = await api.get(`/campaigns/${id}/recipients`)
        return response.data
    },

    deleteRecipient: async (campaignId: number, recipientId: number) => {
        const response = await api.delete(`/campaigns/${campaignId}/recipients/${recipientId}`)
        return response.data
    },
}

// Template API
export const templateAPI = {
    list: async () => {
        const response = await api.get('/templates')
        return response.data
    },

    create: async (data: any) => {
        const response = await api.post('/templates', data)
        return response.data
    },
}

// AI API
export const aiAPI = {
    generate: async (data: {
        context: string
        recipient_data: Record<string, any>
        tone?: string
        length?: string
        custom_body?: string
    }) => {
        const response = await api.post('/ai/generate', data)
        return response.data
    },
}

export default api
