document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("transitPredictForm");
    if (!form) return;

    form.addEventListener("submit", async function(e) {
        // Prevent default page reload to allow AJAX prediction
        e.preventDefault();

        const formData = new FormData(this);
        const payload = {};
        formData.forEach((val, key) => {
            payload[key] = parseFloat(val) || val;
        });

        const resultsContainer = document.getElementById("ajaxPredictionResults");
        const labelElem = document.getElementById("ajaxLabel");
        const confidenceElem = document.getElementById("ajaxConfidence");
        const esiElem = document.getElementById("ajaxESI");

        try {
            const response = await fetch("/api/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.status === "Success") {
                if (resultsContainer) {
                    resultsContainer.style.display = "block";
                    resultsContainer.style.borderLeft = `5px solid ${data.label_color}`;
                    
                    labelElem.textContent = data.classification_label;
                    labelElem.style.color = data.label_color;
                    
                    confidenceElem.textContent = data.confidence_score;
                    esiElem.textContent = data.earth_similarity_index;

                    // Smooth scroll to result
                    resultsContainer.scrollIntoView({ behavior: 'smooth' });
                }
            } else {
                alert("Prediction Error: " + (data.message || "Unknown error occurred"));
            }
        } catch (err) {
            console.error("Failed to submit prediction request:", err);
        }
    });
});
