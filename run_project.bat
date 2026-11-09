@echo off
chcp 65001 >nul
setlocal
set "ROOT=%~dp0"

rem Cửa sổ con gọi lại chính file này với một tham số để mỗi service có
rem working directory, kiểm tra tiên quyết và biến môi trường riêng.
if /i "%~1"=="ml"       goto run_ml
if /i "%~1"=="backend"  goto run_backend
if /i "%~1"=="frontend" goto run_frontend

echo ============================================================
echo  Bio-Digital Twin - khởi động 3 cửa sổ terminal
echo ============================================================
echo  FastAPI (ML)     : http://localhost:8000
echo  Spring Boot      : http://localhost:3000
echo  React (Vite)     : http://localhost:5173
echo.
echo  Dự đoán ở dev đi qua cầu nối Vite -^> FastAPI 8000.
echo  Spring Boot hiện CHƯA build được (thiếu pom.xml và lớp
echo  @SpringBootApplication) nên cửa sổ của nó sẽ báo lỗi rõ ràng.
echo ============================================================
echo.

start "Bio-Digital Twin - FastAPI 8000" cmd /k ""%~f0" ml"
start "Bio-Digital Twin - Spring Boot 3000" cmd /k ""%~f0" backend"
start "Bio-Digital Twin - React 5173" cmd /k ""%~f0" frontend"
exit /b 0


:run_ml
title Bio-Digital Twin - FastAPI 8000
cd /d "%ROOT%"
if not exist ".venv\Scripts\python.exe" (
    echo [LỖI] Không tìm thấy .venv\Scripts\python.exe trong %ROOT%
    echo       Tạo môi trường ảo rồi cài requirements.txt trước.
    pause
    exit /b 1
)
echo [FastAPI] http://localhost:8000 - POST /api/v1/predict-glucose
echo [FastAPI] Nạp best_svr.joblib + scaler.joblib, có thể mất vài giây...
echo.
".venv\Scripts\python.exe" -m uvicorn ml_service.main_api:app --port 8000
echo.
echo [FastAPI] Đã dừng.
pause
exit /b 0


:run_backend
title Bio-Digital Twin - Spring Boot 3000
cd /d "%ROOT%backend_springboot"
if not exist "pom.xml" (
    echo [LỖI] Chưa có pom.xml trong %ROOT%backend_springboot
    echo.
    echo       Thư mục này mới có src/ ^(DTO, entity, repository, service,
    echo       controller^) và application.yml. Còn thiếu:
    echo         1. pom.xml ^(spring-boot-starter-web, data-jpa, validation,
    echo            postgresql, spring-dotenv^)
    echo         2. Lớp @SpringBootApplication
    echo         3. Maven Wrapper mvnw.cmd
    echo.
    echo       Trong lúc đó, React vẫn dự đoán được qua cầu nối dev
    echo       Vite -^> FastAPI 8000 ^(xem vite.config.js^), chỉ là không
    echo       lưu lịch sử vào Postgres.
    echo.
    pause
    exit /b 1
)
rem Spring Boot không tự đọc .env nên nạp vào môi trường cửa sổ này.
rem Giá trị chỉ được set, không in ra màn hình.
if exist ".env" (
    echo [Spring] Nạp biến môi trường từ .env
    for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do (
        if not "%%A"=="" set "%%A=%%~B"
    )
)
echo [Spring] http://localhost:3000 - POST /api/v1/simulation/predict
echo.
if exist "mvnw.cmd" (
    call mvnw.cmd spring-boot:run
) else (
    call mvn spring-boot:run
)
echo.
echo [Spring] Đã dừng.
pause
exit /b 0


:run_frontend
title Bio-Digital Twin - React 5173
cd /d "%ROOT%frontend_react"
if not exist "package.json" (
    echo [LỖI] Không tìm thấy package.json trong %ROOT%frontend_react
    pause
    exit /b 1
)
if not exist "node_modules" (
    echo [React] Chưa có node_modules, đang chạy npm install...
    call npm install
    if errorlevel 1 (
        echo [LỖI] npm install thất bại.
        pause
        exit /b 1
    )
)
echo [React] http://localhost:5173
echo.
rem Vite coi sự kiện 'end' trên stdin là dấu hiệu tiến trình cha đã chết và tự
rem SIGTERM. Cửa sổ mở từ script có stdin đóng (pipe, <nul) sẽ làm Vite thoát
rem ngay sau khi ready. CI=true tắt đúng nhánh đó (vite/dist/node/chunks/node.js).
set "CI=true"
call npm run dev
set "CI="
echo.
echo [React] Đã dừng.
pause
exit /b 0