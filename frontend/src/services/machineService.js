import api from './api'

export const machineService = {
  list: () => api.get('/machines').then((r) => r.data),
  get: (id) => api.get(`/machines/${id}`).then((r) => r.data),
  create: (payload) => api.post('/machines', payload).then((r) => r.data),
  update: (id, payload) => api.put(`/machines/${id}`, payload).then((r) => r.data),
  remove: (id) => api.delete(`/machines/${id}`),
  readings: (id, limit = 100) =>
    api.get(`/machines/${id}/readings`, { params: { limit } }).then((r) => r.data),

  startRuntime: (id, durationSeconds) =>
    api.post(`/machines/${id}/runtime/start`, { duration_seconds: durationSeconds }).then((r) => r.data),
  stopRuntime: (id) => api.post(`/machines/${id}/runtime/stop`).then((r) => r.data),
  getRuntime: (id) => api.get(`/machines/${id}/runtime`).then((r) => r.data),
}
