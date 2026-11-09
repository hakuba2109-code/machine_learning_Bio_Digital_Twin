import { useState } from 'react'
import HealthForm from './HealthForm'
import DigitalTwinSimulation from './DigitalTwinSimulation'

function BioDigitalTwinDashboard() {
  const [activeTab, setActiveTab] = useState('form')
  const [healthData, setHealthData] = useState(null)

  const handleFormSubmit = (data) => {
    setHealthData(data)
    setActiveTab('simulation')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold text-center text-purple-600">
            🧬 Bio-Digital Twin
          </h1>
          <p className="text-center text-gray-600 mt-2">
            Mô phỏng bản sao sinh học và dự báo nguy cơ tiểu đường
          </p>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('form')}
              className={`py-4 px-6 font-semibold border-b-2 transition-colors ${
                activeTab === 'form'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              📝 Nhập thông tin sức khỏe
            </button>
            <button
              onClick={() => setActiveTab('simulation')}
              className={`py-4 px-6 font-semibold border-b-2 transition-colors ${
                activeTab === 'simulation'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
              disabled={!healthData}
            >
              📊 Mô phỏng Digital Twin
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'form' && (
          <HealthForm onSubmit={handleFormSubmit} />
        )}
        {activeTab === 'simulation' && healthData && (
          <DigitalTwinSimulation healthData={healthData} />
        )}
        {activeTab === 'simulation' && !healthData && (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">
              Vui lòng nhập thông tin sức khỏe ở tab trước để bắt đầu mô phỏng
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-gray-500 text-sm">
          <p>Bio-Digital Twin - Dự án nghiên cứu sức khỏe số</p>
        </div>
      </footer>
    </div>
  )
}

export default BioDigitalTwinDashboard
