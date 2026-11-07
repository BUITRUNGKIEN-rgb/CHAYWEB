# AIX – UNETI12 | AI02 Web chạy trên GitHub Pages (không Streamlit)

Đây là web **HTML/CSS/JavaScript**, dùng Pyodide để chạy **Baseline/SVM scikit-learn** trong trình duyệt. **Không dùng app.py, không dùng Streamlit**.

## Đưa giao diện lên GitHub
1. Tạo repository mới (ví dụ `AIX_AI02_WEB`) để không ghi đè repository `AIX_Web_App` hiện tại.
2. Mở repo → Add file → Upload files → kéo **toàn bộ nội dung** của thư mục này (không kéo ZIP) → Commit.
3. Settings → Pages → Deploy from a branch → main → /(root) → Save.
4. Mở `https://BUITRUNGKIEN-rgb.github.io/AIX_AI02_WEB/` (nếu dùng tên repo ví dụ).

## Có dự đoán AI thật cần làm gì?
ZIP KHÔNG kèm checkpoint. Trang không dự đoán bừa. Có hai cách dùng mô hình của chính đội:

**Cách A – Chỉ demo trên máy người dùng, không công khai mô hình:**
- Trong trang chọn SVM hoặc Baseline → chọn nút **Nạp mô hình từ máy** → chọn `improved.joblib` / `baseline.joblib` do đội tự train từ dự án tương ứng.
- Mã trích xuất đặc trưng phải phù hợp checkpoint. Cần kiểm tra phiên bản scikit-learn so với Pyodide.

**Cách B – Tự động có mô hình cho người xem công khai:**
- Để file `models/baseline.joblib` và `models/improved.joblib` do đội đã train thật vào thư mục `models/`, và đổi `models/manifest.json` thành `trained:true` với hai trạng thái tương ứng.
- Hoặc chạy `01_GAN_MODEL_VAO_WEB.bat` để xuất từ dự án có `results/metrics.json` đúng định dạng, `model/` và `src/features.py`.
- Khi đưa các checkpoint lên repository public, chúng trở thành **công khai**. Không nên làm nếu muốn giữ riêng.

**Giới hạn quan trọng:** Web này chạy **SVM/Baseline**, KHÔNG nạp checkpoint CNN `.pth` của AI02 V12 trực tiếp. Muốn chạy CNN trên GitHub Pages cần xuất mô hình sang ONNX/TensorFlow.js và viết bộ suy luận trình duyệt tương thích. Không sử dụng Python backend.

**Mạng:** Lần đầu chạy cần truy cập CDN Pyodide để tải Python và thư viện AI. Trình duyệt có thể chặn CDN; nếu gặp lỗi `importScripts`, kiểm tra mạng/trình chặn.

## Cách chạy thử trên Windows
Nhấp đúp `02_CHAY_THU_WEB_LOCAL.bat`, rồi mở `http://localhost:8000`. Python chỉ đóng vai trò HTTP file server **trên máy bạn**, không chạy dự đoán phía server. Khi đã đưa lên GitHub Pages thì không cần chạy bất kỳ máy nào.

## An toàn
Không đẩy thư mục `data/`, dữ liệu TrashNet, `.venv/`, file bí mật. File `.joblib` chỉ được mở nếu do chính đội train hoặc đáng tin cậy; pickle/joblib có thể thực thi mã. Không khẳng định độ chính xác của mô hình khi chưa đánh giá.
