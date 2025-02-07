function toggleDropdown() {
    const dropdown = document.querySelector('.dropdown');
    dropdown.classList.toggle('show');
}

function confirmDelete(itemId) {
    Swal.fire({
        title: "Are you sure?",
        text: "This product will be deleted permanently!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Yes, delete it!",
        cancelButtonText: "Cancel"
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = "/delete-item/" + itemId;
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    // Scroll ke atas saat halaman dimuat
    window.scrollTo(0, 0);

    // Sembunyikan alert setelah 4 detik
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert-danger');
        alerts.forEach(alert => alert.style.display = 'none');
    }, 4000);
});