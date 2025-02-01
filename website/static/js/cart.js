document.querySelectorAll(".plus-cart").forEach(function (button) {
    button.addEventListener("click", function (e) {
        e.preventDefault();
        var cart_id = this.getAttribute('pid');
        fetch(`/pluscart?cart_id=${cart_id}`, {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            
            // Update semua elemen quantity yang sesuai
            document.querySelectorAll(`.quantity${cart_id}`).forEach(element => {
                element.textContent = data.quantity;
            });

            // Update total harga seluruh keranjang
            updateTotalAmount(data.total);
        });
    });
});

document.querySelectorAll(".minus-cart").forEach(function (button) {
    button.addEventListener("click", function (e) {
        e.preventDefault();
        var cart_id = this.getAttribute('pid');
        fetch(`/minuscart?cart_id=${cart_id}`, {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);

            // Update semua elemen quantity yang sesuai
            document.querySelectorAll(`.quantity${cart_id}`).forEach(element => {
                element.textContent = data.quantity;
            });

            // Jika kuantitas jadi 0, hapus item
            if (data.quantity === 0) {
                removeCartItem(cart_id);
            }

            // Update total harga seluruh keranjang
            updateTotalAmount(data.total);
        });
    });
});





function toggleDropdown() {
    const dropdown = document.querySelector('.dropdown');
    dropdown.classList.toggle('show');
}


// Fungsi untuk memperbarui total harga seluruh keranjang
function updateTotalAmount(total) {
    const totalAmountElement = document.getElementById("totalamount");
    if (totalAmountElement) {
        totalAmountElement.textContent = total.toLocaleString(); // Update total harga
    }
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




