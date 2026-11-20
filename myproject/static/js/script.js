document.addEventListener("DOMContentLoaded", function () {
    console.log("Service Management System завантажився!");

    // Підсвічування активного меню
    const links = document.querySelectorAll("header nav a");
    const currentPage = window.location.pathname;

    links.forEach(link => {
        if (link.href.includes(currentPage)) {
            link.style.textDecoration = "none";
        }
    });

    // Миттєвий пошук
    var search = document.getElementById("service_search");
    if (search) {
        search.addEventListener("input", function () {
            var q = search.value.trim().toLowerCase();
            document.querySelectorAll(".card").forEach(function (card) {
                card.hidden = q !== "" && card.dataset.title.indexOf(q) === -1;
            });
        });
    }

    var search = document.addEventListener('DOMContentLoaded', function () {
        const searchInput = document.querySelector('input[name="client_name"]');
        const table = document.querySelector('table');

        if (searchInput && table) {
            searchInput.addEventListener('input', function () {
                const searchTerm = this.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');

                rows.forEach(row => {
                    const name = row.cells[1].textContent.toLowerCase();
                    const phone = row.cells[2].textContent;
                    const email = row.cells[3].textContent.toLowerCase();

                    if (name.includes(searchTerm) || phone.includes(searchTerm) || email.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        }
    });

    // Підтвердження видалення
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            if (!confirm('Ви впевнені що хочете видалити?')) {
                e.preventDefault();
            }
        });
    });
});