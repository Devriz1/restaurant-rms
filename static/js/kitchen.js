/* ==========================================================
   KITCHEN DISPLAY MODULE
   Handles status transitions, cancellation, auto-refresh,
   and fullscreen mode for the kitchen display screen.
   Groups items by bill rather than by station.
========================================================= */

(function () {
    "use strict";

    const ENDPOINTS = {
        updateItem: (itemId) => `/orders/kitchen/item/${encodeURIComponent(itemId)}/update/`,
        cancelItem: (itemId) => `/orders/kitchen/item/${encodeURIComponent(itemId)}/cancel/`,
        startBill: (billId) => `/orders/kitchen/bill/${encodeURIComponent(billId)}/start/`,
        refresh: "/orders/kitchen/refresh/",
    };

    let refreshing = false;
    let autoRefreshTimer = null;

    function getCSRFToken() {
        const cookie = document.cookie
            .split("; ")
            .find(row => row.startsWith("rms_csrftoken="));
        return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
    }

    async function apiRequest(url, method = "POST", payload = {}) {
        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest",
            },
            body: method === "POST" ? JSON.stringify(payload) : undefined,
        });

        const text = await response.text();

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${text}`);
        }

        return JSON.parse(text);
    }

    function showError(message) {
        console.error("KITCHEN ERROR:", message);
    }

    function showNotification(message, type = "success") {
        const notification = document.createElement("div");
        notification.className = `kitchen-notification alert alert-${type === "success" ? "success" : "warning"} mb-0`;
        notification.innerHTML = `<i class="bi bi-${type === "success" ? "check2-circle" : "exclamation-triangle"} me-1"></i>${message}`;
        notification.style.cssText = "position: fixed; top: 20px; right: 20px; z-index: 1050; min-width: 280px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);";
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    function updateClock() {
        const now = new Date();
        const timeEl = document.getElementById("kitchen-last-update");
        if (timeEl) {
            const hours = now.getHours();
            const minutes = now.getMinutes().toString().padStart(2, "0");
            const ampm = hours >= 12 ? "PM" : "AM";
            const displayHours = hours % 12 || 12;
            timeEl.textContent = `${displayHours}:${minutes} ${ampm}`;
        }
    }

    async function handleBillAction(button) {
        const billId = button.dataset.bill;
        const action = button.dataset.action;
        if (!billId || !action) return;

        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

        try {
            const data = await apiRequest(ENDPOINTS.startBill(billId), "POST", {});

            if (data.success) {
                const billEl = document.querySelector(`.kitchen-bill[data-bill="${billId}"]`);
                if (billEl) {
                    if (data.action === "started") {
                        const preparingBtn = billEl.querySelector('[data-action="preparing"]');
                        if (preparingBtn) {
                            preparingBtn.remove();
                        }
                        const itemCards = billEl.querySelectorAll(".kitchen-item-card.pending");
                        itemCards.forEach(card => {
                            card.classList.remove("pending");
                            card.classList.add("preparing");
                            card.setAttribute("data-status", "preparing");
                        });
                    } else if (data.action === "served") {
                        const serveBtn = billEl.querySelector('[data-action="serve"]');
                        if (serveBtn) {
                            serveBtn.remove();
                        }
                        const itemCards = billEl.querySelectorAll(".kitchen-item-card");
                        itemCards.forEach(card => {
                            card.remove();
                        });
                    }
                }
                updateBillCounts();
                updateClock();
                showNotification(data.message, "success");
            } else {
                throw new Error(data.message || "Unable to process bill action.");
            }
        } catch (error) {
            showError(error.message);
            button.innerHTML = action === "preparing"
                ? '<i class="bi bi-play-circle me-1"></i>Preparing'
                : '<i class="bi bi-truck me-1"></i>Serve Bill';
            button.disabled = false;
        }
    }

    async function handleReadyItem(button) {
        const itemId = button.dataset.item;
        if (!itemId) return;

        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

        try {
            const data = await apiRequest(ENDPOINTS.updateItem(itemId), "POST", {
                status: "ready",
            });

            if (data.success) {
                const itemRow = document.getElementById(`kitchen-item-${itemId}`);
                if (itemRow) {
                    itemRow.outerHTML = data.html || itemRow.outerHTML;
                }
                updateBillCounts();
                updateClock();
            } else {
                throw new Error(data.message || "Unable to update item.");
            }
        } catch (error) {
            showError(error.message);
            button.innerHTML = '<i class="bi bi-check2-circle me-1"></i>Ready';
            button.disabled = false;
        }
    }

    async function handleServeItem(button) {
        const itemId = button.dataset.item;
        if (!itemId) return;

        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

        try {
            const data = await apiRequest(ENDPOINTS.updateItem(itemId), "POST", {
                status: "served",
            });

            if (data.success) {
                const itemRow = document.getElementById(`kitchen-item-${itemId}`);
                if (itemRow) {
                    itemRow.remove();
                }
                updateBillCounts();
                updateClock();
            } else {
                throw new Error(data.message || "Unable to update item.");
            }
        } catch (error) {
            showError(error.message);
            button.innerHTML = '<i class="bi bi-truck me-1"></i>Serve';
            button.disabled = false;
        }
    }

    async function handleCancelItem(button) {
        const itemId = button.dataset.item;
        if (!itemId) return;

        if (!confirm("Cancel this item? This action cannot be undone.")) {
            return;
        }

        button.disabled = true;

        try {
            const data = await apiRequest(ENDPOINTS.cancelItem(itemId), "POST", {});

            if (data.success) {
                const itemRow = document.getElementById(`kitchen-item-${itemId}`);
                if (itemRow) {
                    itemRow.remove();
                }
                updateBillCounts();
                updateClock();
            } else {
                throw new Error(data.message || "Unable to cancel item.");
            }
        } catch (error) {
            showError(error.message);
            button.disabled = false;
        }
    }

    function updateBillCounts() {
        let totalBills = 0;
        let totalItems = 0;

        document.querySelectorAll(".kitchen-bill").forEach(function (billEl) {
            const itemCount = billEl.querySelectorAll(".kitchen-item-card").length;
            const billId = billEl.getAttribute("data-bill");
            const countBadge = document.getElementById(`bill-item-count-${billId}`);

            totalItems += itemCount;

            if (countBadge) {
                countBadge.textContent = `${itemCount} Item${itemCount !== 1 ? "s" : ""}`;
                countBadge.classList.toggle("d-none", itemCount === 0);
            }

            if (itemCount === 0) {
                billEl.classList.add("bill-empty");
            } else {
                billEl.classList.remove("bill-empty");
                totalBills++;
            }
        });

        const billCountBadge = document.getElementById("bill-count-badge");
        if (billCountBadge) {
            billCountBadge.textContent = `${totalBills} Bill${totalBills !== 1 ? "s" : ""}`;
        }
    }

    async function handleRefresh() {
        if (refreshing) return;
        refreshing = true;

        const btn = document.getElementById("kitchen-refresh-btn");
        if (btn) {
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            btn.disabled = true;
        }

        try {
            const response = await fetch(ENDPOINTS.refresh, {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (data.html) {
                const container = document.getElementById("kitchen-bills-container");
                if (container) {
                    container.innerHTML = data.html;
                }
            }

            if (data.last_updated) {
                const timeEl = document.getElementById("kitchen-last-update");
                if (timeEl) {
                    timeEl.textContent = data.last_updated;
                }
            }

            updateBillCounts();
            updateClock();
        } catch (error) {
            showError(error.message);
        } finally {
            refreshing = false;
            if (btn) {
                btn.innerHTML = '<i class="bi bi-arrow-clockwise"></i>';
                btn.disabled = false;
            }
        }
    }

    function handleFullscreen() {
        const display = document.getElementById("kitchen-display");
        if (!display) return;

        if (!document.fullscreenElement) {
            display.requestFullscreen().catch(err => {
                console.warn("Fullscreen failed:", err);
            });
        } else {
            document.exitFullscreen();
        }
    }

    function setupEventDelegation() {
        document.addEventListener("click", function (event) {
            const billActionBtn = event.target.closest(".kitchen-bill-action-btn");
            if (billActionBtn && !billActionBtn.disabled) {
                event.preventDefault();
                handleBillAction(billActionBtn);
                return;
            }

            const readyBtn = event.target.closest(".kitchen-ready-btn");
            if (readyBtn && !readyBtn.disabled) {
                event.preventDefault();
                handleReadyItem(readyBtn);
                return;
            }

            const serveBtn = event.target.closest(".kitchen-serve-btn");
            if (serveBtn && !serveBtn.disabled) {
                event.preventDefault();
                handleServeItem(serveBtn);
                return;
            }

            const cancelBtn = event.target.closest(".kitchen-cancel-btn");
            if (cancelBtn && !cancelBtn.disabled) {
                event.preventDefault();
                handleCancelItem(cancelBtn);
                return;
            }

            const refreshBtn = event.target.closest("#kitchen-refresh-btn");
            if (refreshBtn) {
                event.preventDefault();
                handleRefresh();
                return;
            }

            const fullscreenBtn = event.target.closest("#kitchen-fullscreen-btn");
            if (fullscreenBtn) {
                event.preventDefault();
                handleFullscreen();
                return;
            }
        });
    }

    function initAutoRefresh() {
        autoRefreshTimer = setInterval(() => {
            handleRefresh();
        }, 15000);
    }

    function init() {
        setupEventDelegation();
        initAutoRefresh();

        const refreshBtn = document.getElementById("kitchen-refresh-btn");
        if (refreshBtn) {
            refreshBtn.addEventListener("click", handleRefresh);
        }

        const fullscreenBtn = document.getElementById("kitchen-fullscreen-btn");
        if (fullscreenBtn) {
            fullscreenBtn.addEventListener("click", handleFullscreen);
        }

        updateBillCounts();
        updateClock();

        console.log("Kitchen Display JavaScript loaded successfully.");
    }

    document.addEventListener("DOMContentLoaded", init);
})();