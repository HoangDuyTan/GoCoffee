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
                if (res.status === 401) { alert("Vui lòng đăng nhập"); return; }
                if (!res.ok) { console.error("CSRF hoặc server lỗi", res.status); return; }
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
