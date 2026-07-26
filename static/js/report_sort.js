document.addEventListener("DOMContentLoaded", () => {

    const table = document.getElementById("salesReportTable");

    if (!table) return;

    const tbody = table.querySelector("tbody");

    const headers = table.querySelectorAll("thead th");

    headers.forEach((header, index) => {

        let ascending = true;

        header.style.cursor = "pointer";

        header.addEventListener("click", () => {

            const rows = Array.from(tbody.querySelectorAll("tr"));

            rows.sort((a, b) => {

                const aText = a.cells[index].innerText.trim();

                const bText = b.cells[index].innerText.trim();

                const aNum = parseFloat(aText.replace(/[^\d.]/g, ""));
                const bNum = parseFloat(bText.replace(/[^\d.]/g, ""));

                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return ascending ? aNum - bNum : bNum - aNum;
                }

                return ascending
                    ? aText.localeCompare(bText)
                    : bText.localeCompare(aText);

            });

            rows.forEach(row => tbody.appendChild(row));

            ascending = !ascending;

        });

    });

});