document.addEventListener("DOMContentLoaded", function () {

    const drawer = document.getElementById("reportCustomizer");
    const openBtn = document.getElementById("openCustomizer");
    const closeBtn = document.getElementById("closeCustomizer");
    const overlay = document.querySelector(".customizer-overlay");

    // ===============================
    // OPEN
    // ===============================

    if (openBtn) {

        openBtn.addEventListener("click", function () {

            drawer.classList.add("show");

        });

    }

    // ===============================
    // CLOSE
    // ===============================

    if (closeBtn) {

        closeBtn.addEventListener("click", function () {

            drawer.classList.remove("show");

        });

    }

    if (overlay) {

        overlay.addEventListener("click", function () {

            drawer.classList.remove("show");

        });

    }

    // ===============================
    // SORTABLE
    // ===============================

    const columnList = document.getElementById("columnList");

    if (typeof Sortable !== "undefined" && columnList) {

        new Sortable(columnList, {

            animation: 200,

            handle: ".drag-handle",

            ghostClass: "sortable-ghost",

            chosenClass: "sortable-chosen",

            dragClass: "sortable-drag"

        });

    }

    // ===============================================
// APPLY
// ===============================================

const applyBtn = document.getElementById("applyColumns");

if (applyBtn) {

    applyBtn.addEventListener("click", function () {

        const table = document.getElementById("salesReportTable");

        const headerRow = table.tHead.rows[0];

        const bodyRows = table.tBodies[0].rows;

        // Get current order from customizer
        const order = [];

        document.querySelectorAll("#columnList .column-option").forEach(item => {

            const checkbox = item.querySelector("input");

            order.push({

                column: checkbox.dataset.column,

                visible: checkbox.checked

            });

        });

        // ---------- REORDER HEADER ----------

        const newHeaders = [];

        order.forEach(col => {

            const th = headerRow.querySelector(
                `th[data-column="${col.column}"]`
            );

            if (th) {

                th.style.display = col.visible ? "" : "none";

                newHeaders.push(th);

            }

        });

        newHeaders.forEach(th => headerRow.appendChild(th));



        // ---------- REORDER BODY ----------

        Array.from(bodyRows).forEach(row => {

            const newCells = [];

            order.forEach(col => {

                const td = row.querySelector(
                    `td[data-column="${col.column}"]`
                );

                if (td) {

                    td.style.display = col.visible ? "" : "none";

                    newCells.push(td);

                }

            });

            newCells.forEach(td => row.appendChild(td));

        });

        drawer.classList.remove("show");

    });

}
    // ===============================
    // RESET
    // ===============================

    const resetBtn = document.getElementById("resetColumns");

    if (resetBtn) {

        resetBtn.addEventListener("click", function () {

            document
                .querySelectorAll("#reportCustomizer input[type='checkbox']")
                .forEach(function (checkbox) {

                    checkbox.checked = true;

                });

            // Automatically apply the reset
            applyBtn.click();

        });

    }

});