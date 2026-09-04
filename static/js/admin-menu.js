document.addEventListener("DOMContentLoaded", function () {

    const categoryButtons =
        document.querySelectorAll(".category");

    const menuCards =
        document.querySelectorAll(".menu-card");


    console.log("Admin Menu Filter Loaded");
    console.log("Menu Cards:", menuCards.length);


    categoryButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const selectedCategory =
                this.dataset.category;


            console.log(
                "Selected Category:",
                selectedCategory
            );


            // =========================
            // ACTIVE BUTTON
            // =========================

            categoryButtons.forEach(function (btn) {

                btn.classList.remove("active");

            });

            this.classList.add("active");


            // =========================
            // FILTER MENU
            // =========================

            menuCards.forEach(function (card) {

                const cardCategory =
                    card.dataset.category;


                console.log(
                    "Card Category:",
                    cardCategory
                );


                if (selectedCategory === "all") {

                    card.style.display = "";

                }

                else if (
                    cardCategory === selectedCategory
                ) {

                    card.style.display = "";

                }

                else {

                    card.style.display = "none";

                }

            });

        });

    });

});