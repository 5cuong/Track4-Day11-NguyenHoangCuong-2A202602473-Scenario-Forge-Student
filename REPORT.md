MSSV: 202602473

# Lab 11 · Scenario Forge — báo cáo

## 1. Phát lại log có trung thực không? (bước A)

`evidence/replay.json`: loại 1 log do người lái thật đã va chạm, còn 399 log; planner va chạm 85 lần khi phát lại (82 `rear`, 3 `side`) nhưng chỉ 1 lần trong thế giới phản ứng (1 `front`), và 1 lần va chạm xuất hiện ở cả hai. Phần lớn va chạm `rear` khi phát lại là giả theo nghĩa xe phía sau bị giữ nguyên quỹ đạo trong log, không phản ứng khi ego phanh khác người lái thật; trong mô phỏng phản ứng, xe đó có thể giảm tốc hoặc đổi hành vi. Ví dụ `replay.json: replay_only[0]` là kịch bản 0: phát lại có va chạm từ phía sau, trong khi chạy phản ứng không va chạm và TTC nhỏ nhất là 2.158 s.

## 2. Kịch bản bất khả thi (bước B)

`lab11/feasible.py` loại chuyển làn nếu gia tốc ngang ước tính `(π/cutDur)² × 3.5/2` vượt `μg`, phanh xe chuyển làn nếu `cutBrake > μg`, người đi bộ nếu `pedV > 2.5 m/s`, và xe chuyển làn nếu `cutV` không thuộc `(0, 22] m/s`. Trong `evidence/hunt.json`, cuộc săn `crosswalk_block` có nhiều mẫu bất khả thi nhất (5), so với bus_bypass 4, cut_in 1 và rear_ended 2; CEM bị kéo về các mẫu cực đoan có điểm nguy hiểm cao, nên nếu đếm cả các cảnh không thể xảy ra thì tỷ lệ lỗi sẽ bị thổi phồng và không còn mô tả rủi ro trong thế giới khả thi.

## 3. Monte Carlo cho bạn biết gì (bước C1)

`evidence/mc.json`: `crashes = 2`, `n = 3000`, `p = 0.0006667`, Wilson 95% `[0.0001828, 0.0024277]`. Quy tắc gần đúng `n ≈ 96/p` cho khoảng tương đối ±20% cần khoảng 144,000 lượt chạy. Các kiểu `cut_in`, `crosswalk_block`, `rear_ended` và `other` không xuất hiện trong mẫu tự nhiên; với 0 hit trong 3,000 lần, phải báo cận trên `mc.json: per_mode.*.hi = 0.0012789`, không kết luận xác suất bằng 0.

## 4. Importance sampling, ESS và độ suy biến (bước C3)

Trong bảng, `p` của kiểu không có hit được trình bày bằng cận `upper_zero_hits`, không diễn giải mẫu số 0 quan sát được như rủi ro bằng 0. Các số làm tròn từ `evidence/estimate.json`:

| Kiểu | Seed | p báo cáo | hits | ESS | top_share |
|---|---:|---:|---:|---:|---:|
| bus_bypass | 0 | 0.000246567 | 26 | 109.3 | 0.294 |
| bus_bypass | 1 | 0.000782159 | 25 | 117.7 | 0.237 |
| bus_bypass | 2 | 0.000072624 | 19 | 138.4 | 0.191 |
| cut_in | 0 | ≤0.025 (upper_zero_hits) | 0 | 134.8 | 0.000 |
| cut_in | 1 | ≤0.025 (upper_zero_hits) | 0 | 121.1 | 0.000 |
| cut_in | 2 | ≤0.025 (upper_zero_hits) | 0 | 109.2 | 0.000 |
| crosswalk_block | 0 | 0.000000808 | 78 | 125.5 | 0.465 |
| crosswalk_block | 1 | 0.000000257 | 85 | 111.0 | 0.377 |
| crosswalk_block | 2 | 0.000000549 | 67 | 134.3 | 0.691 |
| rear_ended | 0 | ≤0.025 (upper_zero_hits) | 0 | 103.1 | 0.000 |
| rear_ended | 1 | ≤0.025 (upper_zero_hits) | 0 | 118.2 | 0.000 |
| rear_ended | 2 | ≤0.025 (upper_zero_hits) | 0 | 108.2 | 0.000 |

Ba seed không đồng ý chặt: ước lượng bus_bypass chênh khoảng 10.8 lần, crosswalk_block chênh khoảng 3.1 lần; Monte Carlo thấy 2 bus_bypass nhưng không thấy crosswalk_block. `crosswalk_block`, seed 2 có `top_share = 0.691`, nghĩa là một mẫu nặng đóng góp hơn nửa ước lượng; ESS quanh 103–138 cũng nhỏ hơn nhiều cỡ mẫu danh nghĩa. `estimate.json: budget = 16800`, còn mốc Monte Carlo ±20% từ câu 3 khoảng 144,000 lần; đây là so ngân sách, không phải cam kết cùng độ chính xác. `other` lấy từ `mc.json` (0/3000, cận trên 0.0012789); không được săn như một kiểu cụ thể vì nó là phần dư gộp các va chạm không được gắn nhãn.

## 5. Các kiểu thất bại (bước C2 + 3D)

`evidence/hunt.json` tìm được 83 va chạm bus_bypass và 85 crosswalk_block; cuộc săn mục tiêu cut_in không tìm được cut_in (chỉ ghi 18 bus_bypass), còn cuộc săn rear_ended không tìm được rear_ended (ghi 2 bus_bypass và 17 crosswalk_block). Với bus_bypass, xe C2 lách xe buýt đang dừng để nhập làn trước ego; với crosswalk_block, người đi bộ đi vào đường khi tầm nhìn bị xe buýt che, rồi ego không kịp dừng. Đây là diễn giải cơ chế theo nhãn và tham số kịch bản, cần đối chiếu bằng các ảnh viewer ở đúng khung va chạm. CEM riêng từng kiểu vẫn có thể hút về một kiểu dễ đạt điểm cao; số va chạm ngoài mục tiêu trong hai cuộc săn trên cho thấy một cuộc săn chung có thể bị kiểu trội lấn át. **Ảnh còn thiếu:** `evidence/shots/05-bus-bypass.png` và `evidence/shots/05-crosswalk-block.png`.

## 6. Sửa planner (bước E + 3D)

`evidence/fix.json`: policy được chọn ghi đè `cautionV = 7.0` và `cutinLat = 3.0` (các núm khác giữ mặc định). TRAIN có `fail = 4.0483e-7`, `fail_hi = 7.0520e-7`, `progress = 212.36 m`; ngưỡng tiến độ tối thiểu là 95% baseline TRAIN, tức khoảng 209.09 m. TEST của bản sửa có `fail = 2.9994e-7`, `fail_hi_seen = 4.6431e-7`, `fail_hi = 0.038779`, progress 208.93 m và 8.817 lần phanh gấp trung bình; baseline TEST có `fail = 0.000602764`, `fail_hi_seen = 0.00101957`, `fail_hi = 0.00229847`, progress 217.56 m và 7.869 lần phanh gấp. Cận của bản sửa cao hơn vì `bus_bypass` unseen cộng `upper_zero_hits = 0.0375`, đồng thời `other_crashes` có 0/3000 và cận trên 0.0012789; đó là bất định do chưa quan sát, không phải bằng chứng rằng xác suất thực cao hơn. Hạ `cautionV` nghe có vẻ an toàn hơn vì ego chạy chậm hơn gần vùng bị che, nhưng giao thông phản ứng: xe bám đuôi hoặc xe nhập làn có thể đổi khoảng cách/thời điểm, nên rủi ro có thể chuyển sang va chạm phía sau hoặc cắt ngang; kết quả này phải kiểm tra trên TEST thay vì suy luận đơn điệu từ một núm. **Ảnh bóng mờ còn thiếu:** `evidence/shots/06-fixed-vs-baseline-ghost.png`.

## 7. Từ mô phỏng ra đường thật

Ba giả định tự nhiên đáng đo lại là: (1) `cutGap` có trung vị 14 m — thay bằng khoảng cách nhập làn được gán nhãn từ video/quỹ đạo giao thông tại tuyến tương ứng, có thể dùng [Waymo Open Motion Dataset](https://waymo.com/open/about/) làm nguồn quỹ đạo bổ sung; nếu xe thật chấp nhận khe ngắn hơn, mô phỏng có thể đánh giá thiếu các lần cắt vào nguy hiểm. (2) `pedLook = 0.90` — thay bằng video có gán nhãn hướng nhìn/ngó qua xe buýt tại điểm sang đường; nếu tỷ lệ nhìn thấp hơn giả định, mô phỏng có thể đánh giá thiếu rủi ro người đi bộ không nhường. (3) xác suất đường ướt 0.15 và `μ = 0.5` — thay bằng tỷ lệ thời tiết địa phương ghép với đo ma sát mặt đường theo phương pháp [FHWA locked-wheel tester](https://infotechnology.fhwa.dot.gov/locked-wheel-tester/); nếu đường ướt thường xuyên hơn hoặc ma sát thấp hơn, mô phỏng hiện tại có thể đánh giá thiếu quãng phanh và rủi ro.

## 8. Giới hạn

Các xác suất này không mô tả mọi kiểu đường vì mô phỏng chỉ có một thị trấn/phố và số loại tác nhân hữu hạn; không chứng minh hành vi người thật vì IDM và phân phối tham số là giả định; cũng không chứng nhận rủi ro cỡ 10⁻⁵ vì Monte Carlo 3,000 lượt và importance sampling có ESS thấp, độ nhạy seed và mẫu đóng góp lớn. Nếu có thêm một tuần, tôi sẽ thu thập quỹ đạo nhập làn, quan sát người đi bộ ở vùng khuất và dữ liệu ma sát của tuyến thật; sau đó tăng Monte Carlo lên gần 144,000 lượt cho mốc ±20% hiện tại và chạy importance sampling nhiều seed độc lập trên một tập TEST mới.

## 9. Rắc rối của bạn (bước G + chương 10)

Rắc rối là người đi bộ băng ngang giữa phố từ lề đường vào làn ego ở gần vùng khuất, gần xe buýt đang đỗ; `hazard.json` đặt kịch bản gốc tại `x = 90 m`, `v = 1.4 m/s`, `t0 = 7 s`, `trig = 105 m`. `space` quét `x=[90,100]`, `v=[1.2,1.6]`, `t0=[6.5,7.5]`, `trig=[90,120]`; đây là phạm vi sweep quanh cảnh dựng chứ không phải phân phối thực địa. `exposure = 0.05` là prior minh bạch làm tròn từ 8/184 hành vi người đi bộ “hurry to avoid motorist” trong [FHWA-HRT-06-125, chương 5](https://www.fhwa.dot.gov/publications/research/safety/pedbike/06125/chapter5.cfm), không phải tần suất đã đo cho đúng điểm băng ngang này; tốc độ đi bộ tham khảo [FHWA-HRT-98-107](https://www.fhwa.dot.gov/publications/research/safety/pedbike/98107/section2.cfm). `evidence/mine.json` giữ khả thi 0.994 (1491/1500). Với baseline: 27 crash, gồm 24 avoidable, 0 unavoidable, 3 unattributed, 2 low_speed; `P(crash | hazard)=0.016097`, Wilson 95% `[0.010840,0.023840]`, và theo exposure `per_trip=0.0008048` (cận trên 0.001192). Với policy đã chọn: 6 crash, 6 avoidable, 0 unavoidable, 0 unattributed, 0 low_speed; xác suất điều kiện 0.004024, Wilson `[0.001846,0.008752]`, `per_trip=0.0002012` (cận trên 0.000438). Mốc Monte Carlo cho bus_bypass là 2/3000 = 0.000667 (`mc.json`); đây là hai loại sự kiện và cách lấy mẫu khác nhau nên chỉ đặt cạnh nhau để tham khảo, không phải so sánh tuyệt đối. Phân loại avoidable là lạc quan vì bộ oracle biết rắc rối ngay lúc nó bắt đầu; ngược lại, oracle chỉ thử phanh hết cỡ chứ không thử đánh lái nên có thể bỏ sót cách thoát khác. Tôi chưa có bằng chứng tự lái trực tiếp trên đúng hazard H0 nên không khẳng định người lái tránh được; policy hiện tại giảm số crash trong sweep nhưng còn 6 vụ, nên hướng sửa tiếp theo là giảm tốc/chuẩn bị dừng khi vùng nhìn bị che và kiểm tra `cautionRange`, `cautionV`, `pedBuffer` trên TEST mới. **Ảnh hazard chương 10 còn thiếu:** `evidence/shots/09-custom-hazard.png`.
