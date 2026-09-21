import React, { useState, useEffect, useRef } from 'react';
import { Upload, Play, Loader2, CheckCircle, AlertCircle, Sparkles } from 'lucide-react';
import PropertyEstimator from '../components/analysis/PropertyEstimator';
import HabitabilityScore from '../components/analysis/HabitabilityScore';

const DETECTION_METHODS = [
  'Transit',
  'Radial Velocity',
  'Direct Imaging',
  'Astrometry',
  'Gravitational Microlensing',
  'Orbital Phase Curve',
  'Spectroscopic Detection'
];

const Analyzer = () => {
  const [targetName, setTargetName] = useState('');
  const [method, setMethod] = useState('Transit');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  // Common Inputs
  const [stellarRadius, setStellarRadius] = useState('0.5');
  const [orbitalDistance, setOrbitalDistance] = useState('0.4');
  const [stellarTeff, setStellarTeff] = useState('3788');
  const [stellarMass, setStellarMass] = useState('0.5'); // Added for physics formulas
  
  // Transit specific
  const [transitDepth, setTransitDepth] = useState('1.5');
  const [transitDuration, setTransitDuration] = useState('2.3');
  const [transitPeriod, setTransitPeriod] = useState('129.9');
  const [ttvFlag, setTtvFlag] = useState(false);

  // Radial Velocity specific
  const [dopplerShift, setDopplerShift] = useState('1.2');

  // Direct Imaging specific
  const [angularSeparation, setAngularSeparation] = useState('50');

  // Astrometry specific
  const [astrometricWobble, setAstrometricWobble] = useState('1.5');

  // Microlensing specific
  const [crossingTime, setCrossingTime] = useState('20.5');

  // Phase Curve specific
  const [phaseVariation, setPhaseVariation] = useState('45');

  // Validation Flags
  const [anomalyCheck, setAnomalyCheck] = useState(false);
  const [multiPlanet, setMultiPlanet] = useState(false);

  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const runAnalysis = async () => {
    setIsLoading(true);
    
    // Auto-generate candidate name if empty
    let currentTarget = targetName.trim();
    if (!currentTarget) {
      currentTarget = `CANDIDATE-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;
    }

    try {
      const response = await fetch('/api/pipeline/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target: currentTarget,
          method: method,
          data: {
            stellar_radius: parseFloat(stellarRadius) || undefined,
            stellar_mass: parseFloat(stellarMass) || undefined,
            orbital_distance: parseFloat(orbitalDistance) || undefined,
            stellar_teff: parseFloat(stellarTeff) || undefined,
            transit_depth: parseFloat(transitDepth) || undefined,
            transit_duration: parseFloat(transitDuration) || undefined,
            transit_period: parseFloat(transitPeriod) || undefined,
            ttv_flag: ttvFlag,
            doppler_shift: parseFloat(dopplerShift) || undefined,
            angular_separation: parseFloat(angularSeparation) || undefined,
            astrometric_wobble: parseFloat(astrometricWobble) || undefined,
            crossing_time: parseFloat(crossingTime) || undefined,
            phase_variation: parseFloat(phaseVariation) || undefined,
            anomaly_check: anomalyCheck,
            multi_planet: multiPlanet
          }
        })
      });
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Real-time reactivity hook
  useEffect(() => {
    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    debounceTimer.current = setTimeout(() => {
      runAnalysis();
    }, 500);
    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [
    method, stellarRadius, stellarMass, orbitalDistance, stellarTeff, 
    transitDepth, transitDuration, transitPeriod, ttvFlag, 
    dopplerShift, angularSeparation, astrometricWobble, 
    crossingTime, phaseVariation, anomalyCheck, multiPlanet
  ]);

  const handleRunPipeline = (e: React.FormEvent) => {
    e.preventDefault();
    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    runAnalysis();
  };

  return (
    <div className="flex-1 p-4 md:p-8 overflow-auto">
      <div className="max-w-7xl mx-auto space-y-8">
        
        <header className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight">Advanced Analysis Pipeline</h1>
          <p className="text-muted-foreground">
            Multi-method exoplanet detection, candidate validation, and physical parameter estimation.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          <div className="lg:col-span-4 space-y-6">
            <form onSubmit={handleRunPipeline} className="bg-card border border-white/10 rounded-xl p-6 space-y-6">
              
              <div className="space-y-4 border-b border-white/10 pb-4">
                <h3 className="font-semibold text-lg flex items-center gap-2">
                  <Upload className="h-5 w-5 text-blue-500" />
                  Primary Configuration
                </h3>
                <div className="space-y-2">
                  <label className="text-xs font-medium text-muted-foreground">Target Name</label>
                  <input type="text" value={targetName} onChange={e => setTargetName(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-medium text-muted-foreground">Detection Method</label>
                  <select value={method} onChange={e => setMethod(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-card text-foreground px-3 text-sm focus:outline-none focus:border-blue-500">
                    {DETECTION_METHODS.map(m => <option key={m} value={m} className="bg-card text-foreground">{m}</option>)}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">Stellar Rad (R⊙)</label>
                    <input type="number" step="0.1" value={stellarRadius} onChange={e => setStellarRadius(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">Stellar Mass (M⊙)</label>
                    <input type="number" step="0.1" value={stellarMass} onChange={e => setStellarMass(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">Stellar Teff (K)</label>
                    <input type="number" value={stellarTeff} onChange={e => setStellarTeff(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
                  </div>
                  <div className="space-y-2">
                      <label className="text-xs font-medium text-muted-foreground">Orbital Dist (AU)</label>
                      <input type="number" step="0.01" value={orbitalDistance} onChange={e => setOrbitalDistance(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
                  </div>
                </div>
              </div>

              {/* Dynamic Inputs based on Method */}
              <div className="space-y-4 border-b border-white/10 pb-4">
                <h3 className="font-semibold text-sm text-blue-400 uppercase tracking-wider">{method} Parameters</h3>
                
                {method === 'Transit' && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-xs font-medium text-muted-foreground">Depth (ppm)</label>
                        <input type="number" step="0.1" value={transitDepth} onChange={e => setTransitDepth(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
                      </div>
                      <div className="space-y-2">
                        <label className="text-xs font-medium text-muted-foreground">Duration (hrs)</label>
                        <input type="number" step="0.1" value={transitDuration} onChange={e => setTransitDuration(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-xs font-medium text-muted-foreground">Period (days)</label>
                        <input type="number" step="0.1" value={transitPeriod} onChange={e => setTransitPeriod(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
                      </div>
                      <div className="space-y-2 flex items-end pb-2">
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input type="checkbox" checked={ttvFlag} onChange={e => setTtvFlag(e.target.checked)} className="rounded bg-white/5 border-white/10 text-blue-500 focus:ring-blue-500" />
                          <span className="text-xs font-medium text-muted-foreground">TTV Present</span>
                        </label>
                      </div>
                    </div>
                  </div>
                )}

                {method === 'Radial Velocity' && (
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">Doppler Shift Amplitude (m/s)</label>
                    <input type="number" step="0.1" value={dopplerShift} onChange={e => setDopplerShift(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
                  </div>
                )}

                {method === 'Direct Imaging' && (
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">Angular Separation (mas)</label>
                    <input type="number" step="1" value={angularSeparation} onChange={e => setAngularSeparation(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
                  </div>
                )}

                {method === 'Astrometry' && (
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">Astrometric Wobble (μas)</label>
                    <input type="number" step="0.1" value={astrometricWobble} onChange={e => setAstrometricWobble(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
                  </div>
                )}

                {method === 'Gravitational Microlensing' && (
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">Einstein Crossing Time (days)</label>
                    <input type="number" step="0.1" value={crossingTime} onChange={e => setCrossingTime(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
                  </div>
                )}
                
                {method === 'Orbital Phase Curve' && (
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">Phase Variation (ppm)</label>
                    <input type="number" step="0.1" value={phaseVariation} onChange={e => setPhaseVariation(e.target.value)} className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
                  </div>
                )}
                
                {method === 'Spectroscopic Detection' && (
                  <div className="p-3 bg-white/5 rounded-md text-xs text-muted-foreground">
                    Spectroscopic analysis utilizes automated ML pipelines to identify H2O, CH4, and CO2 signatures. No manual inputs required.
                  </div>
                )}
              </div>

              {/* Validation Controls */}
              <div className="space-y-4 pb-4">
                <h3 className="font-semibold text-sm text-emerald-400 uppercase tracking-wider">Candidate Validation</h3>
                <div className="grid grid-cols-2 gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={anomalyCheck} onChange={e => setAnomalyCheck(e.target.checked)} className="rounded bg-white/5 border-white/10 text-emerald-500 focus:ring-emerald-500" />
                    <span className="text-xs font-medium text-muted-foreground">Run Anomaly ML</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={multiPlanet} onChange={e => setMultiPlanet(e.target.checked)} className="rounded bg-white/5 border-white/10 text-emerald-500 focus:ring-emerald-500" />
                    <span className="text-xs font-medium text-muted-foreground">Multi-Planet Model</span>
                  </label>
                </div>
              </div>

              <button type="submit" disabled={isLoading} className="w-full h-10 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-medium flex items-center justify-center gap-2 transition-colors disabled:opacity-50">
                {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                {isLoading ? 'Processing Pipeline...' : 'Run Analysis'}
              </button>
            </form>
          </div>

          <div className="lg:col-span-8">
            <div className="bg-card border border-white/10 rounded-xl p-6 min-h-[600px] flex flex-col">
              <h3 className="font-semibold text-lg border-b border-white/10 pb-4">Analysis Results</h3>
              
              {!result && !isLoading && (
                <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
                  <Sparkles className="h-8 w-8 text-blue-500/50 mb-4" />
                  <p>Awaiting pipeline execution.</p>
                  <p className="text-sm">Configure detection parameters and run analysis.</p>
                </div>
              )}

              {isLoading && (
                <div className="flex-1 flex flex-col items-center justify-center text-blue-500 gap-4">
                  <Loader2 className="h-8 w-8 animate-spin" />
                  <p>Processing data streams...</p>
                </div>
              )}

              {result && !isLoading && (
                <div className="mt-6 animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-6">
                  
                  {/* Header Row */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-2xl font-bold text-foreground">{result.target}</h4>
                      <p className="text-sm text-muted-foreground">Detection: {result.method}</p>
                    </div>
                    {result.validation?.validated ? (
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                        <CheckCircle className="h-3 w-3" /> Validated Candidate
                      </span>
                    ) : (
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-red-500/20 text-red-400 border border-red-500/30 flex items-center gap-1">
                        <AlertCircle className="h-3 w-3" /> High False Positive Prob.
                      </span>
                    )}
                  </div>
                  
                  {/* Physical Properties */}
                  <div>
                    <h5 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">Physical Properties</h5>
                    <PropertyEstimator properties={result.properties} />
                  </div>

                  {/* Special Detection Outputs */}
                  {result.special_outputs && Object.keys(result.special_outputs).length > 0 && (
                     <div>
                       <h5 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">Method Specific Output</h5>
                       <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                         {Object.entries(result.special_outputs).map(([k, v]) => (
                            <div key={k} className="p-3 bg-white/5 border border-white/10 rounded-lg">
                              <p className="text-xs text-muted-foreground capitalize">{k.replace(/_/g, ' ')}</p>
                              <p className="text-sm font-medium text-foreground mt-1">{String(v)}</p>
                            </div>
                         ))}
                       </div>
                     </div>
                  )}

                  {/* Validation Metrics */}
                  {result.validation && (
                     <div>
                       <h5 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">Validation & Models</h5>
                       <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                          <div className="p-3 bg-white/5 border border-white/10 rounded-lg flex flex-col justify-between">
                            <p className="text-xs text-muted-foreground">False Positive Prob.</p>
                            <p className="text-lg font-bold text-foreground mt-1">{(result.validation.false_positive_prob * 100).toFixed(2)}%</p>
                          </div>
                          <div className="p-3 bg-white/5 border border-white/10 rounded-lg flex flex-col justify-between">
                            <p className="text-xs text-muted-foreground">ML Anomaly Score</p>
                            <p className="text-lg font-bold text-foreground mt-1">{(result.validation.anomaly_score * 100).toFixed(1)}%</p>
                          </div>
                          <div className="p-3 bg-white/5 border border-white/10 rounded-lg flex flex-col justify-between">
                            <p className="text-xs text-muted-foreground">Multi-Planet System</p>
                            <p className="text-lg font-bold text-foreground mt-1">{result.validation.multi_planet_system ? "Detected" : "Unlikely"}</p>
                          </div>
                       </div>
                     </div>
                  )}
                  
                  {/* Habitability */}
                  <HabitabilityScore habitability={result.habitability} />
                  
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Analyzer;
