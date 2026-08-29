import api from './api'

export const gasService = {
  listZones: () => api.get('/gas/zones').then((r) => r.data),
  getZone: (id) => api.get(`/gas/zones/${id}`).then((r) => r.data),
  createZone: (payload) => api.post('/gas/zones', payload).then((r) => r.data),
  updateZone: (id, payload) => api.put(`/gas/zones/${id}`, payload).then((r) => r.data),
}
