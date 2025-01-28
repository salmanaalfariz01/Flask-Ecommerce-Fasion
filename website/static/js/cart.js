// Tombol plus
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
            // Update kuantitas
            const quantityElement = document.getElementById(`quantity${cart_id}`);
            if (quantityElement) {
                quantityElement.textContent = data.quantity; // Update kuantitas
            }
            // Update total harga seluruh keranjang
            updateTotalAmount(data.total);
        });
    });
});

// Tombol minus
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
            // Update kuantitas
            const quantityElement = document.getElementById(`quantity${cart_id}`);
            if (quantityElement) {
                quantityElement.textContent = data.quantity; // Update kuantitas
            }
            // Jika kuantitas menjadi 0, hapus item
            if (data.quantity === 0) {
                removeCartItem(cart_id);
            }
            // Update total harga seluruh keranjang
            updateTotalAmount(data.total);
        });
    });
});

// Fungsi untuk memperbarui total harga seluruh keranjang
function updateTotalAmount(total) {
    const totalAmountElement = document.getElementById("totalamount");
    if (totalAmountElement) {
        totalAmountElement.textContent = total.toLocaleString(); // Update total harga
    }
}

// Fungsi untuk menghapus item dari keranjang
function removeCartItem(cart_id) {
    const cartItemElement = document.getElementById(`cart-item${cart_id}`);
    if (cartItemElement) {
        cartItemElement.remove(); // Hapus elemen keranjang dari DOM
    }
}




    // Toggle dropdown menu
    function toggleDropdown() {
        const dropdownMenu = document.querySelector('.dropdown-menu');
        dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
    }

    // Bind dropdown toggle function to the button
    const dropdownButton = document.querySelector('.dropdown-toggle');
    if (dropdownButton) {
        dropdownButton.addEventListener('click', toggleDropdown);
    };
