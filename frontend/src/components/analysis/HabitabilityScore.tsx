import React from 'react';
import { Activity, ShieldCheck, ShieldAlert, Droplets, Thermometer, Wind } from 'lucide-react';

interface Props {
  habitability: {
    status: string;
    score: number;
    stellar_flux_earth?: number | null;
    in_conservative_hz?: boolean;
    in_optimistic_hz?: boolean;
    is_tidally_locked?: boolean;
    retains_water_atmosphere?: boolean;
    surface_liquid_water_potential?: boolean;
  } | null;
}

const HabitabilityScore: React.FC<Props> = ({ habitability }) => {
  if (!habitability) return null;

  const isHabitable = habitability.status.includes('Habitable');
  const colorClass = isHabitable ? 'text-emerald-500' : 'text-orange-500';
  const bgClass = isHabitable ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-orange-500/10 border-orange-500/20';

  return (
    <div className="mt-6 space-y-4">
      <div className={`p-6 rounded-xl border flex flex-col md:flex-row items-center gap-6 ${bgClass}`}>
        <div className={`p-4 rounded-full bg-background/50 ${colorClass}`}>
          <Activity className="h-8 w-8" />
        </div>
        <div className="flex-1 text-center md:text-left">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-1">Physical Habitability Assessment</h3>
          <p className={`text-2xl font-bold ${colorClass}`}>{habitability.status}</p>
          <p className="text-sm mt-2 text-foreground/80">
            Composite Probability Score: <strong>{(habitability.score * 100).toFixed(1)}%</strong>
          </p>
        </div>
        <div className="w-full md:w-48 h-2 bg-black/40 rounded-full overflow-hidden">
           <div 
             className={`h-full ${isHabitable ? 'bg-emerald-500' : 'bg-orange-500'}`}
             style={{ width: `${habitability.score * 100}%` }}
           />
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {habitability.stellar_flux_earth !== undefined && (
          <div className="p-4 bg-white/5 border border-white/10 rounded-lg flex items-start gap-3">
            <Thermometer className="h-5 w-5 text-blue-400 mt-0.5" />
            <div>
              <p className="text-xs text-muted-foreground uppercase">Stellar Flux</p>
              <p className="text-sm font-medium mt-1">{habitability.stellar_flux_earth ? `${habitability.stellar_flux_earth.toFixed(2)} S⊕` : 'N/A'}</p>
            </div>
          </div>
        )}
        
        <div className="p-4 bg-white/5 border border-white/10 rounded-lg flex items-start gap-3">
          {habitability.in_optimistic_hz ? <ShieldCheck className="h-5 w-5 text-emerald-400 mt-0.5" /> : <ShieldAlert className="h-5 w-5 text-red-400 mt-0.5" />}
          <div>
            <p className="text-xs text-muted-foreground uppercase">Habitable Zone</p>
            <p className="text-sm font-medium mt-1">
              {habitability.in_conservative_hz ? 'Conservative HZ' : habitability.in_optimistic_hz ? 'Optimistic HZ' : 'Outside HZ Boundaries'}
            </p>
          </div>
        </div>

        <div className="p-4 bg-white/5 border border-white/10 rounded-lg flex items-start gap-3">
          <Wind className="h-5 w-5 text-purple-400 mt-0.5" />
          <div>
            <p className="text-xs text-muted-foreground uppercase">Atmos. Retention</p>
            <p className="text-sm font-medium mt-1">
              {habitability.retains_water_atmosphere ? 'Retains Volatiles (Jeans)' : 'Subject to escape'}
            </p>
          </div>
        </div>

        <div className="p-4 bg-white/5 border border-white/10 rounded-lg flex items-start gap-3">
          <Droplets className="h-5 w-5 text-blue-500 mt-0.5" />
          <div>
            <p className="text-xs text-muted-foreground uppercase">Surface Conditions</p>
            <p className="text-sm font-medium mt-1">
              {habitability.is_tidally_locked ? 'Tidally Locked' : habitability.surface_liquid_water_potential ? 'Liquid Water Possible' : 'Unfavorable'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HabitabilityScore;
