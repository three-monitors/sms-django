document.addEventListener("DOMContentLoaded", function () {
    console.log("Service Management System завантажився!");

    // 1. Підсвічування активного меню
    const links = document.querySelectorAll("header nav a");
    const currentPage = window.location.pathname;

    links.forEach(link => {
        if (link.getAttribute("href") === currentPage) {
            link.style.textDecoration = "none";
        }
    });

    // 2. Миттєвий пошук + миттєва фільтрація за статусом по кнопках
    const searchInput = document.querySelector(
        'input[name="client_name"], input[name="service_name"], input[name="search"]'
    );
    const statusButtons = document.querySelectorAll(".status-filters .status-button");
    const table = document.querySelector("table");
    const countSpan = document.getElementById("orders-count");

    let activeStatus = "";

    const filterTable = function () {
        if (!table) return;

        const searchTerm = searchInput ? searchInput.value.trim().toLowerCase() : "";
        const rows = table.querySelectorAll("tr");
        let visibleCount = 0;

        rows.forEach((row, index) => {
            // Пропускаємо рядок заголовків (<th>)
            if (index === 0 && row.querySelector("th")) {
                return;
            }

            const cells = Array.from(row.cells);
            const searchableText = cells
                .slice(0, -1)
                .map(cell => cell.textContent.toLowerCase())
                .join(" ");

            // На сторінці замовлень колонка статусу має індекс 3
            const statusText = cells[3] ? cells[3].textContent.trim().toLowerCase() : "";

            const matchesSearch = searchableText.includes(searchTerm);
            const matchesStatus = !activeStatus || statusText === activeStatus;

            if (matchesSearch && matchesStatus) {
                row.style.display = "";
                visibleCount++;
            } else {
                row.style.display = "none";
            }
        });

        if (countSpan) {
            countSpan.textContent = visibleCount;
        }
    };

    if (searchInput && table) {
        searchInput.addEventListener("input", filterTable);
    }

    if (statusButtons.length && table) {
        statusButtons.forEach(btn => {
            btn.addEventListener("click", function (e) {
                // На головній сторінці замовлень фільтруємо миттєво без перезавантаження
                if (window.location.pathname === "/orders/") {
                    e.preventDefault();
                    activeStatus = (this.dataset.status || "").toLowerCase();

                    // Перемикаємо підсвічування активної кнопки
                    statusButtons.forEach(b => b.removeAttribute("aria-current"));
                    this.setAttribute("aria-current", "page");

                    filterTable();
                }
            });
        });
    }

    // 3. Підтвердження видалення
    const deleteButtons = document.querySelectorAll(".btn-danger");
    deleteButtons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            if (!confirm("Ви впевнені, що хочете видалити?")) {
                e.preventDefault();
            }
        });
    });
});