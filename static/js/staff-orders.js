// =========================
// UPDATE ORDER STATUS
// =========================

function updateOrderStatus(orderId) {

    const select = document.getElementById(
        "status-" + orderId
    );

    if (!select) {
        alert("Status selector not found.");
        return;
    }

    const status = select.value;

    fetch("/staff/orders/update-status", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            order_id: orderId,
            status: status
        })

    })

    .then(response => response.json())

    .then(data => {

        if (data.success) {

            alert("Order status updated successfully.");

            location.reload();

        } else {

            alert(
                data.message ||
                "Failed to update order status."
            );

        }

    })

    .catch(error => {

        console.error(
            "UPDATE STATUS ERROR:",
            error
        );

        alert(
            "Something went wrong while updating the order."
        );

    });
}


// =========================
// DELETE ORDER
// =========================

function deleteOrder(orderId) {

    const confirmed = confirm(
        "Are you sure you want to delete Order #" +
        orderId +
        "?"
    );

    if (!confirmed) {
        return;
    }


    fetch("/staff/orders/delete", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            order_id: orderId
        })

    })

    .then(response => response.json())

    .then(data => {

        if (data.success) {

            alert("Order deleted successfully.");

            location.reload();

        } else {

            alert(
                data.message ||
                "Failed to delete order."
            );

        }

    })

    .catch(error => {

        console.error(
            "DELETE ORDER ERROR:",
            error
        );

        alert(
            "Something went wrong while deleting the order."
        );

    });
}


// =========================
// SEARCH ORDERS
// =========================

function filterOrders() {

    const searchInput =
        document.getElementById("orderSearch");

    const statusFilter =
        document.getElementById("statusFilter");

    const search =
        searchInput.value.toLowerCase();

    const selectedStatus =
        statusFilter.value;

    const orderCards =
        document.querySelectorAll(".order-card");


    orderCards.forEach(card => {

        const orderId =
            card.dataset.orderId.toLowerCase();

        const customerId =
            card.dataset.customerId.toLowerCase();

        const status =
            card.dataset.status;


        const matchesSearch =
            orderId.includes(search) ||
            customerId.includes(search);

        const matchesStatus =
            selectedStatus === "All" ||
            status === selectedStatus;


        if (matchesSearch && matchesStatus) {

            card.style.display = "";

        } else {

            card.style.display = "none";

        }

    });
}


// =========================
// PAGE LOAD
// =========================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        const searchInput =
            document.getElementById("orderSearch");

        const statusFilter =
            document.getElementById("statusFilter");


        if (searchInput) {

            searchInput.addEventListener(
                "input",
                filterOrders
            );

        }


        if (statusFilter) {

            statusFilter.addEventListener(
                "change",
                filterOrders
            );

        }

    }
);