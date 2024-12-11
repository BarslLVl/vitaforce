/* Calculator */
function calculateCalories() {
    const weight = parseFloat(document.getElementById('weight').value);
    const height = parseFloat(document.getElementById('height').value);
    const age = parseInt(document.getElementById('age').value);
    const gender = document.getElementById('gender').value;
    const activity = document.getElementById('activity').value;

    if (isNaN(weight) || isNaN(height) || isNaN(age)) {
        document.getElementById('calorie-result').innerText = "Please fill in all fields correctly.";
        return;
    }

    let bmr;
    if (gender === "male") {
        bmr = 10 * weight + 6.25 * height - 5 * age + 5;
    } else {
        bmr = 10 * weight + 6.25 * height - 5 * age - 161;
    }

    let calories;
    switch (activity) {
        case "sedentary":
            calories = bmr * 1.2;
            break;
        case "lightly_active":
            calories = bmr * 1.375;
            break;
        case "moderately_active":
            calories = bmr * 1.55;
            break;
        case "very_active":
            calories = bmr * 1.725;
            break;
        default:
            calories = bmr;
    }

    document.getElementById('calorie-result').innerText = `Your daily calorie requirement is approximately ${calories.toFixed(0)} kcal.`;
}

/* Shop - Show | Hide description*/
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.toggle-text').forEach(button => {
        button.addEventListener('click', function () {
            const fullText = this.previousElementSibling;
            const shortText = fullText.previousElementSibling;
            
            if (fullText.classList.contains('d-none')) {

                fullText.classList.remove('d-none');
                shortText.classList.add('d-none');
                this.textContent = 'Hide';
            } else {
                fullText.classList.add('d-none');
                shortText.classList.remove('d-none');
                this.textContent = 'Show';
            }
        });
    });
});

/* Stripe | Payment */
document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("payment-form");
    const stripeCheckoutUrl = form.getAttribute("data-url");
    const stripe = Stripe("{{ stripe_public_key }}");
    const elements = stripe.elements();
    const card = elements.create("card");
    card.mount("#card-element");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const fullName = document.getElementById("full-name").value;
        const email = document.getElementById("email").value;
        const address = document.getElementById("address").value;
        const city = document.getElementById("city").value;
        const zip = document.getElementById("zip").value;

        if (!fullName || !email || !address || !city || !zip) {
            document.getElementById("error-message").textContent = "Please fill all billing details.";
            return;
        }

        // Фиктивная обработка
        try {
            const response = await fetch(stripeCheckoutUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                    total_price: "{{ total_price }}",
                    full_name: fullName,
                    email: email,
                    address: address,
                    city: city,
                    zip: zip,
                }),
            });

            const result = await response.json();

            if (result.error) {
                console.warn("Ошибка на стороне сервера:", result.error);
            }

            const clientSecret = result.client_secret || "mock_client_secret";

            const { paymentIntent, error: stripeError } = await stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: fullName,
                        email: email,
                        address: {
                            line1: address,
                            city: city,
                            postal_code: zip,
                        },
                    },
                },
            });

            if (stripeError) {
                console.warn("Ошибка Stripe:", stripeError.message);
            }

            if (paymentIntent && paymentIntent.status === "succeeded") {
                window.location.href = "{% url 'payment_success' %}";
            } else {
                console.warn("Фиктивный успех оплаты");
                window.location.href = "{% url 'payment_success' %}";
            }
        } catch (error) {
            console.warn("Фиктивная оплата при ошибке:", error.message);
            window.location.href = "{% url 'payment_success' %}";
        }
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


/* TinyMCE settings*/
document.addEventListener("DOMContentLoaded", function () {
    tinymce.init({
        selector: 'textarea',
        height: 360,
        menubar: true,
        plugins: [
            'advlist autolink lists link image charmap print preview anchor',
            'searchreplace visualblocks code fullscreen',
            'insertdatetime media table paste code help wordcount'
        ],
        toolbar: 'undo redo | formatselect | bold italic backcolor | alignleft aligncenter ' +
                'alignright alignjustify | bullist numlist outdent indent | removeformat | help',
        content_style: 'body { font-family:Arial,sans-serif; font-size:14px }'
    });
});

