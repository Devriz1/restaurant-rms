/* ==========================================================
   WAITER POS
   Guest Order Page
========================================================== */

(function () {

    "use strict";


    /* ======================================================
       CSRF TOKEN
    ====================================================== */

    function getCSRFToken() {

        const cookie = document.cookie
            .split("; ")
            .find(function (row) {
                return row.startsWith("csrftoken=");
            });

        if (!cookie) {
            return "";
        }

        return decodeURIComponent(
            cookie.substring("csrftoken=".length)
        );
    }


    /* ======================================================
       PARSE RESPONSE
    ====================================================== */

    async function parseResponse(response) {

        const text = await response.text();

        console.log(
            "Server status:",
            response.status
        );

        console.log(
            "Server response:",
            text
        );


        if (!response.ok) {

            throw new Error(
                "HTTP " +
                response.status +
                ": " +
                text
            );
        }


        if (!text) {

            throw new Error(
                "The server returned an empty response."
            );
        }


        try {

            return JSON.parse(text);

        } catch (error) {

            console.error(
                "Invalid JSON response:",
                text
            );

            throw new Error(
                "The server did not return valid JSON."
            );
        }
    }


    /* ======================================================
       UPDATE CURRENT ORDER HTML
    ====================================================== */

    function updateCurrentOrder(html) {

        const currentOrder =
            document.getElementById(
                "current-order"
            );


        if (!currentOrder) {

            console.error(
                "#current-order was not found."
            );

            return;
        }


        if (!html) {

            console.warn(
                "No order HTML received from server."
            );

            return;
        }


        currentOrder.innerHTML = html;
    }


    /* ======================================================
       SHOW ERROR
    ====================================================== */

    function showError(message) {

        console.error(
            "WAITER POS ERROR:",
            message
        );

        alert(message);
    }


    /* ======================================================
       ADD MENU ITEM
    ====================================================== */

    document.addEventListener(
        "click",
        function (event) {

            const button =
                event.target.closest(
                    ".add-item"
                );


            if (!button) {
                return;
            }


            event.preventDefault();


            if (button.disabled) {
                return;
            }


            const menuItemId =
                button.dataset.item;

            const guestId =
                button.dataset.guest;


            if (!menuItemId) {

                showError(
                    "Menu item information is missing."
                );

                return;
            }


            if (!guestId) {

                showError(
                    "Guest information is missing."
                );

                return;
            }


            const originalHTML =
                button.innerHTML;


            button.disabled = true;


            button.innerHTML = `
                <span
                    class="spinner-border spinner-border-sm me-1">
                </span>
                Adding...
            `;


            fetch(
                "/orders/add-item/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "X-CSRFToken":
                            getCSRFToken(),

                        "X-Requested-With":
                            "XMLHttpRequest"
                    },

                    body: JSON.stringify({
                        guest_id:
                            guestId,

                        menu_item_id:
                            menuItemId
                    })
                }
            )

            .then(parseResponse)

            .then(function (data) {

                console.log(
                    "ADD ITEM:",
                    data
                );


                if (!data.success) {

                    throw new Error(
                        data.message ||
                        "Unable to add item."
                    );
                }


                updateCurrentOrder(
                    data.html
                );


                button.innerHTML = `
                    <i class="bi bi-check-circle"></i>
                    Added
                `;


                button.classList.remove(
                    "btn-success"
                );

                button.classList.add(
                    "btn-primary"
                );


                setTimeout(
                    function () {

                        button.innerHTML =
                            originalHTML;

                        button.classList.remove(
                            "btn-primary"
                        );

                        button.classList.add(
                            "btn-success"
                        );

                        button.disabled =
                            false;

                    },
                    700
                );

            })

            .catch(function (error) {

                console.error(
                    "ADD ITEM ERROR:",
                    error
                );


                button.innerHTML =
                    originalHTML;

                button.disabled =
                    false;


                showError(
                    "Unable to add item.\n\n" +
                    error.message
                );
            });

        }
    );


    /* ======================================================
       INCREASE / DECREASE / REMOVE ITEM
    ====================================================== */

    document.addEventListener(
        "click",
        function (event) {

            const button =
                event.target.closest(
                    ".increase-item, " +
                    ".decrease-item, " +
                    ".remove-item"
                );


            if (!button) {
                return;
            }


            event.preventDefault();


            if (button.disabled) {
                return;
            }


            const orderItemId =
                button.dataset.orderItem;


            if (!orderItemId) {

                showError(
                    "Order item information is missing."
                );

                return;
            }


            let action = "";


            if (
                button.classList.contains(
                    "increase-item"
                )
            ) {

                action = "increase";

            }


            else if (
                button.classList.contains(
                    "decrease-item"
                )
            ) {

                action = "decrease";

            }


            else if (
                button.classList.contains(
                    "remove-item"
                )
            ) {

                action = "remove";

            }


            if (!action) {

                console.error(
                    "Unknown order action."
                );

                return;
            }


            /*
             * Optional confirmation for delete.
             */

            if (action === "remove") {

                const confirmed =
                    window.confirm(
                        "Remove this item from the order?"
                    );


                if (!confirmed) {
                    return;
                }
            }


            updateOrderItem(
                orderItemId,
                action,
                button
            );

        }
    );


    /* ======================================================
       UPDATE ORDER ITEM
    ====================================================== */

    function updateOrderItem(
        orderItemId,
        action,
        button
    ) {

        if (button) {
            button.disabled = true;
        }


        fetch(
            "/orders/update-item/",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",

                    "X-CSRFToken":
                        getCSRFToken(),

                    "X-Requested-With":
                        "XMLHttpRequest"
                },

                body: JSON.stringify({
                    order_item_id:
                        orderItemId,

                    action:
                        action
                })
            }
        )

        .then(parseResponse)

        .then(function (data) {

            console.log(
                "UPDATE ITEM:",
                data
            );


            if (!data.success) {

                throw new Error(
                    data.message ||
                    "Unable to update item."
                );
            }


            updateCurrentOrder(
                data.html
            );

        })

        .catch(function (error) {

            console.error(
                "UPDATE ITEM ERROR:",
                error
            );


            showError(
                "Unable to update order item.\n\n" +
                error.message
            );

        })

        .finally(function () {

            if (button) {
                button.disabled = false;
            }

        });

    }


    /* ======================================================
       SEND TO KITCHEN / SEND TO KOT
    ====================================================== */

    document.addEventListener(
        "click",
        function (event) {

            const button =
                event.target.closest(
                    "#send-kitchen"
                );


            if (!button) {
                return;
            }


            event.preventDefault();


            if (button.disabled) {
                return;
            }


            const guestId =
                button.dataset.guest;


            if (!guestId) {

                showError(
                    "Guest information is missing."
                );

                return;
            }


            const originalHTML =
                button.innerHTML;


            button.disabled = true;


            button.innerHTML = `
                <span
                    class="spinner-border spinner-border-sm me-1">
                </span>
                Sending to KOT...
            `;


             /*
              * IMPORTANT:
              *
              * This URL matches your Django view:
              *
              * send_to_kitchen(request, guest_id)
              *
              */

            const url =
                "/orders/guest/" +
                encodeURIComponent(guestId) +
                "/send/";


            /*
             * Open a blank window immediately so the browser
             * does not block the later navigation as a popup.
             */

            const printWindow =
                window.open(
                    "about:blank",
                    "_blank"
                );


            console.log(
                "Sending order to:",
                url
            );


            fetch(
                url,
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken":
                            getCSRFToken(),

                        "X-Requested-With":
                            "XMLHttpRequest"
                    }
                }
            )

            .then(parseResponse)

            .then(function (data) {

                console.log(
                    "SEND TO KOT:",
                    data
                );


                /*
                 * Django can return:
                 *
                 * {
                 *     success: false,
                 *     message: "No new items to send."
                 * }
                 *
                 * or:
                 *
                 * {
                 *     success: true,
                 *     message: "...",
                 *     html: "..."
                 * }
                 */

                if (!data.success) {

                    /*
                     * "No new items to send" is not
                     * a JavaScript/network error.
                     */

                    showError(
                        data.message ||
                        "There are no pending items to send."
                    );

                    if (printWindow) {

                        printWindow.close();
                    }

                    return;
                }


                /*
                 * THIS IS IMPORTANT.
                 *
                 * Django has now assigned the KOT
                 * to the pending OrderItems.
                 *
                 * The returned HTML contains:
                 *
                 * Sent to KOT
                 *
                 * instead of:
                 *
                 * Pending
                 */

                updateCurrentOrder(
                    data.html
                );


                /*
                 * Navigate the pre-opened window
                 * to the KOT print page.
                 */

                if (printWindow && data.kot_url) {

                    printWindow.location.href =
                        data.kot_url;
                }


                /*
                 * Success notification.
                 */

                alert(
                    data.message ||
                    "Order sent to KOT successfully."
                );

            })

            .catch(function (error) {

    console.error(
        "SEND TO KOT ERROR:",
        error
    );

    if (printWindow) {

        printWindow.close();
    }

    showError(
        "Unable to send order to KOT.\n\n" +
        "Please check the browser console for the actual server error."
    );

})
            .finally(function () {

                button.disabled =
                    false;


                button.innerHTML =
                    originalHTML;

            });

        }
    );


    /* ======================================================
       INITIALIZATION
    ====================================================== */

    console.log(
        "Waiter POS JavaScript loaded successfully."
    );

})();