import React from 'react';

interface Props {
  properties: {
    radius_earth: number | null;
    mass_earth: number | null;
    density: number | null;
    equilibrium_temperature_k: number | null;
  } | null;
}

const PropertyEstimator: React.FC<Props> = ({ properties }) => {
  if (!properties) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
      <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
        <p className="text-xs text-blue-400 mb-1">Planet Radius</p>
        <p className="text-xl font-bold text-foreground">
          {properties.radius_earth ? `${properties.radius_earth} R⊕` : 'N/A'}
        </p>
      </div>
      <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
        <p className="text-xs text-emerald-400 mb-1">Planet Mass</p>
        <p className="text-xl font-bold text-foreground">
          {properties.mass_earth ? `${properties.mass_earth} M⊕` : 'N/A'}
        </p>
      </div>
      <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/20">
        <p className="text-xs text-purple-400 mb-1">Density</p>
        <p className="text-xl font-bold text-foreground">
          {properties.density ? `${properties.density} g/cm³` : 'N/A'}
        </p>
      </div>
      <div className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/20">
        <p className="text-xs text-orange-400 mb-1">Eq. Temperature</p>
        <p className="text-xl font-bold text-foreground">
          {properties.equilibrium_temperature_k ? `${properties.equilibrium_temperature_k} K` : 'N/A'}
        </p>
      </div>
    </div>
  );
};

export default PropertyEstimator;
