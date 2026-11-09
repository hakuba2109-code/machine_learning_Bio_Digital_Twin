import axios from 'axios'

// Spring Boot backend chạy tại http://localhost:3000/api/v1.
// Ở chế độ dev, baseURL '/api/v1' đi qua proxy Vite (vite.config.js) → localhost:3000,
// nên không cần cấu hình CORS trên client.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.message || error.message || 'Lỗi kết nối backend'
    const wrapped = new Error(message)
    // Giữ status để nơi gọi phân biệt 4xx (payload sai vĩnh viễn, retry vô ích)
    // với 5xx/network (lỗi tạm thời, nên thử lại).
    wrapped.status = error.response?.status ?? null
    return Promise.reject(wrapped)
  },
)

// Luaồng chính: POST 21 chỉ số BRFSS -> HealthSimulationController trả về
// predictedScore + riskLevel (đã kiểm chứng trong QODER.md).
export function predictGlucose(healthData) {
  return api.post('/simulation/predict', healthData)
}

export default api
