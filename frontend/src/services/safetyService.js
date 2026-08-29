import api from './api'

export const safetyService = {
  listEvents: (limit = 100) => api.get('/safety/events', { params: { limit } }).then((r) => r.data),
  getEvent: (id) => api.get(`/safety/events/${id}`).then((r) => r.data),

  listWorkers: () => api.get('/workers').then((r) => r.data),
  getWorker: (id) => api.get(`/workers/${id}`).then((r) => r.data),
  getWorkerEvents: (id) => api.get(`/workers/${id}/events`).then((r) => r.data),

  listCameras: () => api.get('/cameras').then((r) => r.data),

  listEvidence: (limit = 100) => api.get('/evidence', { params: { limit } }).then((r) => r.data),
  markReviewed: (id) => api.put(`/evidence/${id}/reviewed`).then((r) => r.data),
}
