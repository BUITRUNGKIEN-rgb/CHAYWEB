# SMART CAMPUS AI — AI02: Web demo chạy trên GitHub Pages

Trang web tĩnh, không dùng Streamlit server, không dùng API trả phí. Dự đoán AI thật bằng **chính bộ mô hình scikit-learn `.joblib`** và **bộ trích đặc trưng `src/features.py`** của đội, được chạy trong trình duyệt qua Pyodide/WebAssembly.

> **QUAN TRỌNG:** Bản bàn giao chưa kèm mô hình huấn luyện bằng TrashNet. Không được giới thiệu website đã nhận diện thật cho tới khi xuất hai tệp `models/baseline.joblib` và `models/improved.joblib`. Website thông báo thiếu trọng số và không tự bịa ra dự đoán.

## 1. Thư mục web

```
index.html
.nojekyll
python_features.py       # Sao chép chính xác từ src/features.py khi xuất mô hình
python_bridge.py         # Chạy predict/predict_proba trong trình duyệt
worker.js                # Pyodide Worker giúp không đứng giao diện
assets/
  app.js
  styles.css
  favicon.svg
models/
  manifest.json
  baseline.joblib         # CHƯA CÓ, được tạo sau huấn luyện
  improved.joblib         # CHƯA CÓ, được tạo sau huấn luyện
export_models_for_web.py
```

## 2. Huấn luyện bằng TrashNet thật (trên PC, một lần)

Nếu đang dùng bộ mã **`UNETI12_ODD3_AI02_V3_RA_SOAT_KY.zip`**, mở PowerShell tại thư mục dự án, cài thư viện rồi chạy:

```powershell
py -m pip install -r requirements_core.txt
py -m src.train --images data/dataset-resized
```

Đảm bảo `data/dataset-resized/` gồm đúng 6 thư mục con. Chương trình phải tạo `model/baseline.joblib`, `model/improved.joblib` và `results/metrics.json`. Không dùng `--fast` cho kết quả chính thức.

## 3. Xuất mô hình sang web

Đặt thư mục **website này** cạnh thư mục mã AI02 hoặc ở vị trí bất kỳ. Mở PowerShell bên trong thư mục web:

```powershell
py export_models_for_web.py --project "C:\\duong-dan\\UNETI12_ODD3_AI02"
```

Script kiểm tra thông tin metrics, số ảnh và chế độ thực nghiệm; từ chối kết quả thử trên ảnh giả lập. Sau khi chạy, `models/` có đủ hai `.joblib` và `manifest.json` chuyển thành `trained:true`. Nếu kiểm tra chỉ thấy dưới 2.000 ảnh thì dừng để xem nguyên nhân; chỉ dùng `--allow-small` khi **có dữ liệu thật** nhưng số lượng bị giảm hợp lệ.

**Không đưa bộ ảnh gốc TrashNet lên GitHub**, chỉ đưa các tệp website và trọng số mô hình nếu bạn được phép công bố trọng số.

## 4. Thử website trên máy trước khi đăng GitHub

Do trình duyệt chặn một số tính năng với `file://`, hãy chạy HTTP nội bộ:

```powershell
py -m http.server 8000
```

Mở `http://localhost:8000/`, chọn một ảnh và thử SVM cải tiến/Baseline. **Lần tải đầu** cần Internet để lấy Pyodide, NumPy, scikit-learn, scikit-image, Pillow và joblib từ jsDelivr. Các lần sau trình duyệt có thể dùng cache; không cam kết 100% ngoại tuyến.

## 5. Đưa lên GitHub Pages (không cần terminal Git)

1. Vào https://github.com/new, tạo repository công khai, chẳng hạn `smart-campus-ai02`.
2. Trong repository, nhấn **Add file → Upload files**.
3. **Tải lên nội dung bên trong thư mục website** (đảm bảo `index.html` nằm ở thư mục gốc repository; thư mục `assets/` và `models/` cùng cấp). Nếu GitHub không cho tải cả thư mục bằng chọn file, có thể kéo thả thư mục hoặc dùng Git Desktop.
4. Nhấn **Commit changes**.
5. Chọn **Settings → Pages → Build and deployment → Deploy from a branch**, Branch `main`, Folder `/ (root)` rồi **Save**.
6. Trang web có dạng: `https://TEN_GITHUB.github.io/smart-campus-ai02/`.

Tên repository khác thì thay tương ứng trong URL. Nếu repository chưa có mô hình `.joblib`, website vẫn mở được giao diện nhưng sẽ **không dự đoán AI**; có thể nạp `.joblib` tin cậy tạm từ máy trên giao diện khi demo.

## 6. Nếu web báo lỗi

- `Thiếu improved.joblib`: Huấn luyện và chạy `export_models_for_web.py`, sau đó tải lại các tệp mới vào repo.
- `Failed to fetch`, `importScripts`: Trình duyệt không tải được Pyodide từ CDN; kiểm tra Internet, VPN/extension hoặc mạng.
- `UnpicklingError`, `InconsistentVersionWarning`: Có thể khác phiên bản Python/scikit-learn khi load `joblib`; kiểm tra môi trường huấn luyện, ưu tiên `scikit-learn` cùng phiên bản Pyodide được ghim.
- Website đứng khi mở lần đầu: Pyodide khoa học tải dung lượng đáng kể. Dùng máy có RAM phù hợp và chuẩn bị demo Tkinter ngoại tuyến.
- Ảnh vật thể phức tạp/nhiều vật thể có thể cho dự đoán sai; TrashNet chủ yếu có nền đơn giản.
- Joblib **có thể thực thi mã khi mở**; chỉ dùng trọng số của đội hoặc nguồn đáng tin cậy.

## 7. Liên hệ với quy định đề chung kết

- Tải ảnh → 6 loại rác → xác suất tham khảo → gợi ý phân loại: **có** (khi đã có mô hình).
- Baseline và mô hình cải tiến: **có** (nếu xuất đủ hai trọng số).
- Dữ liệu thống kê, so sánh và biểu đồ: lấy từ mã huấn luyện V3, không tự chế trên website.
- Chuẩn bị phiên bản **demo ngoại tuyến** cho phần thi 05 phút, vì GitHub Pages + CDN phụ thuộc kết nối lần đầu.
- Đề không bắt buộc website, nên hãy ưu tiên thực nghiệm, slide và phương án dự phòng.
