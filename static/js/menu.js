document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // CATEGORY FILTER
    // =========================

    const categoryButtons = document.querySelectorAll(".category");
    const menuCards = document.querySelectorAll(".menu-card");

    categoryButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const category = this.getAttribute("data-category");

            // Remove active from all buttons
            categoryButtons.forEach(function (btn) {
                btn.classList.remove("active");
            });

            // Add active to clicked button
            this.classList.add("active");

            // Filter menu cards
            menuCards.forEach(function (card) {

                if (category === "all") {

                    card.style.display = "block";

                } else if (card.classList.contains(category)) {

                    card.style.display = "block";

                } else {

                    card.style.display = "none";

                }

            });

        });

    });

});