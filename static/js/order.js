// =========================
// CART DATA
// =========================

let cart = JSON.parse(localStorage.getItem("cart")) || [];


// =========================
// OPEN CART
// =========================

function openCart() {

    const cartPanel = document.getElementById("cart-panel");
    const cartOverlay = document.getElementById("cart-overlay");

    if (cartPanel) {
        cartPanel.classList.add("show");
    }

    if (cartOverlay) {
        cartOverlay.classList.add("show");
    }

    renderCart();
}


// =========================
// CLOSE CART
// =========================

function closeCart() {

    const cartPanel = document.getElementById("cart-panel");
    const cartOverlay = document.getElementById("cart-overlay");

    if (cartPanel) {
        cartPanel.classList.remove("show");
    }

    if (cartOverlay) {
        cartOverlay.classList.remove("show");
    }
}


// =========================
// ADD TO CART
// =========================

function addToCart(id, name, price) {

    price = parseFloat(price);

    if (isNaN(price)) {
        alert("Invalid price.");
        return;
    }

    const existingItem = cart.find(
        item => item.id == id
    );

    if (existingItem) {

        existingItem.quantity++;

    } else {

        cart.push({
            id: id,
            name: name,
            price: price,
            quantity: 1
        });

    }

    saveCart();

    updateCartCount();

    renderCart();

    alert(name + " added to cart!");
}


// =========================
// SAVE CART
// =========================

function saveCart() {

    localStorage.setItem(
        "cart",
        JSON.stringify(cart)
    );
}


// =========================
// CART COUNT
// =========================

function updateCartCount() {

    const countElement =
        document.getElementById("cart-count");

    if (!countElement) {
        return;
    }

    let totalQuantity = 0;

    cart.forEach(item => {
        totalQuantity += item.quantity;
    });

    countElement.textContent = totalQuantity;
}


// =========================
// DISPLAY CART ITEMS
// =========================

function renderCart() {

    const cartItems =
        document.getElementById("cart-items");

    const cartTotal =
        document.getElementById("cart-total");

    if (!cartItems || !cartTotal) {
        return;
    }


    // EMPTY CART

    if (cart.length === 0) {

        cartItems.innerHTML = `
            <p class="empty-cart">
                Your cart is empty.
            </p>
        `;

        cartTotal.textContent = "0.00";

        return;
    }


    let total = 0;

    cartItems.innerHTML = "";


    cart.forEach(function(item) {

        const subtotal =
            item.price * item.quantity;

        total += subtotal;


        const cartItem =
            document.createElement("div");

        cartItem.className = "cart-item";


        cartItem.innerHTML = `
            
            <div class="cart-item-info">

                <h4>${item.name}</h4>

                <p>
                    ₱${item.price.toFixed(2)}
                    ×
                    ${item.quantity}
                </p>

            </div>


            <div class="cart-item-controls">

                <button
                    type="button"
                    onclick="decreaseQuantity('${item.id}')">
                    −
                </button>

                <span>
                    ${item.quantity}
                </span>

                <button
                    type="button"
                    onclick="increaseQuantity('${item.id}')">
                    +
                </button>

                <button
                    type="button"
                    onclick="removeFromCart('${item.id}')">
                    🗑
                </button>

            </div>

        `;


        cartItems.appendChild(cartItem);

    });


    cartTotal.textContent =
        total.toFixed(2);
}


// =========================
// INCREASE QUANTITY
// =========================

function increaseQuantity(id) {

    const item = cart.find(
        item => item.id == id
    );

    if (item) {

        item.quantity++;

        saveCart();
        updateCartCount();
        renderCart();

    }
}


// =========================
// DECREASE QUANTITY
// =========================

function decreaseQuantity(id) {

    const item = cart.find(
        item => item.id == id
    );

    if (!item) {
        return;
    }


    item.quantity--;


    if (item.quantity <= 0) {

        cart = cart.filter(
            item => item.id != id
        );

    }


    saveCart();

    updateCartCount();

    renderCart();
}


// =========================
// REMOVE ITEM
// =========================

function removeFromCart(id) {

    cart = cart.filter(
        item => item.id != id
    );

    saveCart();

    updateCartCount();

    renderCart();
}


// =========================
// CHECKOUT
// =========================

function checkout() {

    if (cart.length === 0) {
        alert("Your cart is empty.");
        return;
    }

    console.log("SENDING CART:", cart);

    fetch("/checkout", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            items: cart
        })
    })

    .then(async response => {

        console.log("HTTP STATUS:", response.status);
        console.log("HTTP OK:", response.ok);

        const text = await response.text();

        console.log("RAW SERVER RESPONSE:", text);

        let data;

        try {
            data = JSON.parse(text);
        } catch (error) {

            console.error("JSON PARSE ERROR:", error);

            throw new Error(
                "Server returned non-JSON response:\n" + text
            );
        }

        return {
            ok: response.ok,
            data: data
        };
    })

    .then(result => {

        console.log("CHECKOUT RESULT:", result);

        const data = result.data;

        if (data.success) {

            alert(
                "Order placed successfully!\nOrder ID: "
                + data.order_id
            );

            // Clear cart
            cart = [];

            localStorage.removeItem("cart");

            updateCartCount();
            renderCart();

            closeCart();

        } else {

            alert(
                "CHECKOUT FAILED\n\n" +
                "Status: " + (data.status || "Unknown") +
                "\nMessage: " +
                (data.message || "No message from server.")
            );
        }
    })

    .catch(error => {

        console.error("CHECKOUT ERROR:", error);

        alert(
            "CHECKOUT DEBUG ERROR:\n\n" +
            error.message
        );
    });
}


// =========================
// PAGE LOAD
// =========================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        updateCartCount();

        renderCart();

    }
);