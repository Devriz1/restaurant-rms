/* ==========================================================
   WAITER POS - Guest Order Page Module
========================================================== */

(function () {
    "use strict";

    // Configuration & Endpoint Map
    const ENDPOINTS = {
        addItem: "/orders/add-item/",
        updateItem: "/orders/update-item/",
        sendToKitchen: (guestId) => `/orders/guest/${encodeURIComponent(guestId)}/send/`
    };

    /* ======================================================
       UTILITY FUNCTIONS
    ====================================================== */

    /**
     * Extracts CSRF token from document cookies.
     */
    function getCSRFToken() {
        const cookie = document.cookie
            .split("; ")
            .find(row => row.startsWith("rms_csrftoken="));
        return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
    }

    /**
     * Universal fetch wrapper with automatic CSRF & error handling.
     */
    async function apiPost(url, payload = {}) {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify(payload)
        });

        const text = await response.text();
        console.log(`Server Status [${url}]:`, response.status);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${text}`);
        }

        if (!text) {
            throw new Error("The server returned an empty response.");
        }

        try {
            return JSON.parse(text);
        } catch (error) {
            console.error("Invalid JSON response:", text);
            throw new Error("The server did not return valid JSON.");
        }
    }

    /**
     * Updates the order DOM container cleanly.
     */
    function updateCurrentOrder(html) {
        const currentOrder = document.getElementById("current-order");
        if (!currentOrder) {
            console.error("#current-order element was not found.");
            return;
        }
        if (!html) {
            console.warn("No order HTML payload received from server.");
            return;
        }
        currentOrder.innerHTML = html;
    }

    /**
     * Centralized Error Notification
     */
    function showError(message) {
        console.error("WAITER POS ERROR:", message);
        alert(message);
    }

    /* ======================================================
       EVENT HANDLERS
    ====================================================== */

    /**
     * Handles adding items to order.
     */
    async function handleAddItem(button) {
        const menuItemId = button.dataset.item;
        const guestId = button.dataset.guest;

        if (!menuItemId || !guestId) {
            showError("Missing menu item or guest information.");
            return;
        }

        const originalHTML = button.innerHTML;
        button.disabled = true;
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm me-1"></span>
            Adding...
        `;

        try {
            const data = await apiPost(ENDPOINTS.addItem, {
                guest_id: guestId,
                menu_item_id: menuItemId
            });

            if (!data.success) {
                throw new Error(data.message || "Unable to add item.");
            }

            updateCurrentOrder(data.html);

            // Temporary visual feedback
            button.innerHTML = `<i class="bi bi-check-circle"></i> Added`;
            button.classList.replace("btn-success", "btn-primary");

            setTimeout(() => {
                button.innerHTML = originalHTML;
                button.classList.replace("btn-primary", "btn-success");
                button.disabled = false;
            }, 700);

        } catch (error) {
            console.error("ADD ITEM ERROR:", error);
            button.innerHTML = originalHTML;
            button.disabled = false;
            showError(`Unable to add item.\n\n${error.message}`);
        }
    }

    /**
     * Handles updating item quantity or removing an item.
     */
    async function handleUpdateItem(button) {
        const orderItemId = button.dataset.orderItem;
        if (!orderItemId) {
            showError("Order item information is missing.");
            return;
        }

        let action = "";
        if (button.classList.contains("increase-item")) action = "increase";
        else if (button.classList.contains("decrease-item")) action = "decrease";
        else if (button.classList.contains("remove-item")) action = "remove";

        if (!action) return;

        if (action === "remove" && !confirm("Remove this item from the order?")) {
            return;
        }

        button.disabled = true;

        try {
            const data = await apiPost(ENDPOINTS.updateItem, {
                order_item_id: orderItemId,
                action: action
            });

            if (!data.success) {
                throw new Error(data.message || "Unable to update item.");
            }

            updateCurrentOrder(data.html);
        } catch (error) {
            console.error("UPDATE ITEM ERROR:", error);
            showError(`Unable to update order item.\n\n${error.message}`);
        } finally {
            button.disabled = false;
        }
    }

    /**
     * Handles sending order to KOT printer.
     */
    async function handleSendToKitchen(button) {
        const guestId = button.dataset.guest;
        if (!guestId) {
            showError("Guest information is missing.");
            return;
        }

        const originalHTML = button.innerHTML;
        button.disabled = true;
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm me-1"></span>
            Sending to KOT...
        `;

        // Pre-open pop-up to circumvent browser blocking rules
        const printWindow = window.open("about:blank", "_blank");

        try {
            const data = await apiPost(ENDPOINTS.sendToKitchen(guestId));

            if (!data.success) {
                if (printWindow) printWindow.close();
                showError(data.message || "There are no pending items to send.");
                return;
            }

            updateCurrentOrder(data.html);

            if (printWindow && data.kot_url) {
                printWindow.location.href = data.kot_url;
            }

            alert(data.message || "Order sent to KOT successfully.");
        } catch (error) {
            console.error("SEND TO KOT ERROR:", error);
            if (printWindow) printWindow.close();
            showError("Unable to send order to KOT.\n\nPlease check the console log for details.");
        } finally {
            button.disabled = false;
            button.innerHTML = originalHTML;
        }
    }

    /* ======================================================
       GLOBAL EVENT DELEGATION
    ====================================================== */

    document.addEventListener("click", function (event) {
        const addItemBtn = event.target.closest(".add-item");
        if (addItemBtn && !addItemBtn.disabled) {
            event.preventDefault();
            handleAddItem(addItemBtn);
            return;
        }

        const updateItemBtn = event.target.closest(".increase-item, .decrease-item, .remove-item");
        if (updateItemBtn && !updateItemBtn.disabled) {
            event.preventDefault();
            handleUpdateItem(updateItemBtn);
            return;
        }

        const sendKitchenBtn = event.target.closest("#send-kitchen");
        if (sendKitchenBtn && !sendKitchenBtn.disabled) {
            event.preventDefault();
            handleSendToKitchen(sendKitchenBtn);
            return;
        }
    });

    console.log("Waiter POS JavaScript loaded successfully.");
})();