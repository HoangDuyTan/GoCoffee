document.addEventListener("DOMContentLoaded", function () {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    // Hàm hiển thị thông báo
    function showNotification(message, type = "info") {
        let container = document.querySelector(".messages-container");
        if (!container) {
            container = document.createElement("div");
            container.className = "messages-container";
            document.body.appendChild(container);
        }

        let cssClass = "alert-info";
        let iconHtml = '<i class="fa-solid fa-circle-info"></i>';

        if (type === "success") {
            cssClass = "alert-success";
            iconHtml = '<i class="fa-solid fa-check-circle"></i>';
        } else if (type === "error") {
            cssClass = "alert-error";
            iconHtml = '<i class="fa-solid fa-circle-exclamation"></i>';
        } else if (type === "warning") {
            cssClass = "alert-warning";
            iconHtml = '<i class="fa-solid fa-triangle-exclamation"></i>';
        }

        const alertDiv = document.createElement("div");
        alertDiv.className = `alert ${cssClass}`;
        alertDiv.innerHTML = `
            <span>${iconHtml} ${message}</span>
            <span class="close-msg">&times;</span>
        `;

        alertDiv.querySelector(".close-msg").addEventListener("click", () => {
            alertDiv.remove();
        });

        container.appendChild(alertDiv);

        setTimeout(() => {
            if (alertDiv) {
                alertDiv.classList.add("hide-me");
                setTimeout(() => alertDiv.remove(), 500);
            }
        }, 3000);
    }

    // XỬ LÝ GỬI REVIEW (FETCH API)
    const reviewForm = document.getElementById("review-form");
    if (reviewForm) {
        reviewForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const url = this.action;
            const ratingInput = this.querySelector('input[name="rating"]:checked');
            const commentInput = document.getElementById("review-comment");
            const commentValue = commentInput.value.trim();

            if (!ratingInput) {
                showNotification("Bạn quên chọn số sao rồi!", "warning");
                return;
            }

            if (!commentValue) {
                showNotification("Hãy viết vài dòng chia sẻ nhé!", "warning");
                commentInput.focus();
                return;
            }

            const formData = new FormData();
            formData.append("rating", ratingInput.value);
            formData.append("comment", commentValue);

            const submitBtn = this.querySelector('.btn-submit-review');
            const originalText = submitBtn.innerText;
            submitBtn.innerText = "Đang gửi";
            submitBtn.disabled = true;

            fetch(url, {
                method: "POST",
                headers: {"X-CSRFToken": csrftoken},
                body: formData,
            }).then(res => {
                if (!res.ok) throw new Error("Lỗi kết nối");
                return res.json();
            }).then(data => {
                if (data.success) {
                    showNotification("Cảm ơn bạn đã đánh giá!", "success");
                    reviewForm.reset();
                    addNewReviewToUI(data.review);
                } else {
                    showNotification(data.message || "Có lỗi xảy ra", "error");
                }
            }).catch(err => {
                console.error(err);
                showNotification("Lỗi hệ thống, vui lòng thử lại sau.", "error");
            }).finally(() => {
                submitBtn.innerText = originalText;
                submitBtn.disabled = false;
            });
        });
    }

    // Hàm tải review mới
    function addNewReviewToUI(review) {
        const container = document.getElementById("new-review-container");
        if (!container) return;

        let starsHtml = "";
        for (let i = 1; i <= 5; i++){
            if (i <= review.rating){
                starsHtml += `<i class="fa-solid fa-star rated"></i>`;
            } else {
                starsHtml += `<i class="fa-regular fa-star"></i>`;
            }
        }

        const html = `
            <div class="review-card" style="animation: popIn 0.5s ease forwards; border-left: 4px solid var(--primary-color);">
                <div class="review-header">
                    <span class="reviewer-name">@${review.username}</span>
                    <span class="review-date">Vừa xong</span>
                </div>
                <div class="review-rating">${starsHtml}</div>
                <p>${review.comment}</p>
            </div>`;
        container.insertAdjacentHTML("afterbegin", html);
    }

    // --- Lưu yêu thích ---
    const btn = document.getElementById("save-btn");
    if (btn) {
        const icon = document.getElementById("save-icon");
        btn.addEventListener("click", function () {
            fetch(btn.dataset.url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({
                    shop_id: btn.dataset.shopId
                })
            })
                .then(res => {
                    if (res.status === 401) {
                        alert("Vui lòng đăng nhập");
                        return;
                    }
                    if (!res.ok) {
                        console.error("CSRF hoặc server lỗi", res.status);
                        return;
                    }
                    return res.json();
                })
                .then(data => {
                    if (!data) return;
                    if (data.saved) {
                        icon.classList.remove("fa-regular");
                        icon.classList.add("fa-solid", "saved");
                    } else {
                        icon.classList.remove("fa-solid", "saved");
                        icon.classList.add("fa-regular");
                    }
                });
        });
    }
// --- Modal review ---
    const reviewModal = document.getElementById("review-modal");
    const allReviewsModal = document.getElementById("all-reviews-modal");
    const reviewsList = document.querySelector(".reviews-list");
    const reviews = document.querySelectorAll(".review-card");

    const MAX_VISIBLE = 3;
// Ẩn review
    reviews.forEach((review, index) => {
        if (index >= MAX_VISIBLE) review.style.display = "none";
    });

    if (reviews.length > MAX_VISIBLE && reviewsList) {

        const oldBtn = reviewsList.querySelector(".btn-show-more-reviews");
        if (oldBtn) oldBtn.remove();

        const moreBtn = document.createElement("button");
        moreBtn.type = "button";
        moreBtn.textContent = "Xem thêm bình luận";
        moreBtn.className = "btn-show-more-reviews btn-submit-review";
        moreBtn.style.margin = "10px 0";
        reviewsList.appendChild(moreBtn);

        moreBtn.addEventListener("click", () => {
            allReviewsModal.innerHTML = "";

            reviews.forEach(r => {
                const clone = r.cloneNode(true);
                clone.style.display = "block";
                allReviewsModal.appendChild(clone);
            });

            reviewModal.classList.add("is-open");
            document.body.style.overflow = "hidden";
        });
    }

// Đóng khi click nền
    reviewModal.addEventListener("click", (e) => {
        if (e.target === reviewModal) closeReviewModal();
    });

// ESC
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && reviewModal.classList.contains("is-open")) {
            closeReviewModal();
        }
    });

    function closeReviewModal() {
        reviewModal.classList.remove("is-open");
        document.body.style.overflow = "";
    }
});
