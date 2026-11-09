import { useEffect, useRef, useState } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import {
  Activity,
  AlertTriangle,
  CircleCheck,
  FastForward,
  HeartPulse,
  Info,
  LoaderCircle,
} from 'lucide-react'
import { predictGlucose } from '../services/api'
import './DigitalTwinSimulation.css'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const MAX_YEARS = 10
const DEBOUNCE_MS = 300

// Mỗi POST /simulation/predict ghi một hàng vào DB, nên giữ cache cấp module
// để kéo slider tới lui hoặc đổi tab không gọi lại payload đã dự đoán.
const predictionCache = new Map()
// Các payload trùng nhau trong cùng một đợt (năm 0 chung, BMI làm tròn trùng năm
// liền kề) cùng bay song song; chia sẻ một Promise để không ghi thừa hàng DB.
const inflightRequests = new Map()

const MAX_ATTEMPTS = 3

function requestPrediction(payload) {
  const key = JSON.stringify(payload)
  if (predictionCache.has(key)) return Promise.resolve(predictionCache.get(key))
  if (inflightRequests.has(key)) return inflightRequests.get(key)
  const promise = (async () => {
    let lastError
    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
      try {
        const res = await predictGlucose(payload)
        const record = res.data?.data
        if (!record || record.predictedScore == null) {
          throw new Error('Phản hồi không chứa điểm dự đoán')
        }
        predictionCache.set(key, record)
        return record
      } catch (err) {
        lastError = err
        // 4xx là payload bị từ chối vĩnh viễn; retry chỉ đốt thời gian của cả đợt.
        if (err.status >= 400 && err.status < 500) break
        if (attempt === MAX_ATTEMPTS) break
        await new Promise((resolve) => setTimeout(resolve, 300 * 2 ** (attempt - 1)))
      }
    }
    throw lastError
  })().finally(() => inflightRequests.delete(key))
  inflightRequests.set(key, promise)
  return promise
}

const DEFAULT_HEALTH_DATA = {
  HighBP: 0,
  HighChol: 0,
  CholCheck: 1,
  BMI: 25,
  Smoker: 0,
  Stroke: 0,
  HeartDiseaseorAttack: 0,
  PhysActivity: 1,
  Fruits: 1,
  Veggies: 1,
  HvyAlcoholConsump: 0,
  AnyHealthcare: 1,
  NoDocbcCost: 0,
  GenHlth: 3,
  MentHlth: 0,
  PhysHlth: 0,
  DiffWalk: 0,
  Sex: 0,
  Age: 6,
  Education: 6,
  Income: 8,
}

// Ngưỡng trùng classify_risk() của ml_service/main_api.py.
const RISK_LEVELS = {
  low: {
    label: 'Low Risk',
    apiLabel: 'Nguy cơ thấp',
    cardClass: 'bg-green-50 border-green-300',
    badgeClass: 'bg-green-600',
    iconClass: 'text-green-600',
    Icon: CircleCheck,
    recommendation:
      'Duy trì vận động tối thiểu 150 phút/tuần, ăn nhiều rau củ và trái cây, không hút thuốc, hạn chế cồn. Tầm soát đường huyết định kỳ 1-3 năm/lần.',
  },
  prediabetes: {
    label: 'Prediabetes',
    apiLabel: 'Nguy cơ trung bình (Tiền tiểu đường)',
    cardClass: 'bg-yellow-50 border-yellow-300',
    badgeClass: 'bg-yellow-500',
    iconClass: 'text-yellow-600',
    Icon: AlertTriangle,
    recommendation:
      'Giai đoạn có thể đảo ngược: giảm 5-7% cân nặng nếu thừa cân, vận động tối thiểu 150 phút/tuần, tiết chế đường và tinh bột tinh chế. Xét nghiệm HbA1c hoặc đường huyết lúc đói mỗi 6-12 tháng và trao đổi với bác sĩ.',
  },
  diabetes: {
    label: 'Diabetes',
    apiLabel: 'Nguy cơ cao (Tiểu đường)',
    cardClass: 'bg-red-50 border-red-300',
    badgeClass: 'bg-red-600',
    iconClass: 'text-red-600',
    Icon: AlertTriangle,
    recommendation:
      'Cần can thiệp y khoa sớm: khám chuyên khoa nội tiết, xét nghiệm HbA1c/đường huyết để xác định chẩn đoán và tuân thủ điều trị. Kiểm soát đồng thời huyết áp, cholesterol; theo dõi đường huyết theo hướng dẫn của bác sĩ.',
  },
}

// Vạch ngưỡng 0.5 / 1.5 ngay trên biểu đồ để đọc vùng nguy cơ không cần tra chú giải.
const riskThresholdPlugin = {
  id: 'riskThresholds',
  afterDraw(chart) {
    const { ctx, chartArea, scales } = chart
    if (!chartArea || !scales.y) return
    const thresholds = [
      { value: 0.5, color: 'rgba(217, 119, 6, 0.7)', label: 'Tiền tiểu đường ≥ 0.5' },
      { value: 1.5, color: 'rgba(220, 38, 38, 0.7)', label: 'Tiểu đường ≥ 1.5' },
    ]
    ctx.save()
    ctx.setLineDash([6, 4])
    ctx.lineWidth = 1
    ctx.font = '11px sans-serif'
    ctx.textAlign = 'right'
    ctx.textBaseline = 'bottom'
    for (const { value, color, label } of thresholds) {
      const py = scales.y.getPixelForValue(value)
      ctx.strokeStyle = color
      ctx.beginPath()
      ctx.moveTo(chartArea.left, py)
      ctx.lineTo(chartArea.right, py)
      ctx.stroke()
      ctx.fillStyle = color
      ctx.fillText(label, chartArea.right - 4, py - 2)
    }
    ctx.restore()
  },
}

function classifyRisk(score) {
  if (score == null) return null
  if (score < 0.5) return RISK_LEVELS.low
  if (score < 1.5) return RISK_LEVELS.prediabetes
  return RISK_LEVELS.diabetes
}

// GenHlth BRFSS: 1 = rất tốt, 5 = kém → cải thiện nghĩa là GIẢM điểm.
// Age BRFSS: mỗi nhóm cách nhau 5 tuổi, nên 5 năm mô phỏng = +1 nhóm.
function buildHealthyScenario(base, year) {
  return {
    ...base,
    PhysActivity: 1,
    Fruits: 1,
    Veggies: 1,
    Smoker: 0,
    HvyAlcoholConsump: 0,
    BMI: Math.max(18.5, base.BMI - 0.3 * year),
    GenHlth: Math.max(1, base.GenHlth - Math.floor(year / 3)),
    MentHlth: Math.max(0, base.MentHlth - year),
    PhysHlth: Math.max(0, base.PhysHlth - year),
    Age: Math.min(13, base.Age + Math.floor(year / 5)),
  }
}

// Đường đỏ giữ nguyên thói quen hiện tại (kể cả thói quen xấu) để việc đổi
// lối sống ở form kéo lại API; các chỉ số sức khỏe vẫn xấu dần theo năm.
function buildCurrentScenario(base, year) {
  return {
    ...base,
    BMI: Math.min(97, base.BMI + 0.5 * year),
    GenHlth: Math.min(5, base.GenHlth + Math.floor(year / 3)),
    MentHlth: Math.min(30, base.MentHlth + year),
    PhysHlth: Math.min(30, base.PhysHlth + year),
    Age: Math.min(13, base.Age + Math.floor(year / 5)),
  }
}

// Phạm vi quan sát trong diabetes_500_balanced.csv (giá trị nguyên, float64).
const CSV_RANGES = {
  HighBP: [0, 1],
  HighChol: [0, 1],
  CholCheck: [0, 1],
  BMI: [15, 77],
  Smoker: [0, 1],
  Stroke: [0, 1],
  HeartDiseaseorAttack: [0, 1],
  PhysActivity: [0, 1],
  Fruits: [0, 1],
  Veggies: [0, 1],
  HvyAlcoholConsump: [0, 1],
  AnyHealthcare: [0, 1],
  NoDocbcCost: [0, 1],
  GenHlth: [1, 5],
  MentHlth: [0, 30],
  PhysHlth: [0, 30],
  DiffWalk: [0, 1],
  Sex: [0, 1],
  Age: [1, 13],
  Education: [1, 6],
  Income: [1, 8],
}

// Đủ 21 khóa, kẹp trong phạm vi CSV và làm tròn về số nguyên như dữ liệu train.
function normalizePayload(raw) {
  const payload = {}
  for (const [key, [lo, hi]] of Object.entries(CSV_RANGES)) {
    const value = Number(raw[key])
    payload[key] = Math.min(hi, Math.max(lo, Math.round(Number.isFinite(value) ? value : lo)))
  }
  return payload
}

// Ước lượng cục bộ tối giản, CHỈ dùng khi cả kịch bản không có điểm SVR nào
// để nội suy; không phải mô hình y khoa và được gắn nhãn "dự phòng" trên UI.
function localEstimate(p) {
  let score = 0.08
  score += 0.3 * p.HighBP + 0.22 * p.HighChol + 0.18 * p.HeartDiseaseorAttack
  score += 0.12 * p.Stroke + 0.1 * p.DiffWalk
  score += Math.max(0, p.BMI - 25) * 0.035
  score += (p.GenHlth - 1) * 0.14
  score += (p.MentHlth + p.PhysHlth) * 0.006
  score += (p.Age - 1) * 0.045
  score += 0.1 * p.Smoker + 0.06 * p.HvyAlcoholConsump
  score -= 0.12 * p.PhysActivity + 0.05 * p.Fruits + 0.05 * p.Veggies
  return Math.round(Math.min(2, Math.max(0, score)) * 100) / 100
}

// Lấp điểm thiếu bằng nội suy giữa hai năm thành công gần nhất (hai đầu thì
// giữ giá trị gần nhất) để đường cong không đứt đoạn khi API lỗi vài điểm.
function fillGaps(records, payloads) {
  const points = records.map((r) =>
    r ? { predictedScore: r.predictedScore, riskLevel: r.riskLevel, fallback: null } : null
  )
  const known = points.reduce((acc, r, i) => (r ? [...acc, i] : acc), [])
  
  // Nếu không có điểm nào thành công, sử dụng localEstimate cho tất cả
  if (known.length === 0) {
    return points.map((_, i) => {
      const score = localEstimate(payloads[i])
      return { predictedScore: score, riskLevel: classifyRisk(score).apiLabel, fallback: 'local' }
    })
  }
  
  return points.map((point, i) => {
    if (point) return point
    let score
    const left = [...known].reverse().find((k) => k < i)
    const right = known.find((k) => k > i)
    if (left !== undefined && right !== undefined) {
      const t = (i - left) / (right - left)
      score = points[left].predictedScore + t * (points[right].predictedScore - points[left].predictedScore)
    } else {
      score = points[left !== undefined ? left : right].predictedScore
    }
    score = Math.round(Math.min(2, Math.max(0, score)) * 100) / 100
    return { predictedScore: score, riskLevel: classifyRisk(score).apiLabel, fallback: 'interp' }
  })
}

function DigitalTwinSimulation({ healthData }) {
  const [years, setYears] = useState(5)
  // Mốc năm đi cùng kết quả trong một state: nếu labels dài hơn data (khi vừa
  // đổi slider) chart sẽ thiếu điểm cuối cho tới lúc đợt gọi API mới xong.
  const [results, setResults] = useState({ years: 0, healthy: [], current: [] })
  const [loading, setLoading] = useState(false)
  const generationRef = useRef(0)

  const baseData = healthData ?? DEFAULT_HEALTH_DATA

  // Gọi lại API khi lối sống (healthData) hoặc mốc thời gian (years) đổi.
  // Debounce để kéo slider không bão hòa backend; generation chống response cũ đè mới.
  useEffect(() => {
    const timer = setTimeout(async () => {
      const generation = ++generationRef.current
      setLoading(true)

      // Năm 0 = hồ sơ hiện tại, chung cho cả hai kịch bản; năm 1..years là thời gian duy trì.
      const milestones = Array.from({ length: years + 1 }, (_, year) => year)
      const healthyPayloads = milestones.map((year) =>
        normalizePayload(buildHealthyScenario(baseData, year))
      )
      const currentPayloads = milestones.map((year) =>
        normalizePayload(buildCurrentScenario(baseData, year))
      )

      const settled = await Promise.allSettled([
        ...healthyPayloads.map(requestPrediction),
        ...currentPayloads.map(requestPrediction),
      ])
      const unwrap = (slice) =>
        slice.map((s) => (s.status === 'fulfilled' ? s.value : null))
      const healthy = fillGaps(unwrap(settled.slice(0, milestones.length)), healthyPayloads)
      const current = fillGaps(unwrap(settled.slice(milestones.length)), currentPayloads)

      if (generation !== generationRef.current) return

      setResults({ years, healthy, current })
      setLoading(false)
    }, DEBOUNCE_MS)

    return () => clearTimeout(timer)
  }, [baseData, years])

  const { years: chartYears, healthy: healthyResults, current: currentResults } = results
  const totalPoints = healthyResults.length + currentResults.length
  const fallbackPoints = [...healthyResults, ...currentResults].filter((r) => r?.fallback).length

  const chartData = {
    labels: Array.from({ length: chartYears + 1 }, (_, i) => `Năm ${i}`),
    datasets: [
      {
        label: 'Lối sống lành mạnh',
        data: healthyResults.map((r) => r.predictedScore),
        borderColor: 'rgb(22, 163, 74)',
        backgroundColor: 'rgba(22, 163, 74, 0.12)',
        pointBackgroundColor: healthyResults.map((r) => (r.fallback ? '#ffffff' : 'rgb(22, 163, 74)')),
        pointBorderColor: 'rgb(22, 163, 74)',
        pointBorderWidth: 2,
        borderWidth: 3,
        pointRadius: 4,
        tension: 0.35,
        fill: true,
        spanGaps: true, // Đảm bảo đường không bị đứt đoạn
      },
      {
        label: 'Lối sống hiện tại / Kịch bản xấu',
        data: currentResults.map((r) => r.predictedScore),
        borderColor: 'rgb(220, 38, 38)',
        backgroundColor: 'rgba(220, 38, 38, 0.12)',
        pointBackgroundColor: currentResults.map((r) => (r.fallback ? '#ffffff' : 'rgb(220, 38, 38)')),
        pointBorderColor: 'rgb(220, 38, 38)',
        pointBorderWidth: 2,
        borderWidth: 3,
        pointRadius: 4,
        tension: 0.35,
        fill: true,
        spanGaps: true, // Đảm bảo đường không bị đứt đoạn
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    // Vẽ đồng bộ: không giật khi kéo slider liên tục và không trắng biểu đồ ở tab ẩn.
    animation: false,
    plugins: {
      legend: { position: 'top' },
      title: {
        display: true,
        text: 'Dự báo nguy cơ tiểu đường theo thời gian (mô hình SVR)',
        font: { size: 16 },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const value = context.parsed.y
            if (value == null) return null
            const series = context.datasetIndex === 0 ? healthyResults : currentResults
            const point = series[context.dataIndex]
            const risk = classifyRisk(value)
            const suffix = point?.fallback ? ' · dự phòng' : ''
            return `${context.dataset.label}: ${value.toFixed(2)} (${risk.label})${suffix}`
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 2,
        title: { display: true, text: 'Điểm nguy cơ (0-2)' },
        ticks: { stepSize: 0.5 },
      },
      x: {
        title: { display: true, text: 'Thời gian duy trì lối sống' },
      },
    },
  }

  const scenarioCards = [
    { title: 'Lối sống lành mạnh', result: healthyResults[chartYears] ?? null },
    {
      title: 'Lối sống hiện tại / Kịch bản xấu',
      result: currentResults[chartYears] ?? null,
    },
  ]

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold text-center mb-8 text-purple-600 flex items-center justify-center gap-3">
        <HeartPulse className="w-8 h-8" />
        Digital Twin Simulation
      </h1>

      {/* Time-warp slider */}
      <div className="mb-8 p-6 bg-purple-50 rounded-lg border-2 border-purple-200">
        <label
          htmlFor="time-warp-slider"
          className="text-lg font-semibold mb-3 text-purple-800 flex items-center gap-2"
        >
          <FastForward className="w-5 h-5" />
          Thời gian duy trì lối sống: {years} năm
        </label>
        <input
          id="time-warp-slider"
          type="range"
          min="1"
          max={MAX_YEARS}
          step="1"
          value={years}
          onChange={(e) => setYears(parseInt(e.target.value, 10))}
          className="w-full h-3 bg-purple-200 rounded-lg appearance-none cursor-pointer"
        />
        <div className="flex justify-between text-sm text-gray-600 mt-2">
          <span>Năm 1</span>
          <span>Năm 5</span>
          <span>Năm 10</span>
        </div>
      </div>

      {/* Cảnh báo cấp độ nguy cơ tại năm đang chọn */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {scenarioCards.map(({ title, result }) => {
          const risk = classifyRisk(result?.predictedScore)
          if (!risk) return null
          const Icon = risk.Icon
          return (
            <div key={title} className={`risk-card p-5 rounded-lg border-2 ${risk.cardClass}`}>
              <div className="flex items-center gap-3 mb-3">
                <Icon className={`w-8 h-8 shrink-0 ${risk.iconClass}`} />
                <div>
                  <h3 className="font-semibold text-gray-800">
                    {title} — Năm {chartYears}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {result.fallback ? 'Điểm dự phòng:' : 'Điểm SVR:'}{' '}
                    <strong>{result.predictedScore.toFixed(2)}</strong> / 2
                  </p>
                </div>
              </div>
              <span
                className={`inline-block px-3 py-1 rounded-full text-white text-sm font-bold ${risk.badgeClass}`}
              >
                {risk.label} · {risk.apiLabel}
              </span>
              <p className="mt-3 text-sm text-gray-700">
                <strong>Khuyến nghị y khoa:</strong> {risk.recommendation}
              </p>
            </div>
          )
        })}
      </div>

      {loading && (
        <div className="mb-6 text-center">
          <LoaderCircle className="inline-block w-8 h-8 animate-spin text-purple-600" />
          <p className="mt-2 text-gray-600">Đang mô phỏng...</p>
        </div>
      )}

      {/* Điểm dự phòng được ghi chú trung tính, không phải banner lỗi: đường cong
          vẫn đủ điểm. Khi mọi điểm là SVR thật thì dòng này không render. */}
      {fallbackPoints > 0 && (
        <p className="mb-6 flex items-center justify-center gap-2 text-sm text-gray-500">
          <Info className="w-4 h-4 shrink-0" />
          {fallbackPoints}/{totalPoints} điểm dùng giá trị dự phòng (nội suy hoặc ước lượng cục
          bộ) vì API chưa phản hồi; các điểm này có viền trắng trên biểu đồ.
        </p>
      )}

      {/* Biểu đồ 2 đường so sánh */}
      <div className="mb-8">
        <div style={{ height: '400px' }}>
          <Line data={chartData} options={chartOptions} plugins={[riskThresholdPlugin]} />
        </div>
      </div>

      {/* Giả định của 2 kịch bản */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="p-4 bg-green-50 rounded-lg border-2 border-green-200">
          <h3 className="font-semibold text-green-800 mb-2 flex items-center gap-2">
            <Activity className="w-5 h-5" /> Kịch bản lối sống lành mạnh (đường xanh)
          </h3>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• Vận động thể chất đều, ăn trái cây và rau củ mỗi ngày</li>
            <li>• Bỏ thuốc lá, không uống cồn nhiều</li>
            <li>• Mỗi năm duy trì: BMI -0.3 (sàn 18.5), ngày suy nhược tinh thần/thể chất -1</li>
            <li>• Sức khỏe tổng quát cải thiện 1 bậc mỗi 3 năm</li>
          </ul>
        </div>
        <div className="p-4 bg-red-50 rounded-lg border-2 border-red-200">
          <h3 className="font-semibold text-red-800 mb-2 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" /> Lối sống hiện tại / kịch bản xấu (đường đỏ)
          </h3>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• Giữ nguyên thói quen hiện tại, không cải thiện vận động, thuốc lá hay cồn</li>
            <li>• Mỗi năm duy trì: BMI +0.5, ngày suy nhược tinh thần/thể chất +1</li>
            <li>• Sức khỏe tổng quát xấu đi 1 bậc mỗi 3 năm</li>
          </ul>
        </div>
      </div>

      {/* Giải thích biểu đồ */}
      <div className="p-4 bg-gray-50 rounded-lg">
        <h3 className="font-semibold mb-2 flex items-center gap-2">
          <Info className="w-5 h-5" /> Giải thích biểu đồ
        </h3>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>
            • <strong>Trục X:</strong> Năm 0 là hồ sơ hiện tại; năm 1-10 là thời gian duy trì lối
            sống. Tuổi tăng 1 nhóm BRFSS (5 tuổi) sau mỗi 5 năm mô phỏng.
          </li>
          <li>
            • <strong>Trục Y:</strong> Điểm nguy cơ tiểu đường (0-2) do SVR dự đoán qua API
            Spring Boot.
          </li>
          <li>
            • <strong>Low Risk:</strong> điểm &lt; 0.5 · <strong>Prediabetes:</strong> 0.5-1.4 ·{' '}
            <strong>Diabetes:</strong> ≥ 1.5
          </li>
          <li>
            • Đường cong là giả lập: mỗi năm duy trì lối sống, các chỉ số thay đổi dần theo
            kịch bản rồi đưa vào mô hình SVR. Kết quả chỉ mang tính tham khảo, không thay thế
            chẩn đoán của bác sĩ.
          </li>
        </ul>
      </div>
    </div>
  )
}

export default DigitalTwinSimulation
