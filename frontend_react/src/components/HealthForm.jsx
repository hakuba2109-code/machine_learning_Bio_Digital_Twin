import { useState } from 'react'
import './HealthForm.css'

function HealthForm({ onSubmit }) {
  // State cho 21 chỉ số sức khỏe BRFSS
  const [formData, setFormData] = useState({
    // Nhóm Sinh học cố định
    BMI: 25,
    Age: 6,
    Sex: 0,
    Education: 6,
    Income: 8,

    // Nhóm Tiền sử bệnh lý
    HighBP: 0,
    HighChol: 0,
    HeartDiseaseorAttack: 0,
    Stroke: 0,
    DiffWalk: 0,

    // Nhóm Thói quen sinh hoạt
    Smoker: 0,
    HvyAlcoholConsump: 0,
    PhysActivity: 1,
    Fruits: 1,
    Veggies: 1,
    GenHlth: 3,
    MentHlth: 0,
    PhysHlth: 0,
  })

  // Các trường bổ sung không hiển thị nhưng cần gửi (giá trị mặc định)
  const hiddenFields = {
    CholCheck: 1,
    AnyHealthcare: 1,
    NoDocbcCost: 0,
  }

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Xử lý thay đổi cho checkbox (binary 0/1)
  const handleCheckboxChange = (e) => {
    const { name, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: checked ? 1 : 0,
    }))
  }

  // Xử lý thay đổi cho slider (range)
  const handleRangeChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: parseFloat(value),
    }))
  }

  // Submit form
  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      // Kết hợp dữ liệu form + các trường ẩn
      const payload = {
        ...formData,
        ...hiddenFields,
      }

      // Gọi onSubmit để chuyển dữ liệu lên parent component
      if (onSubmit) {
        onSubmit(payload)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold text-center mb-8 text-blue-600">
        Mô Phỏng Bản Sao Sinh Học
      </h1>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Nhóm 1: Sinh học cố định */}
        <section className="border-2 border-blue-200 rounded-lg p-6 bg-blue-50">
          <h2 className="text-xl font-semibold mb-4 text-blue-800 flex items-center">
            <span className="mr-2">👤</span> Nhóm Sinh học cố định
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* BMI */}
            <div>
              <label className="block text-sm font-medium mb-2">
                BMI (Chỉ số khối cơ thể): {formData.BMI}
              </label>
              <input
                type="range"
                name="BMI"
                min="12"
                max="97"
                step="1"
                value={formData.BMI}
                onChange={handleRangeChange}
                className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>12</span>
                <span>97</span>
              </div>
            </div>

            {/* Age */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Tuổi (Nhóm tuổi): {formData.Age}
              </label>
              <input
                type="range"
                name="Age"
                min="1"
                max="13"
                step="1"
                value={formData.Age}
                onChange={handleRangeChange}
                className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>18-24</span>
                <span>80+</span>
              </div>
            </div>

            {/* Sex */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Giới tính: {formData.Sex === 0 ? 'Nữ' : 'Nam'}
              </label>
              <div className="flex gap-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="Sex"
                    checked={formData.Sex === 1}
                    onChange={handleCheckboxChange}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                  <span className="ml-2">Nam</span>
                </label>
              </div>
            </div>

            {/* Education */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Trình độ học vấn: {formData.Education}
              </label>
              <input
                type="range"
                name="Education"
                min="1"
                max="6"
                step="1"
                value={formData.Education}
                onChange={handleRangeChange}
                className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Thấp</span>
                <span>Cao</span>
              </div>
            </div>

            {/* Income */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Thu nhập: {formData.Income}
              </label>
              <input
                type="range"
                name="Income"
                min="1"
                max="8"
                step="1"
                value={formData.Income}
                onChange={handleRangeChange}
                className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Thấp</span>
                <span>Cao</span>
              </div>
            </div>
          </div>
        </section>

        {/* Nhóm 2: Tiền sử bệnh lý */}
        <section className="border-2 border-red-200 rounded-lg p-6 bg-red-50">
          <h2 className="text-xl font-semibold mb-4 text-red-800 flex items-center">
            <span className="mr-2">🏥</span> Nhóm Tiền sử bệnh lý
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { name: 'HighBP', label: 'Huyết áp cao' },
              { name: 'HighChol', label: 'Cholesterol cao' },
              { name: 'HeartDiseaseorAttack', label: 'Bệnh tim hoặc nhồi máu cơ tim' },
              { name: 'Stroke', label: 'Đột quỵ' },
              { name: 'DiffWalk', label: 'Khó khăn khi đi bộ leo cầu thang' },
            ].map((field) => (
              <label key={field.name} className="flex items-center p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
                <input
                  type="checkbox"
                  name={field.name}
                  checked={formData[field.name] === 1}
                  onChange={handleCheckboxChange}
                  className="w-5 h-5 text-red-600 rounded"
                />
                <span className="ml-3 font-medium">{field.label}</span>
              </label>
            ))}
          </div>
        </section>

        {/* Nhóm 3: Thói quen sinh hoạt */}
        <section className="border-2 border-green-200 rounded-lg p-6 bg-green-50">
          <h2 className="text-xl font-semibold mb-4 text-green-800 flex items-center">
            <span className="mr-2">🌱</span> Nhóm Thói quen sinh hoạt
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Checkboxes */}
            <div className="space-y-3">
              {[
                { name: 'Smoker', label: 'Hút thuốc (ít nhất 100 điếu trong đời)' },
                { name: 'HvyAlcoholConsump', label: 'Uống cồn nhiều (nam >14, nữ >7 ly/tuần)' },
                { name: 'PhysActivity', label: 'Vận động thể chất (30+ ngày/tháng)' },
                { name: 'Fruits', label: 'Ăn trái cây hàng ngày' },
                { name: 'Veggies', label: 'Ăn rau củ hàng ngày' },
              ].map((field) => (
                <label key={field.name} className="flex items-center p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
                  <input
                    type="checkbox"
                    name={field.name}
                    checked={formData[field.name] === 1}
                    onChange={handleCheckboxChange}
                    className="w-5 h-5 text-green-600 rounded"
                  />
                  <span className="ml-3 font-medium">{field.label}</span>
                </label>
              ))}
            </div>

            {/* Sliders cho GenHlth, MentHlth và PhysHlth */}
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Sức khỏe tổng quát: {formData.GenHlth}
                </label>
                <input
                  type="range"
                  name="GenHlth"
                  min="1"
                  max="5"
                  step="1"
                  value={formData.GenHlth}
                  onChange={handleRangeChange}
                  className="w-full h-2 bg-green-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Tốt</span>
                  <span>Kém</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Ngày suy nhược tinh thần (tháng vừa qua): {formData.MentHlth}
                </label>
                <input
                  type="range"
                  name="MentHlth"
                  min="0"
                  max="30"
                  step="1"
                  value={formData.MentHlth}
                  onChange={handleRangeChange}
                  className="w-full h-2 bg-green-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0 ngày</span>
                  <span>30 ngày</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Ngày suy nhược thể chất (tháng vừa qua): {formData.PhysHlth}
                </label>
                <input
                  type="range"
                  name="PhysHlth"
                  min="0"
                  max="30"
                  step="1"
                  value={formData.PhysHlth}
                  onChange={handleRangeChange}
                  className="w-full h-2 bg-green-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0 ngày</span>
                  <span>30 ngày</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Nút submit */}
        <div className="flex justify-center">
          <button
            type="submit"
            disabled={loading}
            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold text-lg rounded-lg shadow-lg hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {loading ? 'Đang xử lý...' : '🧬 Tiếp tục đến Mô Phỏng Digital Twin'}
          </button>
        </div>
      </form>

      {/* Hiển thị lỗi */}
      {error && (
        <div className="mt-8 p-6 bg-red-100 border-2 border-red-300 rounded-lg">
          <h3 className="text-xl font-bold text-red-800 mb-2">Lỗi</h3>
          <p className="text-red-700">{error}</p>
        </div>
      )}
    </div>
  )
}

export default HealthForm
