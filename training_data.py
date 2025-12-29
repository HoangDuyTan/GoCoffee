TRAIN_DATA = [
    # =================================================================
    # 1. DRINK
    # =================================================================
    # --- Khen (Positive) ---
    ("Nước ngon thật", "drink", 1),
    ("cà phê ở đây rất thơm và đậm đà", "drink", 1),
    ("trà sữa trân châu ngon tuyệt vời", "drink", 1),
    ("menu đa dạng nhiều món ngon", "drink", 1),
    ("đồ uống trang trí đẹp mắt, vị ổn", "drink", 1),
    ("bạc xỉu béo ngậy, rất vừa miệng", "drink", 1),
    ("cốt dừa đá xay siêu đỉnh", "drink", 1),
    ("trà đào cam sả uống mát lạnh, sảng khoái", "drink", 1),
    ("topping nhiều ú nu, ăn ngập mồm", "drink", 1),
    ("nước ép tươi, không bị pha đường hóa học", "drink", 1),
    ("vị cafe chuẩn gu mình", "drink", 1),
    ("món mới uống lạ miệng mà cuốn lắm", "drink", 1),
    ("trân châu đường đen mềm dẻo", "drink", 1),
    ("bánh ngọt ở đây ăn rất bon mồm", "drink", 1),
    ("must try món trà vải nhé mọi người", "drink", 1),
    ("cafe không quá ngọt, rất thanh", "drink", 1),
    ("lớp kem cheese mặn mặn béo béo ngon xỉu", "drink", 1),

    # --- Chê (Negative) ---
    ("nước uống nhạt nhẽo như nước lã", "drink", -1),
    ("sinh tố bơ hơi bị đắng", "drink", -1),
    ("bạc xỉu quá ngọt uống gắt cổ", "drink", -1),
    ("trà sữa vị bột béo quá nhiều, ngấy", "drink", -1),
    ("cafe bị chua, uống rất khó chịu", "drink", -1),
    ("đồ uống toàn đá là đá, hút 2 cái là hết", "drink", -1),
    ("trân châu bị cứng như đá", "drink", -1),
    ("hoa quả trong trà bị ủng, không tươi", "drink", -1),
    ("mùi vị kỳ cục, không uống nổi", "drink", -1),
    ("pha chế dở tệ", "drink", -1),
    ("ly nước bị hôi mùi nhựa", "drink", -1),
    ("kem cheese bị vón cục", "drink", -1),
    ("cà phê loãng toẹt", "drink", -1),
    ("bánh cũ, ăn bị khô", "drink", -1),
    ("nước uống chán đời thực sự", "drink", -1),

    # =================================================================
    # 2. SERVICE
    # =================================================================
    # --- Khen (Positive) ---
    ("nhân viên phục vụ rất nhiệt tình", "service", 1),
    ("các bạn nhân viên dễ thương lắm", "service", 1),
    ("bác bảo vệ dắt xe thân thiện", "service", 1),
    ("lên món siêu nhanh, không phải chờ lâu", "service", 1),
    ("nhân viên tư vấn món rất có tâm", "service", 1),
    ("thái độ phục vụ chuyên nghiệp", "service", 1),
    ("mình làm đổ nước nhân viên lau dọn vui vẻ", "service", 1),
    ("phục vụ chu đáo, rót trà đá liên tục", "service", 1),
    ("anh chủ quán vui tính, xởi lởi", "service", 1),
    ("gọi món nhanh gọn lẹ", "service", 1),
    ("nhân viên lễ phép, chào hỏi khách", "service", 1),
    ("duyệt thái độ phục vụ 10 điểm", "service", 1),
    ("service tốt, sẽ quay lại", "service", 1),

    # --- Chê (Negative) ---
    ("gọi món mà chờ dài cả cổ", "service", -1),
    ("thái độ phục vụ lồi lõm", "service", -1),
    ("nhân viên order nhầm món", "service", -1),
    ("phục vụ quá chậm chạp", "service", -1),
    ("lên món lâu quá", "service", -1),
    ("nhân viên làm việc lề mề", "service", -1),
    ("chờ đợi mòn mỏi mới có nước", "service", -1),
    ("nhân viên coi thường khách", "service", -1),
    ("gọi nhân viên mãi không thưa", "service", -1),
    ("bảo vệ khó chịu, nạt nộ khách", "service", -1),
    ("đợi 30 phút chưa có ly nước", "service", -1),
    ("nhân viên tụ tập nói chuyện ồn ào", "service", -1),
    ("thái độ như mẹ thiên hạ", "service", -1),
    ("chất lượng phục vụ kém", "service", -1),
    ("nhân viên mặt như đâm lê", "service", -1),
    ("hỏi pass wifi mà nhân viên cau có", "service", -1),
    ("phục vụ thiếu chuyên nghiệp", "service", -1),

    # =================================================================
    # 3. PRICE
    # =================================================================
    # --- Khen (Positive) ---
    ("giá rẻ", "price", 1),
    ("rẻ bất ngờ", "price", 1),
    ("giá hạt rẻ", "price", 1),
    ("không hề đắt", "price", 1),
    ("rẻ vãi", "price", 1),
    ("giá hạt dẻ", "price", 1),
    ("nước rẻ", "price", 1),
    ("Nước uống không những rẻ", "price", 1),
    ("giá cả rất hợp lý với sinh viên", "price", 1),
    ("giá rẻ bất ngờ", "price", 1),
    ("đáng đồng tiền bát gạo", "price", 1),
    ("giá này là quá hời", "price", 1),
    ("nước ngon mà giá hạt dẻ", "price", 1),
    ("thường xuyên có khuyến mãi", "price", 1),
    ("giá bình dân, phù hợp đi hàng ngày", "price", 1),
    ("không thu thêm phí gửi xe", "price", 1),
    ("giá mềm xèo", "price", 1),
    ("với chất lượng này thì giá quá ok", "price", 1),

    # --- Chê (Negative) ---
    ("nước quá đắt so với chất lượng", "price", -1),
    ("một ly nước 80k là quá mắc", "price", -1),
    ("tính tiền sai bill", "price", -1),
    ("giá trên trời", "price", -1),
    ("quán hút máu khách hàng", "price", -1),
    ("giá chát quá", "price", -1),
    ("thu thêm VAT mà không báo trước", "price", -1),
    ("phụ thu phí dịch vụ vô lý", "price", -1),
    ("ly bé tẹo mà giá 60k", "price", -1),
    ("không xứng đáng với số tiền bỏ ra", "price", -1),
    ("giá hơi cao so với mặt bằng chung", "price", -1),
    ("tính tiền gửi xe riêng là điểm trừ", "price", -1),
    ("đắt cắt cổ", "price", -1),

    # =================================================================
    # 4. AMBIANCE
    # =================================================================
    # --- Khen (Positive) ---
    ("không gian quán decor rất đẹp", "ambiance", 1),
    ("view sống ảo cực chill", "ambiance", 1),
    ("máy lạnh mát mẻ dễ chịu", "ambiance", 1),
    ("quán yên tĩnh, thích hợp làm việc", "ambiance", 1),
    ("nhạc hay, nhẹ nhàng", "ambiance", 1),
    ("nhà vệ sinh sạch sẽ, thơm tho", "ambiance", 1),
    ("bàn ghế ngồi thoải mái", "ambiance", 1),
    ("có nhiều góc chụp hình đẹp", "ambiance", 1),
    ("wifi mạnh, chạy vù vù", "ambiance", 1),
    ("không gian thoáng đãng, nhiều cây xanh", "ambiance", 1),
    ("quán thơm mùi tinh dầu dễ chịu", "ambiance", 1),
    ("chỗ để xe rộng rãi", "ambiance", 1),
    ("decor xinh xỉu", "ambiance", 1),

    # --- Chê (Negative) ---
    ("quán ồn ào quá không làm việc được", "ambiance", -1),
    ("nhà vệ sinh bẩn và hôi", "ambiance", -1),
    ("quán nóng nực, bí bách", "ambiance", -1),
    ("nhạc mở to đau cả đầu", "ambiance", -1),
    ("wifi yếu xìu, không load nổi web", "ambiance", -1),
    ("bàn ghế dính bụi bẩn", "ambiance", -1),
    ("không gian tối tăm, chật chội", "ambiance", -1),
    ("quán nồng nặc mùi thuốc lá", "ambiance", -1),
    ("chỗ ngồi chật chội, đi lại khó khăn", "ambiance", -1),
    ("sàn nhà dơ, đầy rác", "ambiance", -1),
    ("wifi rớt mạng liên tục", "ambiance", -1),
    ("view nhìn ra bãi rác", "ambiance", -1),
    ("quán đông đúc, xô bồ", "ambiance", -1),
]
