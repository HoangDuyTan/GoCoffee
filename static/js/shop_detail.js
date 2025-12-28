
document.addEventListener("DOMContentLoaded", function () {

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    const btn = document.getElementById("save-btn");
    if (!btn) return;

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
                return null;
            }
            if (!res.ok) {
                console.error("CSRF hoặc server lỗi", res.status);
                return null;
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
});
