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
document.addEventListener("DOMContentLoaded", function () {

    window.submitFilters = function () {
        const scrollY = window.scrollY;
        sessionStorage.setItem("scrollY", scrollY);

        document.getElementById("filters").submit();
    };

    const savedScroll = sessionStorage.getItem("scrollY");
    if (savedScroll !== null) {
        window.scrollTo(0, parseInt(savedScroll));
        sessionStorage.removeItem("scrollY");
    }

});
const shopList = document.getElementById("shop-list");
const shopMap = document.getElementById("shop-map");
const listBtn = document.getElementById("list-btn");
const mapBtn = document.getElementById("map-btn");

function showList() {
    listBtn.classList.add("active");
    mapBtn.classList.remove("active");
    shopList.style.display = "block";
    shopMap.style.display = "none";
}

function showMap() {
    mapBtn.classList.add("active");
    listBtn.classList.remove("active");
    shopList.style.display = "none";
    shopMap.style.display = "block";
    loadMap();
}

document.addEventListener("DOMContentLoaded", () => {
    const mode = sessionStorage.getItem("viewMode") || "list";
    if (mode === "shop-list") {
        showList();
    } else {
        showMap();
    }
    listBtn.addEventListener("click", () => {
        sessionStorage.setItem("viewMode", "shop-list");
        showList();
    });
    mapBtn.addEventListener("click", () => {
        sessionStorage.setItem("viewMode", "shop-map");
        showMap();
    });
});

let map;
let maploaded = false

function loadMap() {
    if (!maploaded) {
        map = L.map('map').setView([10.7769, 106.7009], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        markersLayer = L.layerGroup().addTo(map);
        maploaded = true;
    }

    const params = new URLSearchParams(
        new FormData(document.getElementById("filters"))
    );

    fetch("/api/shops/map/?" + params)
        .then(res => res.json())
        .then(data => {
            markersLayer.clearLayers();

            data.forEach(shop => {
                if (!shop.lat || !shop.lng) return;

                const icon = L.divIcon({
                    className: "custom-marker",
                    html: `<div class="marker-rating">${shop.rating}<i class="fa-solid fa-star"></i></div>`
                });

                const marker = L.marker([shop.lat, shop.lng], {icon: icon})
                    .addTo(markersLayer)
                    .bindPopup(`
                        <b>${shop.name}</b><br>
                        ${shop.cover_image ? `<img src="${shop.cover_image}" class="map-popup-img">` : ""}<br>
                        ${shop.rating} <i class="fa-solid fa-star"></i><br>
                        ${shop.address ?? ""}
                    `);
            });

            if (data.length > 0) {
                map.setView([data[0].lat, data[0].lng], 13);
            }
        });
}


