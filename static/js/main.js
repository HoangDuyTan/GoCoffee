// ================== LOGIN/ REGISTER ==================
document.addEventListener('DOMContentLoaded', function () {
    const authModal = document.getElementById('authModal');
    const closeBtn = document.querySelector('.close-button');

    const loginBtn = document.getElementById('login-button');
    const loginTabBtn = document.getElementById('login-tab');
    const loginForm = document.getElementById('login-form');

    const registerTabBtn = document.getElementById('register-tab');
    const registerForm = document.getElementById('register-form');

    if (loginBtn) {
        loginBtn.addEventListener('click', function (e) {
            e.preventDefault();
            authModal.style.display = 'flex';
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            authModal.style.display = 'none';
        });
    }

    window.addEventListener('click', function (event) {
        if (event.target == authModal) {
            authModal.style.display = 'none';
        }
    });

    if (loginTabBtn && registerTabBtn) {
        loginTabBtn.addEventListener('click', function () {
            loginTabBtn.classList.add('active');
            registerTabBtn.classList.remove('active');
            loginForm.classList.add('active');
            registerForm.classList.remove('active');
        });
        registerTabBtn.addEventListener('click', function () {
            registerTabBtn.classList.add('active');
            loginTabBtn.classList.remove('active');
            registerForm.classList.add('active');
            loginForm.classList.remove('active');
        });
    }
});

// ================== SWIPER ==================
document.querySelectorAll('.carousel-container').forEach(function (container) {
    const swiperElement = container.querySelector('.swiper');
    const nextBtn = container.querySelector('.swiper-button-next');
    const prevBtn = container.querySelector('.swiper-button-prev');
    const pagination = container.querySelector('.swiper-pagination');

    new Swiper(swiperElement, {
        direction: 'horizontal',
        loop: true,
        slidesPerView: 3,
        spaceBetween: 20,

        pagination: {
            el: pagination,
            clickable: true,
        },

        navigation: {
            nextEl: nextBtn,
            prevEl: prevBtn,
        },
    });
});