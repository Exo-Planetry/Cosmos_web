function loadPresetTarget(presetKey) {
    fetch(`/api/nasa/preset/${presetKey}`)
        .then(response => response.json())
        .then(res => {
            if (res.status === 'Success' && res.data) {
                const data = res.data;
                for (const key in data) {
                    const inputElem = document.getElementById(key);
                    if (inputElem) {
                        inputElem.value = data[key];
                    }
                }
                
                // Highlight form
                const formElem = document.getElementById("transitPredictForm");
                if (formElem) {
                    formElem.style.boxShadow = "0 0 15px #00f2fe";
                    setTimeout(() => formElem.style.boxShadow = "none", 1500);
                }
            }
        })
        .catch(err => console.error("Failed to load target preset:", err));
}

function renderLightCurveChart(containerId, timePoints, fluxValues) {
    if (!window.Plotly) return;

    const trace = {
        x: timePoints,
        y: fluxValues,
        mode: 'lines+markers',
        type: 'scatter',
        marker: { color: '#00f2fe', size: 6 },
        line: { color: '#4facfe', width: 2 },
        name: 'Normalized Flux'
    };

    const layout = {
        title: { text: 'Transit Light Curve Photometry', font: { color: '#ffffff' } },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        xaxis: { title: 'Phase / Time (Hours)', gridcolor: '#333', color: '#fff' },
        yaxis: { title: 'Relative Flux', gridcolor: '#333', color: '#fff' },
        margin: { t: 40, b: 40, l: 50, r: 20 }
    };

    Plotly.newPlot(containerId, [trace], layout, { responsive: true });
}
