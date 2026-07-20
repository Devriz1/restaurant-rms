function showToast(message, success = true) {

    const toastElement = document.getElementById("appToast");
    const toastMessage = document.getElementById("toast-message");

    toastMessage.innerText = message;

    toastElement.classList.remove(
        "text-bg-success",
        "text-bg-danger",
        "text-bg-warning"
    );

    if (success) {
        toastElement.classList.add("text-bg-success");
    } else {
        toastElement.classList.add("text-bg-danger");
    }

    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}


function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {

            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }
        }
    }

    return cookieValue;
}

const csrftoken = getCookie("csrftoken");


function updateCurrentOrder(html) {

    const container = document.getElementById("current-order");

    if (container && html !== undefined) {
        container.innerHTML = html;
    }

}


function sendOrderUpdate(orderItemId, action) {

    fetch("/orders/update-item/", {

        method: "POST",

        headers: {

            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,

        },

        body: JSON.stringify({

            order_item_id: orderItemId,
            action: action,

        })

    })

    .then(response => response.json())

    .then(data => {

        if (data.success) {

            updateCurrentOrder(data.html);

        }

    })

    .catch(error => {

        console.error(error);

        showToast("Something went wrong.", false);

    });

}


document.addEventListener("click", function (e) {

    /*
    ---------------------------------
    ADD ITEM
    ---------------------------------
    */

    if (e.target.closest(".add-item")) {

        const button = e.target.closest(".add-item");

        fetch("/orders/add-item/", {

            method: "POST",

            headers: {

                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,

            },

            body: JSON.stringify({

                guest_id: button.dataset.guest,
                menu_item_id: button.dataset.item,

            })

        })

        .then(response => response.json())

        .then(data => {

            if (data.success) {

                updateCurrentOrder(data.html);

                showToast("Item added successfully.");

            }

        })

        .catch(error => {

            console.error(error);

            showToast("Unable to add item.", false);

        });

    }


    /*
    ---------------------------------
    INCREASE
    ---------------------------------
    */

    if (e.target.closest(".increase-item")) {

        const button = e.target.closest(".increase-item");

        sendOrderUpdate(button.dataset.orderItem, "increase");

    }


    /*
    ---------------------------------
    DECREASE
    ---------------------------------
    */

    if (e.target.closest(".decrease-item")) {

        const button = e.target.closest(".decrease-item");

        sendOrderUpdate(button.dataset.orderItem, "decrease");

    }


    /*
    ---------------------------------
    REMOVE
    ---------------------------------
    */

    if (e.target.closest(".remove-item")) {

        const button = e.target.closest(".remove-item");

        if (!confirm("Remove this item from the order?")) {
            return;
        }

        sendOrderUpdate(button.dataset.orderItem, "remove");

    }


    /*
    ---------------------------------
    SEND TO KITCHEN
    ---------------------------------
    */

    if (e.target.closest("#send-kitchen")) {

        e.preventDefault();

        const button = e.target.closest("#send-kitchen");

        button.disabled = true;

        fetch(`/orders/guest/${button.dataset.guest}/send/`, {

            method: "POST",

            headers: {

                "X-CSRFToken": csrftoken,

            }

        })

        .then(response => response.json())

        .then(data => {

            if (data.success) {

                if (data.html) {
                    updateCurrentOrder(data.html);
                }

                showToast(data.message);

                if (data.print_url) {
                    window.open(data.print_url, "_blank");
                }

            } else {

                showToast(data.message, false);

            }

            button.disabled = false;

        })

        .catch(error => {

            console.error(error);

            showToast("Unable to send order to kitchen.", false);

            button.disabled = false;

        });

    }

});