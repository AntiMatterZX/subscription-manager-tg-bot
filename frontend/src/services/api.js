import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

// Products
export const getProducts = () => api.get('/products')
export const getProduct = (id) => api.get(`/products/${id}`)
export const createProduct = (data) => api.post('/products', data)
export const updateProduct = (id, data) => api.put(`/products/${id}`, data)
export const deleteProduct = (id) => api.delete(`/products/${id}`)

// Groups
export const getGroups = () => api.get('/groups')
export const getUnmappedGroups = () => api.get('/groups/unmapped')
export const mapProductToGroup = (productId, data) => api.post(`/products/${productId}/map`, data)
export const unmapProduct = (productId) => api.delete(`/products/${productId}/unmap`)

// Subscriptions
export const getSubscriptions = () => api.get('/subscriptions')
export const createSubscription = (data) => api.post('/subscribe', data)

export default api