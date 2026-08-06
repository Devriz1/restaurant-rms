// ==========================================================
// PURCHASE MODULE
// ==========================================================

document.addEventListener("DOMContentLoaded", function () {

    bindEvents();

    calculatePurchase();

});


// ==========================================================
// BIND EVENTS
// ==========================================================

function bindEvents() {

    document.addEventListener("input", function (e) {

        if (

            e.target.classList.contains("qty") ||

            e.target.classList.contains("rate") ||

            e.target.classList.contains("gst")

        ) {

            calculateRow(

                e.target.closest(".purchase-row")

            );

        }

        if (

            e.target.id === "id_discount" ||

            e.target.id === "id_other_charges"

        ) {

            calculatePurchase();

        }

    });

}


// ==========================================================
// CALCULATE SINGLE ROW
// ==========================================================

function calculateRow(row) {

    if (!row) return;

    const qty = parseFloat(

        row.querySelector(".qty")?.value

    ) || 0;

    const rate = parseFloat(

        row.querySelector(".rate")?.value

    ) || 0;

    const gst = parseFloat(

        row.querySelector(".gst")?.value

    ) || 0;

    const basic = qty * rate;

    const gstAmount = basic * gst / 100;

    const total = basic + gstAmount;

    const totalBox = row.querySelector(".line-total");

    if (totalBox) {

        totalBox.value = total.toFixed(2);

    }

    calculatePurchase();

}


// ==========================================================
// CALCULATE PURCHASE
// ==========================================================

function calculatePurchase() {

    let subtotal = 0;

    let gstTotal = 0;

    let grandTotal = 0;

    document.querySelectorAll(".purchase-row").forEach(function (row) {

        const qty = parseFloat(

            row.querySelector(".qty")?.value

        ) || 0;

        const rate = parseFloat(

            row.querySelector(".rate")?.value

        ) || 0;

        const gst = parseFloat(

            row.querySelector(".gst")?.value

        ) || 0;

        const basic = qty * rate;

        const gstAmount = basic * gst / 100;

        subtotal += basic;

        gstTotal += gstAmount;

    });

    const discount = parseFloat(

        document.getElementById("id_discount")?.value

    ) || 0;

    const other = parseFloat(

        document.getElementById("id_other_charges")?.value

    ) || 0;

    grandTotal = subtotal + gstTotal + other - discount;

    document.getElementById("subtotal").innerText =
        "₹ " + subtotal.toFixed(2);

    document.getElementById("gst-total").innerText =
        "₹ " + gstTotal.toFixed(2);

    document.getElementById("discount-total").innerText =
        "₹ " + discount.toFixed(2);

    document.getElementById("other-total").innerText =
        "₹ " + other.toFixed(2);

    document.getElementById("grand-total").innerText =
        "₹ " + grandTotal.toFixed(2);

}
// ==========================================================
// ADD NEW PURCHASE ITEM
// ==========================================================

const addRowButton = document.getElementById("add-row");

if (addRowButton) {

    addRowButton.addEventListener("click", function () {

        const totalForms = document.querySelector(
            "#id_items-TOTAL_FORMS, #id_purchaseitem_set-TOTAL_FORMS"
        );

        if (!totalForms) {

            console.error("TOTAL_FORMS input not found.");

            return;

        }

        const formIndex = parseInt(totalForms.value);

        const template = document.querySelector(
            "#empty-form tbody"
        );

        const newRow = template.firstElementChild.cloneNode(true);

        // Replace __prefix__ with current index
        newRow.innerHTML = newRow.innerHTML.replace(
            /__prefix__/g,
            formIndex
        );

        // Reset values
        newRow.querySelectorAll("input").forEach(function (input) {

            if (input.type === "number") {

                input.value = "";

            }

            if (input.type === "text" && input.classList.contains("line-total")) {

                input.value = "0.00";

            }

            if (input.type === "checkbox") {

                input.checked = false;

            }

        });

        newRow.querySelectorAll("select").forEach(function (select) {

            select.selectedIndex = 0;

        });

        document
            .getElementById("item-table")
            .appendChild(newRow);

        totalForms.value = formIndex + 1;

    });

}
