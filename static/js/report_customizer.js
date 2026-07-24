document.addEventListener("DOMContentLoaded", function () {

    const drawer = document.getElementById("reportCustomizer");
    const openBtn = document.getElementById("openCustomizer");
    const closeBtn = document.getElementById("closeCustomizer");
    const overlay = document.querySelector(".customizer-overlay");

    // ===============================================
    // OPEN
    // ===============================================

    if (openBtn && drawer) {

        openBtn.addEventListener("click", function () {

            drawer.classList.add("show");

        });

    }

    // ===============================================
    // CLOSE
    // ===============================================

    if (closeBtn && drawer) {

        closeBtn.addEventListener("click", function () {

            drawer.classList.remove("show");

        });

    }

    if (overlay && drawer) {

        overlay.addEventListener("click", function () {

            drawer.classList.remove("show");

        });

    }

    // ===============================================
    // SORTABLE
    // ===============================================

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

            // Automatically find the report table
            const table =
                document.getElementById("salesReportTable") ||
                document.getElementById("paymentReportTable") ||
                document.getElementById("itemReportTable") ||
                document.getElementById("waiterReportTable") ||
                document.getElementById("dailyClosingTable");

            if (!table) return;
            const headerRow = table.tHead.rows[0];
            const bodyRows = table.tBodies[0].rows;

            const order = [];

            document.querySelectorAll("#columnList .column-option").forEach(function (item) {

                const checkbox = item.querySelector("input");

                order.push({

                    column: checkbox.dataset.column,

                    visible: checkbox.checked

                });

            });

            // ==========================
            // REORDER HEADER
            // ==========================

            const newHeaders = [];

            order.forEach(function (col) {

                const th = headerRow.querySelector(
                    `th[data-column="${col.column}"]`
                );

                if (th) {

                    th.style.display = col.visible ? "" : "none";

                    newHeaders.push(th);

                }

            });

            newHeaders.forEach(function (th) {

                headerRow.appendChild(th);

            });

            // ==========================
            // REORDER BODY
            // ==========================

            Array.from(bodyRows).forEach(function (row) {

                const newCells = [];

                order.forEach(function (col) {

                    const td = row.querySelector(
                        `td[data-column="${col.column}"]`
                    );

                    if (td) {

                        td.style.display = col.visible ? "" : "none";

                        newCells.push(td);

                    }

                });

                newCells.forEach(function (td) {

                    row.appendChild(td);

                });

            });

            if (drawer) {

                drawer.classList.remove("show");

            }

        });

    }

    // ===============================================
    // RESET
    // ===============================================

    const resetBtn = document.getElementById("resetColumns");

    if (resetBtn) {

        resetBtn.addEventListener("click", function () {

            document.querySelectorAll(
                "#reportCustomizer input[type='checkbox']"
            ).forEach(function (checkbox) {

                checkbox.checked = true;

            });

            if (applyBtn) {

                applyBtn.click();

            }

        });

    }

});