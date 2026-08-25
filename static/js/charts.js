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
                
                const formElem = document.getElementById("transitPredictForm");
                if (formElem) {
                    formElem.style.boxShadow = "0 0 20px #00f2fe";
                    setTimeout(() => formElem.style.boxShadow = "none", 1500);
                }
            }
        })
        .catch(err => console.error("Failed to load target preset:", err));
}

function renderTransitChart(containerId, timePoints, fluxValues) {
    if (!window.Plotly) return;

    const trace = {
        x: timePoints,
        y: fluxValues,
        mode: 'lines+markers',
        type: 'scatter',
        marker: { color: '#00f2fe', size: 6 },
        line: { color: '#4facfe', width: 2 },
        name: 'Normalized Relative Flux'
    };

    const layout = {
        title: { text: 'Transit Light Curve Photometry', font: { color: '#00f2fe', size: 16 } },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(255,255,255,0.03)',
        xaxis: { title: 'Time / Phase (Hours)', gridcolor: '#222', color: '#fff' },
        yaxis: { title: 'Relative Stellar Flux', gridcolor: '#222', color: '#fff' },
        margin: { t: 40, b: 40, l: 50, r: 20 }
    };

    Plotly.newPlot(containerId, [trace], layout, { responsive: true });
}

function renderRVChart(containerId, rawTime, rawVel, fitTime, fitVel) {
    if (!window.Plotly) return;

    const traceScatter = {
        x: rawTime,
        y: rawVel,
        mode: 'markers',
        type: 'scatter',
        marker: { color: '#ffb700', size: 8 },
        name: 'Observed Radial Velocity'
    };

    const traceFit = {
        x: fitTime,
        y: fitVel,
        mode: 'lines',
        type: 'scatter',
        line: { color: '#00ffb3', width: 2 },
        name: 'Keplerian Fitted Curve'
    };

    const layout = {
        title: { text: 'Radial Velocity Orbital Variation (m/s)', font: { color: '#ffb700', size: 16 } },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(255,255,255,0.03)',
        xaxis: { title: 'Observation Epoch (Days)', gridcolor: '#222', color: '#fff' },
        yaxis: { title: 'Radial Velocity (m/s)', gridcolor: '#222', color: '#fff' },
        margin: { t: 40, b: 40, l: 50, r: 20 }
    };

    Plotly.newPlot(containerId, [traceScatter, traceFit], layout, { responsive: true });
}

function renderDirectImagingChart(containerId, pixels, intensities) {
    if (!window.Plotly) return;

    const trace = {
        x: pixels,
        y: intensities,
        type: 'bar',
        marker: {
            color: intensities.map(v => v > 1.2 ? '#00ffb3' : '#7928ca')
        },
        name: 'Spatial Signal Intensity'
    };

    const layout = {
        title: { text: 'Direct Imaging Spatial Coronagraph Signal Peak', font: { color: '#00ffb3', size: 16 } },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(255,255,255,0.03)',
        xaxis: { title: 'Spatial Pixel Index', gridcolor: '#222', color: '#fff' },
        yaxis: { title: 'Normalized Signal Intensity', gridcolor: '#222', color: '#fff' },
        margin: { t: 40, b: 40, l: 50, r: 20 }
    };

    Plotly.newPlot(containerId, [trace], layout, { responsive: true });
}

function renderBiosignatureChart(containerId, breakdown) {
    if (!window.Plotly) return;

    const gases = Object.keys(breakdown);
    const observed = gases.map(g => breakdown[g].observed_fraction * 100);
    const earth = gases.map(g => breakdown[g].earth_baseline * 100);

    const traceObserved = {
        x: gases,
        y: observed,
        name: 'Candidate Exoplanet (%)',
        type: 'bar',
        marker: { color: '#00f2fe' }
    };

    const traceEarth = {
        x: gases,
        y: earth,
        name: 'Earth Baseline (%)',
        type: 'bar',
        marker: { color: '#ff4757' }
    };

    const layout = {
        title: { text: 'Atmospheric Biosignature Gas Breakdown vs Earth Baseline', font: { color: '#00f2fe', size: 16 } },
        barmode: 'group',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(255,255,255,0.03)',
        xaxis: { title: 'Atmospheric Gas Species', gridcolor: '#222', color: '#fff' },
        yaxis: { title: 'Volume Concentration (%)', type: 'log', gridcolor: '#222', color: '#fff' },
        margin: { t: 40, b: 40, l: 50, r: 20 }
    };

    Plotly.newPlot(containerId, [traceObserved, traceEarth], layout, { responsive: true });
}
