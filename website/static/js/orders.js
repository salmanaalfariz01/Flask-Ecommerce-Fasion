// Fungsi untuk memproses pengiriman form jika sudah lebih dari 1 jam
function autoSubmitOrderForm(orderTime, formId) {
    // Konversi waktu ke dalam millisecond
    const orderTimeMillis = new Date(orderTime).getTime();
    const currentTimeMillis = new Date().getTime();

    // Hitung selisih waktu antara saat ini dan waktu pesanan
    const timeDifference = currentTimeMillis - orderTimeMillis;

    // Jika lebih dari 1 jam (3600000 ms)
    const oneHourMillis = 3600000;
    if (timeDifference >= oneHourMillis) {
        // Otomatis kirim form setelah 1 jam
        document.getElementById(formId).submit();
    } else {
        // Atur waktu mundur untuk mengklik tombol setelah 1 jam
        const timeToClick = oneHourMillis - timeDifference;
        setTimeout(() => {
            document.getElementById(formId).submit();
        }, timeToClick);
    }
}

// Panggil fungsi untuk setiap order yang ada
function setupAutoSubmitOrderForms() {
    // Ambil semua elemen form dengan class 'order-form'
    const orderForms = document.querySelectorAll('.order-form');

    // Loop melalui setiap form untuk mengambil informasi waktu dan ID form
    orderForms.forEach(form => {
        const orderTime = form.dataset.orderTime; // Ambil waktu pesanan dari data atribut
        const formId = form.id;
        autoSubmitOrderForm(orderTime, formId);
    });
}

// Panggil fungsi saat DOM siap
document.addEventListener('DOMContentLoaded', setupAutoSubmitOrderForms);

function toggleDropdown() {
    const dropdown = document.querySelector('.dropdown');
    dropdown.classList.toggle('show');
}



window.onload = function () {
    // Ambil semua elemen dengan kelas 'alert-remove'
    const flashMessages = document.querySelectorAll(".alert-remove");

    // Loop untuk mengatur waktu hilangnya pesan flash
    flashMessages.forEach((message) => {
        setTimeout(() => {
            message.style.opacity = "0"; // Efek menghilang
            setTimeout(() => {
                message.style.display = "none";
            }, 1000); // Sembunyikan setelah efek selesai
        }, 4000); // 4 detik sebelum mulai menghilang
    });
};
