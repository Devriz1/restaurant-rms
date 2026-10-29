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
       NOTIFICATION UTILITY
    ====================================================== */

    function showNotification(message, type = "success") {
        const container = document.getElementById("pos-notification-container");
        if (!container) return;

        const notification = document.createElement("div");
        notification.className = `alert alert-${type === "success" ? "success" : "danger"} alert-dismissible fade show mb-2`;
        notification.setAttribute("role", "alert");
        notification.style.cssText = "position: relative; z-index: 1060; animation: slideIn 0.3s ease-out;";
        notification.innerHTML = `
            <i class="bi bi-${type === "success" ? "check2-circle" : "exclamation-triangle"} me-1"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        container.appendChild(notification);

        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove("show");
                notification.classList.add("fade");
                setTimeout(() => notification.remove(), 300);
            }
        }, 4000);
    }

    function showError(message) {
        console.error("WAITER POS ERROR:", message);
        showNotification(message, "error");
    }

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
        renderKitchenButton();
    }

    /**
     * Brings a specific order row into view inside the Current Order list
     * and flashes it, so the waiter sees what they just added instead of
     * being left looking at the top of the menu.
     *
     * Scrolls the list's own scroll container only — never the page — so the
     * menu grid does not jump away.
     */
    function focusOrderItem(orderItemId) {
        if (!orderItemId) {
            return;
        }

        const row = document.getElementById("oi-" + orderItemId);
        if (!row) {
            return;
        }

        const container =
            document.querySelector("#current-order .custom-scroll") ||
            document.getElementById("current-order");

        if (container && container.scrollHeight > container.clientHeight) {
            // Park the row near the bottom edge of the list, like a POS should.
            const target =
                row.offsetTop - container.clientHeight + row.offsetHeight + 12;

            container.scrollTo({
                top: Math.max(0, target),
                behavior: "smooth"
            });
        }

        row.classList.remove("oi-focus-flash");
        // Force a reflow so re-adding the class restarts the animation.
        void row.offsetWidth;
        row.classList.add("oi-focus-flash");

        setTimeout(() => {
            row.classList.remove("oi-focus-flash");
        }, 1200);
    }

    /* ======================================================
       SEND TO KITCHEN BUTTON STATE
    ====================================================== */

    let kotBusy = false;

    /**
     * Counts dishes in the basket that have not gone to the kitchen yet,
     * summing quantities so a line of 3 reads as 3.
     */
    function pendingItemCount() {
        const rows = document.querySelectorAll(
            '#current-order [data-pending="1"]'
        );

        let total = 0;

        rows.forEach((row) => {
            const qty = parseInt(row.dataset.qty, 10);
            total += isNaN(qty) ? 1 : qty;
        });

        return total;
    }

    /**
     * Renders the fixed Send To Kitchen button: spinner while sending,
     * a live pending count, and disabled when there is nothing to send.
     */
    function renderKitchenButton() {
        const button = document.getElementById("send-kitchen");
        if (!button) {
            return;
        }

        const count = pendingItemCount();
        const hasPending = count > 0;

        if (kotBusy) {
            button.innerHTML =
                '<span class="spinner-border spinner-border-sm me-2"></span>' +
                'Sending to KOT...';
            button.classList.remove("btn-success");
            button.classList.add("btn-secondary");
            button.disabled = true;
            return;
        }

        const badgeClass = hasPending
            ? "bg-white text-success"
            : "bg-white text-secondary";

        button.innerHTML =
            '<i class="bi bi-printer me-2"></i>Send To Kitchen' +
            `<span class="badge ${badgeClass} ms-2">${count}</span>`;

        button.classList.toggle("btn-success", hasPending);
        button.classList.toggle("btn-secondary", !hasPending);
        button.disabled = !hasPending;
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
            focusOrderItem(data.order_item_id);

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

            // A removed row is already gone, so this is a no-op for "remove".
            focusOrderItem(orderItemId);
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

        kotBusy = true;
        renderKitchenButton();

        try {
            const data = await apiPost(ENDPOINTS.sendToKitchen(guestId));

            if (!data.success) {
                showError(data.message || "There are no pending items to send.");
                return;
            }

            updateCurrentOrder(data.html);

            showNotification(data.message || "Order sent to KOT successfully.");
        } catch (error) {
            console.error("SEND TO KOT ERROR:", error);
            showError("Unable to send order to KOT.\n\nPlease check the console log for details.");
        } finally {
            kotBusy = false;
            renderKitchenButton();
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

    document.addEventListener("DOMContentLoaded", function () {
        renderKitchenButton();
    });

    console.log("Waiter POS JavaScript loaded successfully.");
})();