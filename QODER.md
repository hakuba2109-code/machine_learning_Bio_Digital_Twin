# QODER.md — Bio-Digital Twin

Chỉ dẫn dự án, được Agent nạp mỗi đầu phiên. Đọc mục "Trạng thái repo" trước
khi giả định bất kỳ thư mục nào tồn tại.

## Trạng thái repo (đã kiểm ngày 2026-11-06, cập nhật cùng phiên)

Thư mục gốc: `D:\DOAN\Do_An_Bio_Digital_Twin` — **không phải repo git**. Toàn bộ file đang tồn tại:

```
frontend_react/  (Vite + React scaffold 2026-11-06, xem Tech Stack + mục Frontend)
run_project.bat  (trình khởi động 3 cửa sổ terminal, thêm 2026-11-09)
svr_service.py  test_svr_demo.py  requirements.txt  SPEC_SVR.md
ml_service/predictor.py  ml_service/svr_pipeline.py  ml_service/data_generator.py
ml_service/trainer.py  ml_service/main_api.py
ml_service/saved_models/best_svr.joblib
ml_service/saved_models/scaler.joblib
ml_service/data/metabolic_data.csv
diabetes_012_health_indicators_BRFSS2015.csv/  (thư mục, tên dễ nhầm với file)
  diabetes_012_health_indicators_BRFSS2015.csv  (22.7 MB, toàn bộ BRFSS 2015)
  diabetes_500_balanced.csv  (nguồn train hiện tại của trainer.py)
  diabetes_500_samples.csv
tests/test_svr_pipeline.py  tests/test_api.py
backend_springboot/src/main/resources/application.yml
backend_springboot/src/main/java/com/biodigitaltwin/dto/ApiResponse.java
backend_springboot/src/main/java/com/biodigitaltwin/dto/HealthSimulationRequestDto.java
backend_springboot/src/main/java/com/biodigitaltwin/dto/MlPredictionResponseDto.java
backend_springboot/src/main/java/com/biodigitaltwin/config/RestClientConfig.java
backend_springboot/src/main/java/com/biodigitaltwin/service/MlClientService.java
backend_springboot/src/main/java/com/biodigitaltwin/service/HealthSimulationService.java
backend_springboot/src/main/java/com/biodigitaltwin/controller/HealthSimulationController.java
backend_springboot/src/main/java/com/biodigitaltwin/entity/HealthRecord.java
backend_springboot/src/main/java/com/biodigitaltwin/repository/HealthRecordRepository.java
backend_springboot/.env.example  (backend_springboot/.env — có secret, đã ignore)
.qoder/skills/python-ml-skill/SKILL.md
.qoderignore  .gitignore  .ignore  .venv/
```

`backend_springboot/` đã có đầy đủ một luồng dọc: `application.yml`,
`dto/ApiResponse.java`, `dto/HealthSimulationRequestDto.java` (21 trường BRFSS
+ `userId`, ràng buộc trùng Pydantic), `dto/MlPredictionResponseDto.java`,
`config/RestClientConfig.java` (bean `RestTemplate`),
`service/MlClientService.java`, `service/HealthSimulationService.java`,
`controller/HealthSimulationController.java`,
`entity/HealthRecord.java` (bảng `health_records`, đủ 21 chỉ số BRFSS kiểu
`Double` + `predictedScore`/`riskLevel`) và
`repository/HealthRecordRepository.java`. **Vẫn chưa có `pom.xml` và chưa có
lớp `@SpringBootApplication`** nên chưa build hay chạy được — toàn bộ code Java
ở đây mới là nguồn chưa được build thật. `javac` trên PATH trỏ về **JDK
`1.8.0_504`** (`C:\java-8`), không compile nổi `record` và `jakarta.persistence`;
máy này **có** JDK 25 tại `C:\Program Files\Eclipse Adoptium\jdk-25.0.4.101-hotspot`
(chính là `JAVA_HOME`) — phải gọi bằng đường dẫn tuyệt đối. Đã dùng JDK 25 chạy
`javac -Xmaxerrs 2000` trên cả 9 file: **175 lỗi, 100% là `package ... does not
exist` / `cannot find symbol` các type framework** (Spring, Jakarta, Jackson,
slf4j) vì thiếu jar — không có lỗi cú pháp hay lỗi tham chiếu chéo giữa các lớp
của dự án. React **đã** scaffold ngày 2026-11-06 tại `frontend_react/` (Vite
react template, JavaScript — làm theo yêu cầu gốc, chưa áp rule TypeScript ở
dưới). `pom.xml` vẫn chưa tồn tại — nếu cần khung dự án mới, hỏi người dùng
chứ đừng tạo tùy tiện.

Cổng phục vụ (tránh nhầm như yêu cầu gốc từng ghi `ml.service.url:
http://localhost:3000`): backend Spring = **3000**, FastAPI ML service =
**8000** (`uvicorn ml_service.main_api:app --port 8000`). Secret DB chỉ nằm
trong `backend_springboot/.env` (đã thêm `.env` vào cả ba file ignore);
`application.yml` chỉ tham chiếu `${POSTGRES_PASSWORD}`. Spring Boot không tự
đọc `.env` — cần `spring-boot-dotenv`/`me.paulschwarz:spring-dotenv` khi
scaffold `pom.xml`, hoặc export biến môi trường khi chạy.

Cầu nối Spring → FastAPI (đã kiểm ngày 2026-11-06):
`POST /api/v1/simulation/predict` (`HealthSimulationController`,
`@CrossOrigin(origins = "*")`) → `HealthSimulationService.simulate()` →
`MlClientService.predict()` gọi `POST {ml.service.url}/api/v1/predict-glucose`
→ trả `MlPredictionResponseDto` → lưu `HealthRecord` qua
`HealthRecordRepository`. Service **gọi ML trước rồi mới persist** để
`predicted_score`/`risk_level` không bao giờ null trong lịch sử.
`MlClientService` tự dựng body `LinkedHashMap` theo đúng tên cột BRFSS in hoa
(`HighBP`, `BMI`, ...) thay vì serialize DTO, vì Pydantic so khớp tên field
có phân biệt hoa thường mà bean Java sẽ sinh ra `highBP`. Đã đối chiếu bằng
script: 21 key Java gửi = 21 field `SimulationRequest`, thứ tự trùng
`FEATURE_COLUMNS`, 21 setter trong `HealthRecord` được gán đủ (+ `userId`),
2 key `MlPredictionResponseDto` = 2 field `SimulationResponse`; gọi HTTP thật
vào `localhost:8000` → `200 {"predicted_score": 2.0, "risk_level": "Nguy cơ
cao (Tiểu đường)"}`. `MlClientService` đọc `${ml.service.url}` (8000), tuyệt
đối không hard-code 3000 như yêu cầu gốc — xem đoạn cổng phục vụ ở trên.
Controller trả thẳng entity theo đúng đề bài, đây
là chỗ lệch rule "Controller không trả thẳng entity" ở mục Quy tắc Java (đã
ghi chú ngay trong Javadoc của controller).

## Tech Stack

| Lớp | Công nghệ | Phiên bản | Trạng thái |
|---|---|---|---|
| ML | Python | 3.13.0 | đang dùng |
| ML | numpy | 2.5.4 | đang dùng |
| ML | scikit-learn | 1.9.1 | đang dùng |
| ML | matplotlib | 3.11.2 | đang dùng |
| ML | pandas | 3.1.1 | đang dùng |
| API | FastAPI + Uvicorn | 0.162.0 / 0.54.0 | đang dùng (`ml_service/main_api.py`) |
| Backend | Java + Spring Boot | chưa có `pom.xml` | config + DTO + entity + repository + cầu nối ML (RestTemplate) |
| Frontend | React + Vite | React 19.3.1, Vite 8.3.6 | đang dùng (`frontend_react/`, JS template) |
| Frontend | TailwindCSS | 3.4.19 (PostCSS + Autoprefixer) | đang dùng — `tailwind.config.js` + `@tailwind` trong `src/index.css` |
| Frontend | axios / chart.js / react-chartjs-2 / lucide-react | 1.21.0 / 4.6.1 / 5.3.1 / 1.70.0 | đang dùng |

Môi trường ảo: `.venv` ở thư mục gốc, Python 3.13.0. **Luôn chạy code bằng
`.venv`**, không dùng Python hệ thống — máy dev còn bản scikit-learn trong
user-site (`AppData\Roaming\Python\Python313`) sẽ che mất lỗi của `.venv`.

```cmd
.venv\Scripts\python.exe svr_service.py
.venv\Scripts\python.exe ml_service\data_generator.py
.venv\Scripts\python.exe ml_service\trainer.py
.venv\Scripts\python.exe -m uvicorn ml_service.main_api:app
.venv\Scripts\python.exe -m pytest tests
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Quy tắc Python

Bốn quy chuẩn bắt buộc, chi tiết và ví dụ mẫu ở `.qoder/skills/python-ml-skill/SKILL.md`
(skill `python-ml-skill` tự kích hoạt khi sửa code Python):

1. Type hints cho mọi tham số và giá trị trả về.
2. Docstring cho mọi hàm; ghi rõ đơn vị (năm, kg/m², mg/dL).
3. `StandardScaler` trước khi SVR dự đoán — dùng `make_pipeline` để scaler chỉ
   fit trên tập train, tránh data leakage.
4. `round(value, 2)` tại biên trả về với mọi `float`; không làm tròn trung gian.

Hai dòng mô hình đang cùng tồn tại — **đừng trộn lẫn feature của chúng**:

**A. Mô hình 5 đặc trưng (in-memory, không artifact)** — `svr_service.py` sinh
600 mẫu giả lập seed 42, `SVR(kernel="rbf", C=1000.0, gamma=0.05, epsilon=0.2)`
(đừng đổi nếu chưa đo lại). Kiểm chứng trên 200 điểm giữ lại: MAE 0.69 mg/dL,
max 2.77 mg/dL, R² 0.9997. `gamma="scale"` cho lỗi tới 14.7 mg/dL ở góc không
gian 5 chiều. Người dùng: `SPEC_SVR.md`, `ml_service/svr_pipeline.py`,
`ml_service/predictor.py`, `tests/test_svr_pipeline.py`.
Ca mẫu: `GlucosePredictor(age=45, bmi=27.0, sleep_hours=6.5, alcohol_units=8.0, years=10).predict()`
→ `140.96` mg/dL.

**B. Mô hình 21 đặc trưng BRFSS (artifact)** — `ml_service/trainer.py` đọc
`diabetes_012_health_indicators_BRFSS2015.csv/diabetes_500_balanced.csv`
(500 hàng × 22 cột, target `Diabetes_012` 0/1/2 phân bố 250/50/200), split
80/20 seed 42, grid-search C×gamma kernel rbf → `C=1, gamma=0.01`, test
**R² 0.24, MAE 0.64 score units**. Artifact
`ml_service/saved_models/{best_svr,scaler}.joblib`. Người dùng duy nhất:
`ml_service/main_api.py`. R² thấp là bình thường vì SVR hồi quy trên nhãn
thứ tự 0/1/2 chứ không phân lớp.

`ml_service/data_generator.py` + `ml_service/data/metabolic_data.csv` (10 đặc
trưng, glucose mg/dL) **không còn nuôi artifact nữa** — vẫn chạy được và vẫn
là dữ liệu demo, nhưng API hiện tại không đọc nó.

API FastAPI (`ml_service/main_api.py`, POST `/api/v1/predict-glucose`, điểm
`Diabetes_012`: <0.5 `Nguy cơ thấp`, 0.5–1.4 `Nguy cơ trung bình (Tiền tiểu
đường)`, ≥1.5 `Nguy cơ cao (Tiểu đường)`). Luồng đúng sơ đồ:
`SimulationRequest` (21 trường) → mảng numpy `(1, 21)` theo thứ tự
`FEATURE_COLUMNS` → `scaler.transform` → `best_svr.predict` → clip [0, 2]
(SVR không bị chặn; payload mạnh cho điểm thô 2.30/2.63) → round 2 → phân
loại. `trainer.py` fit scaler trên mảng định vị (không phải DataFrame có tên
cột) nên API truyền numpy thô mà không bị cảnh báo feature-names. Ca mẫu
`_payload()` trong `tests/test_api.py` → `2.0` `Nguy cơ cao`; ca thấp →
`0.12`; ca trung bình → `1.27`. Test API đã tune theo giá trị artifact thật,
không hard-code số của mô hình A.

Ngoại lệ đã biết: `test_svr_demo.py` là demo tham số gốc, **không** theo quy tắc
3 (dùng SVR thô, không scaler). Kết quả của nó là `9.64`; nếu thêm scaler sẽ
ra `9.97`. Đừng "sửa cho đồng bộ" khi chưa được yêu cầu.

## Quy tắc Java (áp dụng khi backend tồn tại)

- Constructor injection, không dùng `@Autowired` trên field.
- Phân lớp cứng: Controller → Service → Repository. Controller không chứa logic
  nghiệp vụ và không trả thẳng entity.
- DTO/record ở biên API, có `jakarta.validation`; không đưa ID nội bộ ra URL công khai.
- Migration schema bằng Flyway, đánh số tăng dần; không sửa migration đã áp dụng.
- Build bằng wrapper, không dùng `mvn` hệ thống:

```cmd
mvnw.cmd spring-boot:run
mvnw.cmd test
```

- Muốn kiểm tra nhanh code Java khi chưa có `pom.xml` (chưa có jar vẫn dùng
  được), compile bằng JDK 25 đường dẫn tuyệt đối rồi lọc lỗi — chỉ số lỗi
  `package ... does not exist` / `cannot find symbol` là hợp lệ, còn lỗi khác
  là code mình sai:

```cmd
dir /s /b src\main\java\*.java > %TEMP%\sources.txt
"C:\Program Files\Eclipse Adoptium\jdk-25.0.4.101-hotspot\bin\javac" -Xmaxerrs 2000 -encoding UTF-8 -proc:none -d %TEMP%\javacheck @%TEMP%\sources.txt
```

- **Không chạy `mvnw.cmd clean` khi app đang chạy** — làm hỏng tiến trình đang
  phục vụ. Dừng app trước rồi mới clean.

## Quy tắc React (áp dụng khi frontend tồn tại)

- TypeScript `strict`, không `any` mới; component hàm + hooks, không class component.
- Một component một file, đặt cạnh file test của nó.
- Gọi API qua proxy Vite trong dev, không hard-code CORS hay URL production.
- Không nhét API key vào client; secrets đi qua backend.

Đã cài đặt ngày 2026-11-06 trong `frontend_react/`: `vite.config.js` cấu hình
proxy dev `'/api' → http://localhost:3000` (đúng rule không hard-code URL);
`src/services/api.js` đặt axios `baseURL: '/api/v1'` (override được bằng
`VITE_API_BASE_URL`), timeout 15 s, interceptor trả `Error` kèm message, helper
`predictGlucose(healthData)` gọi `POST /simulation/predict` khớp
`HealthSimulationController`. Kiểm chứng: `npm run build` pass (3.44 s); dev
server 5173 trả `200` trang gốc và `502` cho `POST /api/v1/simulation/predict`
vì backend Spring chưa chạy (đúng hành vi proxy mong đợi). Lưu ý lệch rule:
code frontend hiện là JavaScript (`.js`/`.jsx`) theo yêu cầu gốc, chưa phải
TypeScript strict.

Cập nhật 2026-11-07: `frontend_react/src/components/` đã có `HealthForm.jsx`
(+ css), `BioDigitalTwinDashboard.jsx` (2 tab form / mô phỏng) và
`DigitalTwinSimulation.jsx` (+ css). Component mô phỏng vẽ `Line`
(react-chartjs-2) hai đường: xanh = kịch bản cải thiện (ép vận động, bỏ
thuốc lá/cồn, BMI -0.3/năm), đỏ = giữ thói quen hiện tại và xấu dần
(BMI +0.5/năm, GenHlth +1 bậc/3 năm — nhớ GenHlth 1 = tốt, 5 = kém); slider
"Thời gian duy trì lối sống" 1-10 năm, debounce 300 ms, cache cấp module theo
JSON payload (mỗi POST ghi một hàng DB nên không gọi lại), generation chống
response cũ đè mới; card Low Risk / Prediabetes / Diabetes theo ngưỡng 0.5/1.5
kèm khuyến nghị; `animation: false` để vẽ đồng bộ cả ở tab ẩn. Đã kiểm thử
browser thật ngày 2026-11-07 bằng cầu nối mock cổng 3000 chuyển tiếp sang FastAPI 8000
(Spring chưa build được): đủ 3 mức nguy cơ, đổi lối sống gọi lại API, kéo
slider tới lui không gọi thừa. Thư mục `CSDL/` ở gốc chỉ có `sql.sql`.

Cập nhật 2026-11-09 — chống đứt đoạn biểu đồ và cầu nối dev:

- `vite.config.js` có plugin `mlDevBridge` (`apply: 'serve'`, chỉ dev): middleware
  chặn `POST /api/v1/simulation/predict`, chuyển sang
  `${ML_SERVICE_URL:http://localhost:8000}/api/v1/predict-glucose` rồi bọc lại
  envelope `ApiResponse` (`status`/`message`/`data`/`timestamp`, đổi
  `predicted_score` → `predictedScore`, `risk_level` → `riskLevel`). Không ghi
  Postgres — phần đó vẫn thuộc Spring Boot thật. ML chết thì trả 502. Plugin
  chạy trước middleware proxy nên `/api` → 3000 vẫn giữ cho endpoint khác.
- `DigitalTwinSimulation.jsx`: payload vẫn qua `normalizePayload` — đủ 21 khóa,
  kẹp trong dải quan sát của `diabetes_500_balanced.csv` (đã đối chiếu lại bằng
  pandas: BMI 15-77, GenHlth 1-5, MentHlth/PhysHlth 0-30, Age 1-13, Education
  1-6, Income 1-8, còn lại 0/1) và làm tròn về số nguyên như dữ liệu train.
- `Promise.allSettled` cho cả 2 kịch bản + `fillGaps` lấp điểm thiếu (nội suy
  giữa 2 năm thành công, hai đầu giữ giá trị gần nhất, không có điểm nào thành
  công thì dùng `localEstimate`). **Không còn banner lỗi màu đỏ**; thay bằng
  một dòng ghi chú xám `x/y điểm dùng giá trị dự phòng…` chỉ hiện khi có
  fallback, điểm fallback có viền trắng. Mọi điểm thành công thì dòng này
  không render.
- Kết quả và mốc năm nằm chung một state `{ years, healthy, current }`: trước
  đây `labels` dài `years+1` nhưng data còn theo mốc cũ nên chart thiếu điểm
  cuối ngay khi kéo slider. Card và nhãn trục giờ đọc `chartYears`.
- `requestPrediction` retry tối đa 3 lần, backoff 300/600 ms, **không retry
  4xx** và không ngủ sau lần cuối; `api.js` gắn `status` vào Error để phân biệt
  4xx với 5xx/network.
- Số điểm: mỗi đường có `years+1` điểm (năm 0 là hồ sơ hiện tại). Mặc định
  `years=5` → **12 điểm** tổng 2 đường; kéo max `years=10` → **22 điểm**.
- Kiểm thử browser thật 2026-11-09 (BMI 40, GenHlth 5, HighBP/HighChol bật):
  12/12 và 22/22 điểm SVR thật, 0 null, `labels.length == data.length` mọi mốc,
  console sạch, 22 request FastAPI đều 200. Tắt ML: 12/12 điểm vẫn vẽ bằng
  `localEstimate`, không banner đỏ. Tắt ML rồi kéo 9→10 năm: đúng ca "2 điểm
  thiếu" → 22/22 điểm vẫn vẽ (2 điểm nội suy), ghi chú `2/22`. Bật lại ML:
  ghi chú tự biến mất, 20/20 điểm SVR thật. `npm run lint` 0 warning/0 error,
  `npm run build` pass (3.15 s, 476.55 kB js / 16.83 kB css).
- **Chạy dev phải đúng thư mục** (chạy ở gốc sẽ báo `No plugin found for prefix
  'spring-boot'` và `ENOENT package.json`):

```cmd
cd /d D:\DOAN\Do_An_Bio_Digital_Twin
.venv\Scripts\python.exe -m uvicorn ml_service.main_api:app --port 8000
```

```cmd
cd /d D:\DOAN\Do_An_Bio_Digital_Twin\frontend_react
npm run dev
```

`run_project.bat` (thêm 2026-11-09 ở thư mục gốc) gom hai lệnh trên thành một
cú nhấp đúp, mở **3 cửa sổ terminal** riêng: FastAPI 8000, Spring Boot 3000,
React 5173. Cơ chế: file tự gọi lại chính nó qua `start "tiêu đề" cmd /k
""%~f0" <ml|backend|frontend>"` nên mỗi nhánh có `cd /d` và kiểm tra riêng,
không phải lồng `cd` trong ngoặc kép.

- Nhánh `ml`: kiểm tra `.venv\Scripts\python.exe` rồi chạy
  `-m uvicorn ml_service.main_api:app --port 8000`.
- Nhánh `frontend`: `npm install` nếu thiếu `node_modules`, rồi `npm run dev`
  với `CI=true`. **Bắt buộc có `CI=true`**: Vite gắn
  `process.stdin.on("end", parentSigtermCallback)` và tự SIGTERM khi stdin
  đóng (xem `node_modules/vite/dist/node/chunks/node.js` dòng 3103, điều kiện
  `process.env.CI !== "true"`). Cửa sổ mở từ script có stdin là pipe/`<nul`
  làm Vite in "ready" rồi thoát ngay; `< CON` không cứu được, `CI=true` thì
  có. Đánh đổi duy nhất: mất phím tắt `h + enter` trong cửa sổ Vite.
- Nhánh `backend`: **dừng ngay và giải thích** khi thiếu `pom.xml` (liệt kê
  pom.xml + `@SpringBootApplication` + `mvnw.cmd` còn thiếu, nhắc cầu nối dev).
  Khi đã có `pom.xml`: nạp `backend_springboot/.env` vào môi trường cửa sổ bằng
  `for /f ... set "%%A=%%~B"` (Spring Boot không tự đọc `.env`; giá trị chỉ
  được set, không in ra), rồi `mvnw.cmd spring-boot:run`, fallback `mvn`.
- **File .bat phải là CRLF.** Bản ghi bằng LF làm cmd.exe parse sai hoàn toàn
  (hàng loạt `'n_ml' is not recognized...`); đã `unix2dos`. `chcp 65001` ở đầu
  file để tiếng Việt có dấu hiển thị đúng. Sau mỗi lần sửa lại file phải
  `unix2dos run_project.bat` vì công cụ ghi file dùng LF.
- Kiểm thử thật 2026-11-09 (khởi động tách rời bằng
  `powershell Start-Process run_project.bat`, tương đương nhấp đúp):
  `openapi.json` ở 8000 trả 200, trang 5173 trả 200,
  `POST 5173/api/v1/simulation/predict` trả `{"predictedScore":0.95,...}`
  qua cầu nối. Cổng 3000 không mở (đúng dự kiến). Nhánh `backend` chạy riêng
  in đúng thông báo thiếu `pom.xml`, exit code 1. Tắt FastAPI thì cầu nối trả
  502 kèm message, không sập Vite.
- Khi thử nghiệm từ shell của Agent: dừng tiến trình nền bằng TaskStop có thể
  để lại process con giữ cổng (node vẫn giữ 5173 sau khi npm wrapper bị dừng)
  làm Vite nhảy sang 5174 — dò `netstat -ano | findstr :5173` và kill đúng PID
  trước khi chạy lại.

## Quy tắc an toàn Workspace

- Không chạy lệnh xóa đệ quy (`rm -rf`, `del /s /q`) trên `.venv`, `.qoder`,
  hay thư mục gốc. Xóa file rác theo tên từng file.
- Không `pip install` vào Python hệ thống; mọi dependency mới phải vào `.venv`
  và được ghi lại trong `requirements.txt`.
- Không sửa tay bên trong `.venv/` hay `node_modules/`.
- Secret (API key, mật khẩu DB) chỉ nằm trong `.env`; không xuất hiện nguyên văn
  trong lệnh shell, log, hay file commit.
- Lệnh ảnh hưởng ngoài máy cục bộ (git push, force push, `--no-verify`, xóa
  branch, publish) phải xin xác nhận trước.
- Ba file ignore `.qoderignore` / `.gitignore` / `.ignore` giữ nội dung giống
  nhau: `.venv/`, `__pycache__/`, `target/`, `node_modules/`, `*.log`. Lý do:
  folder chưa phải repo git nên `.gitignore` chưa có tác dụng với ripgrep;
  `.ignore` mới chặn được Agent quét `.venv` vào Context Window. Sau khi
  `git init` có thể bỏ `.ignore`.

## Kiểm tra trước khi bàn giao

```cmd
.venv\Scripts\python.exe svr_service.py
.venv\Scripts\python.exe -m pip freeze | findstr /i "numpy scikit-learn matplotlib pandas fastapi uvicorn httpx pytest"
```

Mọi con số ghi trong file này phải khớp lệnh chạy thật; nếu sửa code làm đổi
kết quả, cập nhật luôn số trong QODER.md và skill.
