# SPEC_SVR — Đặc tả kỹ thuật hàm dự đoán đường huyết

Module áp dụng: `ml_service/svr_pipeline.py` (class `GlucosePredictor`, hàm
`predict_glucose`), dùng pipeline SVR đã hiệu chuẩn từ `svr_service.py`.

## 1. Chữ ký hàm

```python
class GlucosePredictor:
    @staticmethod
    def predict_glucose(X_input: np.ndarray) -> np.ndarray: ...
```

## 2. Input

- `X_input`: mảng numpy 2D, shape `(n, 5)`, mỗi hàng là một người, các cột theo
  đúng thứ tự:

| Cột | Tên | Kiểu | Đơn vị |
|---|---|---|---|
| 0 | `age` | int | năm tuổi |
| 1 | `bmi` | float | kg/m² |
| 2 | `sleep_hours` | float | giờ ngủ đêm |
| 3 | `alcohol_units` | float | đơn vị cồn/tuần |
| 4 | `years` | int | năm theo dõi |

- Chấp nhận dạng convenience: mảng 1D shape `(5,)` được hiểu là 1 hàng.
- Mảng phải mang giá trị số; hàm tự chuyển về `float` trước khi xử lý.
- Sai shape (không phải `(n, 5)` hoặc `(5,)`) → `ValueError` mô tả shape nhận được.

## 3. Ràng buộc đầu vào (validate trước khi dự đoán)

Nếu **bất kỳ** hàng nào vi phạm một trong các điều kiện sau, hàm phải ném lỗi:

```python
raise ValueError("Tham số đầu vào không hợp lệ")
```

| Điều kiện vi phạm | Cột liên quan |
|---|---|
| `bmi < 10` | cột 1 |
| `sleep_hours < 0` | cột 2 |
| `years < 0` | cột 4 |

- Kiểm tra trên toàn bộ mảng trước khi gọi model (fail-fast, không dự đoán nửa chừng).
- Thông báo lỗi phải đúng nguyên văn: `"Tham số đầu vào không hợp lệ"`.

## 4. Xử lý

1. Chuẩn hóa dữ liệu bằng `sklearn.preprocessing.StandardScaler`.
2. Dự đoán bằng `sklearn.svm.SVR(kernel="rbf")` — tham số đã hiệu chuẩn trong
   `svr_service.py`: `C=1000.0, gamma=0.05, epsilon=0.2`.
3. Scaler và SVR được gói trong một `Pipeline`; scaler **chỉ fit trên dữ liệu
   huấn luyện** (600 mẫu giả lập, seed=42), không bao giờ fit trên `X_input`
   (chống data leakage).
4. Model fit một lần và cache trong module; các lần gọi sau tái sử dụng.
5. Kết quả thô bị kẹp (clip) vào đoạn an toàn `[60.0, 300.0]` mg/dL — sinh lý
   học không có giá trị ngoài khoảng này với đầu vào đã validate.

## 5. Output

- Kiểu: `float`, làm tròn **2 chữ số thập phân** bằng `round(value, 2)`.
- Miền giá trị bảo đảm: `60.0 <= kết quả <= 300.0` (mg/dL).
- Nhiều hàng: trả `np.ndarray` dtype `float64`, shape `(n,)`, mỗi phần tử đã
  làm tròn 2 chữ số và nằm trong miền trên.
- Một hàng (input shape `(5,)` hoặc `(1, 5)`): có thể dùng `float(predict_glucose(row)[0])`
  để lấy scalar.

## 6. Ví dụ

```python
import numpy as np
from ml_service.svr_pipeline import GlucosePredictor

X = np.array([[45, 27.0, 6.5, 8.0, 10],   # hợp lệ
              [30, 22.0, 7.5, 3.0,  5]])  # hợp lệ
GlucosePredictor.predict_glucose(X)       # -> array([140.96, ...]), mg/dL

GlucosePredictor.predict_glucose(np.array([[45, 8.0, 6.5, 8.0, 10]]))
# -> ValueError: Tham số đầu vào không hợp lệ   (bmi < 10)
```

## 7. Bảng tuân thủ

| Yêu cầu | Trạng thái | Vị trí |
|---|---|---|
| Input mảng 2D 5 thuộc tính | ✅ | `predict_glucose` §2 |
| ValueError nguyên văn khi bmi<10 / sleep<0 / years<0 | ✅ | `predict_glucose` §3 |
| StandardScaler + SVR(kernel='rbf') | ✅ | `GlucosePredictor.build_model` |
| Scaler chỉ fit trên train | ✅ | Pipeline, không fit trên X_input |
| Output float, khoảng [60, 300], round 2 | ✅ | clip + round tại return |
