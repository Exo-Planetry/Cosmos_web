/**
 * COSMOS Production JS Orchestrator
 * Handles Target Search, FITS/CSV File Upload, Unified API Calls, Plotly Charts, SHAP Bars, & Evidence Fusion.
 */

async function executeTargetAnalysis(targetName = null) {
    const query = targetName || document.getElementById("targetSearchInput")?.value || "TOI-700 d";
    
    try {
        const response = await fetch("/api/analysis", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ target_name: query })
        });

        const data = await response.json();

        if (data.status === "Success") {
            renderAnalysisDashboard(data);
        } else if (data.status === "DATA_UNAVAILABLE") {
            alert(`DATA_UNAVAILABLE: ${data.message}\n\n${data.suggestion}`);
        } else {
            alert("Analysis Request Error: " + (data.message || "Failed to retrieve analysis."));
        }
    } catch (err) {
        console.error("Failed to execute target analysis:", err);
    }
}

function renderAnalysisDashboard(data) {
    const target = data.target_id;
    const assessment = data.candidate_assessment || {};
    const ml = data.ml_prediction || {};
    const fp = ml.false_positive_analysis || {};
    const prov = data.data_provenance || {};
    const params = data.parameters || {};

    // 1. Update Header Banner
    document.getElementById("bannerTargetName").textContent = target;
    document.getElementById("bannerProvenance").textContent = prov.data_source || "NASA Exoplanet Archive";
    document.getElementById("bannerTierLabel").textContent = assessment.candidate_tier_label || "STRONG CANDIDATE";
    document.getElementById("bannerTierLabel").style.color = assessment.tier_color || "#00ffb3";
    document.getElementById("bannerScoreNum").textContent = assessment.candidate_assessment_score || 85;
    document.getElementById("bannerFPRisk").textContent = `${fp.false_positive_risk_pct || 12.0}%`;
    document.getElementById("bannerFPRisk").style.color = fp.false_positive_risk_pct < 30 ? "#00ffb3" : "#ff4757";

    // 2. Update Provenance Card
    document.getElementById("provSource").textContent = prov.data_source || "NASA TAP Archive";
    document.getElementById("provStatus").textContent = prov.data_status || "Observed + Derived";
    document.getElementById("provPipeline").textContent = prov.pipeline_version || "COSMOS v2.0.0";
    document.getElementById("provTime").textContent = prov.analysis_timestamp || "2026-09-06 UTC";

    // 3. Update Evidence Breakdown Grid
    const breakdown = assessment.evidence_breakdown || {};
    let gridHtml = "";
    for (const key in breakdown) {
        const title = key.replace(/_/g, ' ').toUpperCase();
        gridHtml += `
        <div class="col-md-6 mb-3">
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); padding: 14px; border-radius: 10px;">
                <div style="font-size: 0.75em; color: var(--text-muted); font-weight: 700;">${title}</div>
                <div style="font-size: 1.2em; font-weight: 700; color: var(--accent-green); margin-top: 4px;">${breakdown[key]}</div>
            </div>
        </div>
        `;
    }
    document.getElementById("evidenceBreakdownGrid").innerHTML = gridHtml;

    // 4. Render Light Curve Plotly Chart
    const lc = data.photometric_transit_analysis || {};
    if (lc.phase_folded_light_curve && window.renderTransitChart) {
        const pf = lc.phase_folded_light_curve;
        renderTransitChart("plotlyLightCurveChart", pf.phase, pf.flux, pf.fitted_model_flux, pf.residuals);
    }

    // 5. Render Keplerian RV Chart
    const rv = data.keplerian_rv_analysis || {};
    if (rv.raw_time && window.renderRVChart) {
        renderRVChart("plotlyRVChart", rv.raw_time, rv.raw_velocity, rv.fit_time, rv.fit_velocity);
    }

    // 6. Render Biosignature & Spectroscopy Chart
    const spec = data.transmission_spectroscopy || {};
    if (spec.wavelengths_microns && window.renderSpectroscopyChart) {
        renderSpectroscopyChart("plotlySpectroscopyChart", spec.wavelengths_microns, spec.model_spectrum_ppm, spec.measured_spectrum_ppm);
    }

    const bio = data.atmospheric_assessment || {};
    document.getElementById("bioAssessmentOutput").innerHTML = `
        <div style="font-size: 1.3em; font-weight: 700; color: var(--accent-green);">${bio.assessment_label || 'Potential Biosignature Evidence'}</div>
        <p style="margin-top: 8px;">Disequilibrium Index: <strong>${bio.chemical_disequilibrium_index} / 1.00</strong> | Confidence: <strong>${bio.biosignature_confidence_pct}%</strong></p>
        <div style="margin-top: 12px;"><strong>Indicators:</strong> ${bio.detected_indicators ? bio.detected_indicators.join(', ') : 'Standard Equilibrium'}</div>
        <div style="margin-top: 8px; color: var(--accent-warning);"><strong>False Positive Risk Flags:</strong> ${bio.false_positive_concerns ? bio.false_positive_concerns.join(', ') : 'None'}</div>
    `;

    // 7. Render Habitable Zone & ESI
    const hz = data.habitable_zone_position || {};
    const esi = hz.multidimensional_esi || {};
    document.getElementById("hzPositionOutput").innerHTML = `
        <div style="font-size: 1.2em; font-weight: 700; color: ${hz.zone_color || '#00ffb3'};">${hz.zone_position || 'Conservative Habitable Zone'}</div>
        <p style="margin-top: 8px; color: var(--text-muted); font-size: 0.9em;">${hz.explanation || ''}</p>
        <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px; font-size: 0.85em; color: var(--text-muted);">${hz.scientific_disclaimer}</div>
    `;

    let esiHtml = `<div style="font-size: 1.6em; font-weight: 800; color: var(--accent-green); mb-3">Composite ESI: ${esi.composite_esi || 0.85} / 1.000</div>`;
    const comps = esi.components || {};
    for (const cKey in comps) {
        const pct = comps[cKey] * 100;
        esiHtml += `
        <div class="mb-2">
            <div class="d-flex justify-content-between font-size-xs text-muted mb-1">
                <span>${cKey.replace('_similarity', '').toUpperCase()}</span>
                <span>${comps[cKey]}</span>
            </div>
            <div style="background: rgba(255,255,255,0.08); height: 8px; border-radius: 4px; overflow: hidden;">
                <div style="background: var(--accent-green); width: ${pct}%; height: 100%;"></div>
            </div>
        </div>
        `;
    }
    document.getElementById("esiBreakdownOutput").innerHTML = esiHtml;

    // 8. Render Tree SHAP Attributions List
    const shapList = ml.xai_attributions || [];
    let shapHtml = "";
    shapList.forEach(item => {
        const color = item.direction === 'positive' ? 'var(--accent-green)' : 'var(--accent-red)';
        shapHtml += `
        <div style="background: rgba(255,255,255,0.03); border-left: 4px solid ${color}; padding: 14px; border-radius: 6px; margin-bottom: 12px;">
            <div class="d-flex justify-content-between align-items-center">
                <strong style="color: #fff;">${item.feature}</strong>
                <span style="font-weight: 700; color: ${color};">${item.impact} (SHAP: ${item.shap_score})</span>
            </div>
            <p style="margin: 6px 0 0 0; color: var(--text-muted); font-size: 0.85em;">${item.explanation}</p>
        </div>
        `;
    });
    document.getElementById("shapAttributionsList").innerHTML = shapHtml;

    // 9. Render Observations Table
    let obsHtml = "";
    for (const pKey in params) {
        obsHtml += `<tr><th>${pKey}</th><td>${params[pKey]}</td></tr>`;
    }
    document.getElementById("observationsTable").innerHTML = obsHtml;

    // 10. Init 3D Orbit Visualization if function present
    if (window.init3dOrbit) {
        init3dOrbit("canvas3dContainer", params.pl_orbper || 365.25, params.pl_orbeccen || 0.0167);
    }
}

async function handleFileUpload(inputElem) {
    if (!inputElem.files || inputElem.files.length === 0) return;
    const file = inputElem.files[0];

    const formData = new FormData();
    formData.append("file", file);
    formData.append("target_name", file.name.replace('.csv', '').replace('.fits', ''));

    try {
        const res = await fetch("/api/analysis", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        if (data.status === "Success") {
            var myModalEl = document.getElementById('uploadModal');
            var modal = bootstrap.Modal.getInstance(myModalEl);
            if (modal) modal.hide();

            renderAnalysisDashboard(data);
            alert(`File '${file.name}' processed successfully!`);
        } else {
            alert("File upload analysis error: " + (data.message || "Failed to process file."));
        }
    } catch (e) {
        console.error("Upload error:", e);
    }
}
