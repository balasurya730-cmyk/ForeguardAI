import api from './api'

export const alertService = {
  list: (status) => api.get('/alerts', { params: status ? { status } : {} }).then((r) => r.data),
  acknowledge: (id) => api.put(`/alerts/${id}/acknowledge`).then((r) => r.data),
  resolve: (id) => api.put(`/alerts/${id}/resolve`).then((r) => r.data),
}
