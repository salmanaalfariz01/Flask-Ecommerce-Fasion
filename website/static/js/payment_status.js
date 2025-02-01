// Panggil fungsi saat DOM siap
document.addEventListener('DOMContentLoaded', setupAutoSubmitOrderForms);

function toggleDropdown() {
    const dropdown = document.querySelector('.dropdown');
    dropdown.classList.toggle('show');
}