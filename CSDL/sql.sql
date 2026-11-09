-- ============================================================================
-- Bio-Digital Twin - Database Schema
-- ============================================================================
-- Tạo bảng health_records lưu trữ 21 chỉ số BRFSS 2015 + kết quả dự đoán ML
-- ============================================================================

-- Bảng health_records: lưu trữ mỗi lần mô phỏng sức khỏe
CREATE TABLE IF NOT EXISTS health_records (
    -- Khóa chính tự tăng
    id BIGSERIAL PRIMARY KEY,

    -- ID người dùng (nếu có hệ thống user)
    user_id BIGINT,

    -- Thời điểm tạo bản ghi
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- ========================================================================
    -- 21 CHỈ SỐ SỨC KHỎE BRFSS 2015 (kiểu DOUBLE để khớp với dữ liệu CSV)
    -- ========================================================================

    -- Tiền sử bệnh lý & kiểm tra sức khỏe
    high_bp DOUBLE PRECISION,                    -- Huyết áp cao (0/1)
    high_chol DOUBLE PRECISION,                  -- Cholesterol cao (0/1)
    chol_check DOUBLE PRECISION,                 -- Đã kiểm tra cholesterol (0/1)

    -- Chỉ số cơ thể
    bmi DOUBLE PRECISION,                        -- BMI (12-97)

    -- Thói quen sinh hoạt
    smoker DOUBLE PRECISION,                     -- Hút thuốc (0/1)
    stroke DOUBLE PRECISION,                     -- Đột quỵ (0/1)
    heart_disease_or_attack DOUBLE PRECISION,    -- Bệnh tim/nhồi máu cơ tim (0/1)
    phys_activity DOUBLE PRECISION,              -- Vận động thể chất (0/1)
    fruits DOUBLE PRECISION,                     -- Ăn trái cây hàng ngày (0/1)
    veggies DOUBLE PRECISION,                    -- Ăn rau củ hàng ngày (0/1)
    hvy_alcohol_consump DOUBLE PRECISION,        -- Uống cồn nhiều (0/1)

    -- Chăm sóc sức khỏe
    any_healthcare DOUBLE PRECISION,             -- Có bảo hiểm y tế (0/1)
    no_doc_bc_cost DOUBLE PRECISION,             -- Không đi khám vì chi phí (0/1)

    -- Sức khỏe tổng quát & tinh thần
    gen_hlth DOUBLE PRECISION,                   -- Sức khỏe tổng quát (1-5)
    ment_hlth DOUBLE PRECISION,                  -- Ngày suy nhược tinh thần (0-30)
    phys_hlth DOUBLE PRECISION,                  -- Ngày suy nhược thể chất (0-30)
    diff_walk DOUBLE PRECISION,                  -- Khó khăn đi bộ/leo cầu thang (0/1)

    -- Nhân khẩu học
    sex DOUBLE PRECISION,                        -- Giới tính (0=Nữ, 1=Nam)
    age DOUBLE PRECISION,                        -- Nhóm tuổi (1-13)
    education DOUBLE PRECISION,                  -- Trình độ học vấn (1-6)
    income DOUBLE PRECISION,                     -- Thu nhập (1-8)

    -- ========================================================================
    -- KẾT QUẢ DỰ ĐOÁN TỪ ML SERVICE
    -- ========================================================================
    predicted_score DOUBLE PRECISION,            -- Điểm dự đoán (0-2)
    risk_level VARCHAR(100),                     -- Mức độ nguy cơ (text)

    -- ========================================================================
    -- INDEXES để tối ưu truy vấn
    -- ========================================================================
    CONSTRAINT chk_predicted_score CHECK (predicted_score >= 0 AND predicted_score <= 2)
);

-- Index cho user_id để truy vấn theo người dùng
CREATE INDEX IF NOT EXISTS idx_health_records_user_id ON health_records(user_id);

-- Index cho created_at để sắp xếp theo thời gian
CREATE INDEX IF NOT EXISTS idx_health_records_created_at ON health_records(created_at DESC);

-- Index cho risk_level để lọc theo mức độ nguy cơ
CREATE INDEX IF NOT EXISTS idx_health_records_risk_level ON health_records(risk_level);

-- Index cho predicted_score để phân tích phân phối
CREATE INDEX IF NOT EXISTS idx_health_records_predicted_score ON health_records(predicted_score);

-- ============================================================================
-- COMMENTS để mô tả các cột (tùy chọn, PostgreSQL hỗ trợ)
-- ============================================================================
COMMENT ON TABLE health_records IS 'Bảng lưu trữ kết quả mô phỏng sức khỏe với 21 chỉ số BRFSS và dự đoán ML';
COMMENT ON COLUMN health_records.id IS 'Khóa chính tự tăng';
COMMENT ON COLUMN health_records.user_id IS 'ID người dùng (nếu có hệ thống user)';
COMMENT ON COLUMN health_records.created_at IS 'Thời điểm tạo bản ghi';
COMMENT ON COLUMN health_records.predicted_score IS 'Điểm nguy cơ tiểu đường (0-2) từ SVR model';
COMMENT ON COLUMN health_records.risk_level IS 'Mức độ nguy cơ: Nguy cơ thấp / Nguy cơ trung bình (Tiền tiểu đường) / Nguy cơ cao (Tiểu đường)';

-- ============================================================================
-- SAMPLE DATA (tùy chọn - có thể xóa nếu không cần)
-- ============================================================================
-- INSERT INTO health_records (
--     user_id, high_bp, high_chol, chol_check, bmi, smoker, stroke,
--     heart_disease_or_attack, phys_activity, fruits, veggies,
--     hvy_alcohol_consump, any_healthcare, no_doc_bc_cost, gen_hlth,
--     ment_hlth, phys_hlth, diff_walk, sex, age, education, income,
--     predicted_score, risk_level
-- ) VALUES (
--     1, 0, 0, 1, 25.0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 2, 0, 0, 0, 0, 6, 6, 8,
--     0.12, 'Nguy cơ thấp'
-- );

-- ============================================================================
-- TRIGGERS (tùy chọn - tự động cập nhật timestamp)
-- ============================================================================
-- Tạo trigger để tự động cập nhật created_at khi insert
-- CREATE OR REPLACE FUNCTION update_created_at_column()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     NEW.created_at = CURRENT_TIMESTAMP;
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE TRIGGER update_health_records_created_at
--     BEFORE INSERT ON health_records
--     FOR EACH ROW
--     EXECUTE FUNCTION update_created_at_column();
