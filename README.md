# GoCoffee
I. Tổng quan:
- Vấn đề: Người dùng mất nhiều thời gian để tìm quán cà phê phù hợp (theo sở thích, vị trí, giá cả). Các trang review hiện tại thường bị loãng, không cá nhân hóa theo "gu" từng người.
- Giải pháp: Xây dựng Website review cà phê tích hợp AI gợi ý cá nhân hóa. Hệ thống tự động học thói quen người dùng để đề xuất quán phù hợp nhất.

II. Công nghệ sử dụng
1. Back-End: 
- Ngôn ngữ: Python 3.10+ 
- Framework: Django (Mô hình MVT). 
- Database: SQLite / PostgreSQL.
2. Front-End: 
- Giao diện: HTML5, CSS3, Bootstrap 5. 
- Hiệu ứng: SwiperJS (Slider), FontAwesome 6. 
- Xử lý bất đồng bộ: AJAX (Fetch API).
3. API & Công cụ phát triển: 
- OpenStreetMap (OSM): Cung cấp dữ liệu bản đồ nền miễn phí. 
- Nominatim API (Geopy): Sử dụng để chuyển đổi địa chỉ sang tọa độ (Geocoding) trong Python. 
- Leaflet.js: Thư viện JavaScript để hiển thị bản đồ tương tác trên giao diện. 
- Version Control: Git & GitHub. 
- IDE: PyCharm.
4. Thư viện xử lý dữ liệu & AI: 
- Pandas: Xử lý ma trận dữ liệu User-Item. 
- Scikit-learn (sklearn): Các thuật toán học máy và tính toán vector. 
- Underthesea: Xử lý ngôn ngữ tự nhiên tiếng Việt (Tách từ, gán nhãn từ loại). 
- Joblib: Lưu trữ và load mô hình đã huấn luyện.

III. Database
- CafeShop: Lưu trữ toàn bộ thông tin định danh và dữ liệu hiển thị của quán cà phê. Tích hợp sẵn các trường Cache chỉ số AI (avg_service, avg_drink...) giúp tối ưu tốc độ truy vấn và hiển thị bản đồ. 
- MenuItem: Quản lý danh sách món ăn, giá cả và phân loại thực đơn của từng quán. 
- ShopImage: Lưu trữ thư viện ảnh không gian, hỗ trợ trải nghiệm người dùng. 
- Review: Lưu đánh giá người dùng kèm kết quả phân tích cảm xúc chi tiết từng khía cạnh (Service, Drink, Price, Ambiance). 
- ShopViewLog: Ghi nhận lịch sử và tần suất xem quán (view_count). Dữ liệu đầu vào cốt lõi cho Thuật toán Gợi ý (Recommendation System). 
- SavedShop: Quản lý danh sách yêu thích (Wishlist) cá nhân hóa của người dùng. 
- Contact: Bảng độc lập. Cho phép cả khách vãng lai (Guest) gửi góp ý mà không cần đăng nhập. 
- User: Hệ thống xác thực và quản lý tài khoản người dùng (Django Auth).

IV. AI
1. ASPECT-BASED SENTIMENT ANALYSIS
Phần 1: Huấn luyện (Training - file train_ai.py):
"Trong lớp train_ai.py, em sử dụng bộ ba thư viện Scikit-learn, Underthesea và Joblib.
Quy trình huấn luyện gồm 3 bước:
Tiền xử lý: Em dùng word_tokenize của Underthesea để tách từ, giúp AI hiểu được các từ ghép tiếng Việt (như 'nhân_viên').
Pipeline huấn luyện: Em xây dựng một luồng xử lý khép kín (make_pipeline) gồm:
TF-IDF kết hợp N-gram (1-3): Để vector hóa văn bản và giúp AI nắm bắt được ngữ cảnh của cả cụm từ dài.
Thuật toán SVC: Để phân loại dữ liệu.
Đóng gói: Cuối cùng, em dùng joblib để xuất model ra file .pkl. Việc này giúp hệ thống có thể tái sử dụng ngay lập tức mà không cần tốn tài nguyên train lại từ đầu."

Phần 2: Suy luận thực tế (Inference - file sentiment.py):
"Lớp SentimentEngine chịu trách nhiệm xử lý review thực tế trên web. Điểm nhấn ở đây là em áp dụng mô hình Hybrid (kết hợp AI và Luật):
Tối ưu hiệu năng: Em dùng Singleton Pattern để đảm bảo model nặng chỉ được load vào RAM một lần duy nhất khi server khởi động.
Xử lý ngôn ngữ: Em dùng Regex và POS-TAGGING của underthesea để tách các câu ghép phức tạp thành các vế đơn, tránh làm nhiễu AI.
Cơ chế tính điểm: Sau khi AI dự đoán song song Khía cạnh và Cảm xúc, em tính Điểm trọng số bằng công thức:
Score = (Nhãn dự đoán) x (Độ tin cậy của AI) x (Hệ số Boost words).
Ví dụ: Nếu AI chắc chắn 90% và người dùng dùng từ 'cực kỳ', điểm sẽ được nhân lên.
Kết quả: Cuối cùng em quy đổi về ngưỡng -1, 0, 1 để lưu vào Database."


2. RECOMMENDATION SYSTEM
Lớp 1: Lọc cộng tác (Collaborative Filtering - User-based):
- B1: Xử lý dữ liệu: Để giải quyết vấn đề dữ liệu thưa (Data Sparsity), em không chỉ dùng Review mà kết hợp cả View Log.
Em xây dựng Ma trận tương tác: Hàng là User, Cột là Quán.
Giá trị là Rating, nếu chưa rate thì em quy đổi số lượt xem (View * 0.5).
- B2: Tìm người dùng tương đồng: Em dùng độ đo Cosine Similarity để tính toán và tìm ra người dùng (Neighbors) có hành vi, sở thích giống user hiện tại nhất. (bỏ qua những user có độ tương đồng < 30%)
- B3: Dự đoán điểm số: Em tính điểm cho các quán dựa trên đánh giá của những người hàng xóm này theo công thức Trung bình cộng CÓ TRỌNG SỐ (Weighted Average). Nghĩa là người nào càng giống user hiện tại thì đánh giá của họ càng có sức nặng.
- B4: Gợi ý: Cuối cùng, hệ thống lọc bỏ những quán user đã từng tương tác, sắp xếp và trả về Top 8 quán có điểm dự đoán cao nhất."

Lớp 2: Lọc theo nội dung (Content-based Filtering):
- Được kích hoạt khi Lớp 1 chưa đủ dữ liệu (Cold-start). 
- Hệ thống phân tích lịch sử xem của user để trích xuất các Tags xuất hiện nhiều nhất. 
- So Tags của User với Tags của các quán trong Database để đưa ra gợi ý.
- Còn nếu mới tạo tài khoản chưa có dữ liệu thì sẽ đề xuất random các quán có rating >= 4.0.