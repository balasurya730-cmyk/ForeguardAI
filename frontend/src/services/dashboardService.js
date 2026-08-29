import api from './api'

export const dashboardService = {
  summary: () => api.get('/dashboard/summary').then((r) => r.data),
}

export const reportService = {
  daily: () => api.get('/reports/daily').then((r) => r.data),
  weekly: () => api.get('/reports/weekly').then((r) => r.data),
  monthly: () => api.get('/reports/monthly').then((r) => r.data),
}
