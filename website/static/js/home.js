// Tunggu sampai halaman sepenuhnya dimuat
window.onload = function() {
    // Ambil semua elemen dengan kelas 'alert' yang bukan 'banner-info'
    const flashMessages = document.querySelectorAll('.alert-home');
    
    // Loop untuk mengatur waktu hilangnya pesan flash
    flashMessages.forEach((message) => {
        // Menyembunyikan pesan flash setelah 2 detik
        setTimeout(() => {
            message.style.display = 'none';
        }, 2000); // 2000ms = 2 detik
    });
}


function toggleDropdown() {
        const dropdown = document.querySelector('.dropdown');
        dropdown.classList.toggle('show');
}
