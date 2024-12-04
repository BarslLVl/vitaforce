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
