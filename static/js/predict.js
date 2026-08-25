document.addEventListener("DOMContentLoaded", function() {
    // 1. Transit Photometry ML Predictor Form
    const transitForm = document.getElementById("transitPredictForm");
    if (transitForm) {
        transitForm.addEventListener("submit", async function(e) {
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
                    headers: { "Content-Type": "application/json" },
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

                        // Fetch simulation for Plotly chart
                        fetchTransitPlot(payload.pl_trandep || 0.0084, payload.pl_trandur || 3.2);
                        resultsContainer.scrollIntoView({ behavior: 'smooth' });
                    }
                } else {
                    alert("Prediction Error: " + (data.message || "Unknown error occurred"));
                }
            } catch (err) {
                console.error("Failed to submit prediction request:", err);
            }
        });
    }

    // Helper to trigger transit light curve plot
    async function fetchTransitPlot(depth, duration) {
        try {
            const chartElem = document.getElementById("plotlyTransitChart");
            if (!chartElem) return;

            const timePts = Array.from({length: 30}, (_, i) => i * 0.5);
            const fluxArr = timePts.map(t => (t > 4 && t < 10) ? (1.0 - depth) : 1.0);

            const res = await fetch("/api/simulate/transit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ light_curve: fluxArr })
            });
            const data = await res.json();
            if (data.status === "Success") {
                chartElem.style.display = "block";
                renderTransitChart("plotlyTransitChart", data.time_points, data.flux_values);
            }
        } catch (e) {
            console.error("Failed to fetch transit plot:", e);
        }
    }
});

// Global Trigger Functions for methods
async function calculateRadialVelocity() {
    const v1 = parseFloat(document.getElementById("rv_input1")?.value || 10.0);
    const v2 = parseFloat(document.getElementById("rv_input2")?.value || 5.0);
    const v3 = parseFloat(document.getElementById("rv_input3")?.value || -8.0);
    const v4 = parseFloat(document.getElementById("rv_input4")?.value || -12.0);

    const signals = [v1, v2, v3, v4, -4.0, 7.0, 11.0];

    try {
        const res = await fetch("/api/simulate/radial_velocity", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ signals })
        });
        const data = await res.json();
        if (data.status === "Success") {
            const chartElem = document.getElementById("plotlyRVChart");
            if (chartElem) {
                chartElem.style.display = "block";
                renderRVChart("plotlyRVChart", data.raw_time, data.raw_velocity, data.fit_time, data.fit_velocity);
            }
            const outElem = document.getElementById("rv_output");
            if (outElem) {
                outElem.innerHTML = `<strong>Amplitude:</strong> ${data.estimated_parameters.amplitude_ms} m/s | <strong>Orbital Period:</strong> ${data.estimated_parameters.orbital_period_days} days | <strong>Status:</strong> ${data.is_confirmed ? 'CONFIRMED RV SIGNAL' : 'NO CONFIRMED SIGNAL'}`;
            }
        }
    } catch (e) {
        console.error("RV calculation failed:", e);
    }
}

async function calculateDirectImaging() {
    const s1 = parseFloat(document.getElementById("di_input1")?.value || 1.0);
    const s2 = parseFloat(document.getElementById("di_input2")?.value || 1.05);
    const s3 = parseFloat(document.getElementById("di_input3")?.value || 1.85);
    const s4 = parseFloat(document.getElementById("di_input4")?.value || 1.1);

    const intensities = [s1, s2, s3, s4, 0.95, 0.98];

    try {
        const res = await fetch("/api/simulate/direct_imaging", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ intensities })
        });
        const data = await res.json();
        if (data.status === "Success") {
            const chartElem = document.getElementById("plotlyDirectChart");
            if (chartElem) {
                chartElem.style.display = "block";
                renderDirectImagingChart("plotlyDirectChart", data.pixel_indices, data.intensity_values);
            }
            const outElem = document.getElementById("di_output");
            if (outElem) {
                outElem.innerHTML = `<strong>Peak Intensity:</strong> ${data.metrics.peak_intensity} | <strong>SNR:</strong> ${data.metrics.signal_to_noise_ratio} | <strong>Companion Status:</strong> ${data.is_confirmed ? 'DIRECT EXOPLANET IMAGE CONFIRMED' : 'NO COMPANION DETECTED'}`;
            }
        }
    } catch (e) {
        console.error("Direct Imaging calculation failed:", e);
    }
}

async function calculateBiosignature() {
    const o2 = parseFloat(document.getElementById("bio_o2")?.value || 0.21);
    const h2o = parseFloat(document.getElementById("bio_h2o")?.value || 0.02);
    const n2 = parseFloat(document.getElementById("bio_n2")?.value || 0.75);
    const co2 = parseFloat(document.getElementById("bio_co2")?.value || 0.01);

    const composition = { Oxygen: o2, Water: h2o, Nitrogen: n2, CarbonDioxide: co2 };

    try {
        const res = await fetch("/api/simulate/biosignature", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ composition })
        });
        const data = await res.json();
        if (data.status === "Success") {
            const chartElem = document.getElementById("plotlyBioChart");
            if (chartElem) {
                chartElem.style.display = "block";
                renderBiosignatureChart("plotlyBioChart", data.chemical_breakdown);
            }
            const outElem = document.getElementById("bio_output");
            if (outElem) {
                outElem.innerHTML = `<strong>Biosignature Habitability Score:</strong> ${data.biosignature_score} / 1.00 | <strong>Condition:</strong> ${data.is_habitable ? 'FAVORABLE FOR LIFE' : 'NEEDS FURTHER ANALYSIS'}`;
            }
        }
    } catch (e) {
        console.error("Biosignature calculation failed:", e);
    }
}
