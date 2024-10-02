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
            slide.classList.toggle('active', i === index);
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

    // Add event listeners to prev/next buttons
    prevButton?.addEventListener('click', showPrevSlide);
    nextButton?.addEventListener('click', showNextSlide);

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

    // Plan Filter functionality (Only for pages with plans)
    const currentPath = window.location.pathname;
    if (currentPath === '/shop/' || currentPath === '/plans/') {
        const filterButtons = document.querySelectorAll('.filter-btn');
        const planCards = document.querySelectorAll('.plan-card');

        filterButtons.forEach(button => {
            button.addEventListener('click', function () {
                const filter = this.getAttribute('data-filter');

                planCards.forEach(card => {
                    const category = card.getAttribute('data-category');
                    card.style.display = (filter === 'all' || category === filter) ? 'block' : 'none';
                });

                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // Product Filter functionality (Only for shop page)
    if (currentPath === '/shop/') {
        const filterButtons = document.querySelectorAll('.filter-btn');
        const productCards = document.querySelectorAll('.product-card');

        filterButtons.forEach(button => {
            button.addEventListener('click', function () {
                const filter = this.getAttribute('data-filter');

                productCards.forEach(card => {
                    const category = card.getAttribute('data-category');
                    card.style.display = (filter === 'all' || category === filter) ? 'block' : 'none';
                });

                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // Mobile menu functionality
    document.getElementById("hamburger")?.addEventListener("click", function() {
        document.getElementById("mobile-menu").classList.add("open");
    });

    document.getElementById("close-btn")?.addEventListener("click", function() {
        document.getElementById("mobile-menu").classList.remove("open");
    });

    // Stripe payment form functionality
    const stripeForm = document.getElementById('payment-form');
    if (stripeForm && typeof Stripe !== 'undefined') {
        var stripe = Stripe(stripe_publishable_key);
        var elements = stripe.elements();

        var card = elements.create('card');
        card.mount('#card-element');

        card.on('change', function(event) {
            var displayError = document.getElementById('error-message');
            displayError.textContent = event.error ? event.error.message : '';
        });

        stripeForm.addEventListener('submit', function(event) {
            event.preventDefault();

            stripe.confirmCardPayment(client_secret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: user_name
                    }
                }
            }).then(function(result) {
                if (result.error) {
                    // Show error to your customer
                    document.getElementById('error-message').textContent = result.error.message;
                } else if (result.paymentIntent.status === 'succeeded') {
                    // Redirect to success page
                    window.location.href = payment_success_url;
                } else {
                    // Redirect to failure page if payment fails
                    window.location.href = payment_failure_url;
                }
            });
        });
    }
});
