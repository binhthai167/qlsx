function toggleDropdown(event, dropdownId) {
    event.preventDefault();
    const dropdown = document.getElementById(dropdownId);
    dropdown.classList.toggle("show");

    // Đóng menu khi click ra ngoài
    window.onclick = function(e) {
        if (!e.target.closest('.dropdown')) {
            dropdown.classList.remove("show");
        }
    };
}