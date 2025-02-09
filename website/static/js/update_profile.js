
function toggleDropdown() {
    const dropdown = document.querySelector('.dropdown');
    dropdown.classList.toggle('show');
}

setTimeout(function () {
    let alertBox = document.querySelector(".alert");
    if (alertBox) {
        alertBox.style.transition = "opacity 1s";
        alertBox.style.opacity = "0";
        setTimeout(() => alertBox.remove(), 1000); // Remove from DOM
    }
}, 4000); // Hide after 4 seconds
