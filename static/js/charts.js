/**
 * COSMOS Plotly Visualization Engine
 * Renders Photometric Light Curves, Keplerian RV Orbit Fits, Residuals, Transmission Spectra, & SNR Bars.
 */

function renderTransitChart(containerId, phase, flux, fittedFlux = null, residuals = null) {
    if (!window.Plotly) return;

    const traceData = {
        x: phase,
        y: flux,
        mode: 'markers',
        type: 'scatter',
        marker: { color: '#38bdf8', size: 4, opacity: 0.7 },
        name: 'Phase-Folded Flux'
    };

    const traces = [traceData];

    if (fittedFlux) {
        traces.push({
            x: phase,
            y: fittedFlux,
            mode: 'lines',
            type: 'scatter',
            line: { color: '#00ffb3', width: 2.5 },
            name: 'Box Transit Model Fit'
        });
    }

    const layout = {
        title: { text: 'Phase-Folded Photometric Transit & Transit Fit Model', font: { color: '#00ffb3', size: 16 } },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(255,255,255,0.03)',
        xaxis: { title: 'Orbital Phase (-0.5 to +0.5)', gridcolor: '#1e293b', color: '#94a3b8' },
        yaxis: { title: 'Normalized Relative Flux', gridcolor: '#1e293b', color: '#94a3b8' },
        margin: { t: 40, b: 40, l: 50, r: 20 },
        legend: { font: { color: '#fff' } }
    };

    Plotly.newPlot(containerId, traces, layout, { responsive: true });
}

function renderRVChart(containerId, rawTime, rawVel, fitTime, fitVel) {
    if (!window.Plotly) return;

    const traceScatter = {
        x: rawTime,
        y: rawVel,
        mode: 'markers',
        type: 'scatter',
        marker: { color: '#ffb700', size: 8 },
        name: 'Observed RV Data'
    };

    const traceFit = {
        x: fitTime,
        y: fitVel,
        mode: 'lines',
        type: 'scatter',
        line: { color: '#00ffb3', width: 2.5 },
        name: '6-Parameter Keplerian Fit'
    };

    const layout = {
        title: { text: 'Keplerian Radial Velocity Orbital Curve (m/s)', font: { color: '#ffb700', size: 16 } },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(255,255,255,0.03)',
        xaxis: { title: 'Time / Epoch (Days)', gridcolor: '#1e293b', color: '#94a3b8' },
        yaxis: { title: 'Radial Velocity (m/s)', gridcolor: '#1e293b', color: '#94a3b8' },
        margin: { t: 40, b: 40, l: 50, r: 20 },
        legend: { font: { color: '#fff' } }
    };

    Plotly.newPlot(containerId, [traceScatter, traceFit], layout, { responsive: true });
}

function renderSpectroscopyChart(containerId, wavelengths, modelSpectrum, measuredSpectrum) {
    if (!window.Plotly) return;

    const traceMeasured = {
        x: wavelengths,
        y: measuredSpectrum,
        mode: 'markers',
        type: 'scatter',
        marker: { color: '#ffb700', size: 5, opacity: 0.7 },
        name: 'JWST Synthetic Observation'
    };

    const traceModel = {
        x: wavelengths,
        y: modelSpectrum,
        mode: 'lines',
        type: 'scatter',
        line: { color: '#00ffb3', width: 2.5 },
        name: 'Atmospheric Opacity Model'
    };

    const layout = {
        title: { text: 'Transmission Opacity Spectrum (0.6 - 12.0 µm)', font: { color: '#00ffb3', size: 16 } },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(255,255,255,0.03)',
        xaxis: { title: 'Wavelength (Microns µm)', gridcolor: '#1e293b', color: '#94a3b8' },
        yaxis: { title: 'Transit Depth (ppm)', gridcolor: '#1e293b', color: '#94a3b8' },
        margin: { t: 40, b: 40, l: 50, r: 20 },
        legend: { font: { color: '#fff' } }
    };

    Plotly.newPlot(containerId, [traceMeasured, traceModel], layout, { responsive: true });
}
