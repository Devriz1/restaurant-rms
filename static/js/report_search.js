document.addEventListener("DOMContentLoaded", () => {

    const input = document.getElementById("billSearch");

    if (!input) return;

    const table = document.getElementById("salesReportTable");

    if (!table) return;

    const rows = table.querySelectorAll("tbody tr");

    input.addEventListener("keyup", function () {

        const value = this.value.toLowerCase();

        rows.forEach(row => {

            const text = row.innerText.toLowerCase();

            row.style.display = text.includes(value)
                ? ""
                : "none";

        });

    });

});