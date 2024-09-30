document.addEventListener('DOMContentLoaded', function () {
    // Slider functionality
    let slideIndex = 0;
    const slides = document.querySelectorAll('.slide');
    const totalSlides = slides.length;
    const prevButton = document.querySelector('.prev');
    const nextButton = document.querySelector('.next');

    // Function to show the current slide and hide others
    function showSlide(index) {
        slides.forEach((slide, i) => {
            if (i === index) {
                slide.classList.add('active');
            } else {
                slide.classList.remove('active');
            }
        });
    }

    // Show the first slide initially
    showSlide(slideIndex);

    // Function to show the next slide
    function showNextSlide() {
        slideIndex = (slideIndex + 1) % totalSlides;
        showSlide(slideIndex);
    }

    // Function to show the previous slide
    function showPrevSlide() {
        slideIndex = (slideIndex - 1 + totalSlides) % totalSlides;
        showSlide(slideIndex);
    }

    // Check if the buttons exist and add event listeners
    if (prevButton) {
        prevButton.addEventListener('click', showPrevSlide);
    }

    if (nextButton) {
        nextButton.addEventListener('click', showNextSlide);
    }

    // Automatic slide change every 10 seconds
    setInterval(showNextSlide, 10000);

    // Calorie Calculator Script
    const calculateBtn = document.getElementById("calculate-btn");
    if (calculateBtn) {
        calculateBtn.addEventListener("click", () => {
            const weight = document.getElementById("weight").value;
            const activityLevel = document.getElementById("activity-level").value;

            if (weight && activityLevel) {
                const calories = weight * 24 * activityLevel;
                document.getElementById("calorie-result").innerText = `You need ${Math.round(calories)} calories per day.`;
            } else {
                document.getElementById("calorie-result").innerText = "Please enter a valid weight and activity level.";
            }
        });
    }

    // Profile Dropdown functionality
    const profileIcon = document.getElementById('profile-icon');
    const profileMenu = document.getElementById('profile-menu');

    if (profileIcon && profileMenu) {
        // Toggle dropdown on icon click
        profileIcon.addEventListener('click', function () {
            profileMenu.classList.toggle('show');
        });

        // Close dropdown if clicked outside
        document.addEventListener('click', function (e) {
            if (!profileIcon.contains(e.target) && !profileMenu.contains(e.target)) {
                profileMenu.classList.remove('show');
            }
        });
    }

    // Plan Filter functionality
    const filterButtons = document.querySelectorAll('.filter-btn');
    const planCards = document.querySelectorAll('.plan-card');

    if (filterButtons.length > 0 && planCards.length > 0) {
        // Add event listener to each filter button
        filterButtons.forEach(button => {
            button.addEventListener('click', function () {
                const filter = this.getAttribute('data-filter');

                // Loop through each plan card and filter by category
                planCards.forEach(card => {
                    const category = card.getAttribute('data-category');
                    if (filter === 'all' || category === filter) {
                        card.style.display = 'block'; // Show matching plans
                    } else {
                        card.style.display = 'none'; // Hide non-matching plans
                    }
                });

                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));

                // Add active class to the clicked button
                this.classList.add('active');
            });
        });
    } else {
        console.error('Filter buttons or plan cards not found!');
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');

    // Add event listener to each filter button
    filterButtons.forEach(button => {
        button.addEventListener('click', function () {
            const filter = this.getAttribute('data-filter');

            // Loop through each product card and filter by category
            productCards.forEach(card => {
                const category = card.getAttribute('data-category');
                if (filter === 'all' || category === filter) {
                    card.style.display = 'block'; // Show matching products
                } else {
                    card.style.display = 'none'; // Hide non-matching products
                }
            });

            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));

            // Add active class to the clicked button
            this.classList.add('active');
        });
    });
});
