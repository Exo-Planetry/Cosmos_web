import { useState } from 'react';
import { Search, Globe2, Moon, Sparkles, X, Orbit } from 'lucide-react';

const SOLAR_SYSTEM = [
  { name: 'Mercury', type: 'Terrestrial', mass: 0.055, radius: 0.383, dist: 0.39, moons: 0, desc: 'Smallest and innermost planet.', moonDetails: '', temp: '430°C (Day)', atmosphere: 'Virtually None', gravity: '3.7 m/s²' },
  { name: 'Venus', type: 'Terrestrial', mass: 0.815, radius: 0.95, dist: 0.72, moons: 0, desc: 'Thick, toxic atmosphere.', moonDetails: '', temp: '471°C', atmosphere: 'Carbon Dioxide, Nitrogen', gravity: '8.87 m/s²' },
  { name: 'Earth', type: 'Terrestrial', mass: 1.0, radius: 1.0, dist: 1.0, moons: 1, desc: 'Our home planet, supports life.', moonDetails: 'Moon (Luna)', temp: '15°C', atmosphere: 'Nitrogen, Oxygen', gravity: '9.8 m/s²' },
  { name: 'Mars', type: 'Terrestrial', mass: 0.107, radius: 0.532, dist: 1.52, moons: 2, desc: 'The Red Planet.', moonDetails: 'Phobos, Deimos', temp: '-65°C', atmosphere: 'Carbon Dioxide', gravity: '3.71 m/s²' },
  { name: 'Jupiter', type: 'Gas Giant', mass: 317.8, radius: 11.21, dist: 5.20, moons: 95, desc: 'Largest planet in the solar system.', moonDetails: 'Io, Europa, Ganymede, Callisto...', temp: '-110°C', atmosphere: 'Hydrogen, Helium', gravity: '24.79 m/s²' },
  { name: 'Saturn', type: 'Gas Giant', mass: 95.2, radius: 9.45, dist: 9.58, moons: 146, desc: 'Famous for its prominent ring system.', moonDetails: 'Titan, Enceladus, Mimas...', temp: '-140°C', atmosphere: 'Hydrogen, Helium', gravity: '10.44 m/s²' },
  { name: 'Uranus', type: 'Ice Giant', mass: 14.5, radius: 4.01, dist: 19.2, moons: 28, desc: 'Rotates on its side.', moonDetails: 'Titania, Oberon, Umbriel...', temp: '-195°C', atmosphere: 'Hydrogen, Helium, Methane', gravity: '8.69 m/s²' },
  { name: 'Neptune', type: 'Ice Giant', mass: 17.1, radius: 3.88, dist: 30.0, moons: 16, desc: 'Dark, cold, and whipped by supersonic winds.', moonDetails: 'Triton, Proteus...', temp: '-200°C', atmosphere: 'Hydrogen, Helium, Methane', gravity: '11.15 m/s²' },
  { name: 'Pluto', type: 'Dwarf Planet', mass: 0.00218, radius: 0.186, dist: 39.48, moons: 5, desc: 'Famous dwarf planet in the Kuiper Belt.', moonDetails: 'Charon, Nix, Hydra...', temp: '-225°C', atmosphere: 'Nitrogen, Methane', gravity: '0.62 m/s²' }
];

const SolarSystem = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPlanet, setSelectedPlanet] = useState<typeof SOLAR_SYSTEM[0] | null>(null);

  const filteredPlanets = SOLAR_SYSTEM.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex-1 p-4 md:p-8 overflow-auto">
      <div className="max-w-7xl mx-auto space-y-6">
        
        <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Solar System</h1>
            <p className="text-muted-foreground mt-1">Explore our local planetary neighborhood.</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative flex-1 md:w-64">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                type="search"
                placeholder="Search planets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-8 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all"
              />
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPlanets.map((planet) => (
            <div key={planet.name} className="rounded-xl border border-white/10 bg-card p-6 shadow-sm hover:border-white/20 transition-all duration-300">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`p-2.5 rounded-lg ${planet.type === 'Gas Giant' ? 'bg-orange-500/10 text-orange-400' : planet.type === 'Ice Giant' ? 'bg-blue-500/10 text-blue-400' : 'bg-stone-500/10 text-stone-400'}`}>
                    <Globe2 className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-xl text-foreground">{planet.name}</h3>
                    <p className="text-xs text-muted-foreground">{planet.type}</p>
                  </div>
                </div>
              </div>
              
              <p className="text-sm text-foreground/80 mb-6 h-10">{planet.desc}</p>
              
              <div className="grid grid-cols-3 gap-4 border-t border-white/5 pt-4 mb-4">
                <div>
                  <p className="text-xs text-muted-foreground">Mass (M⊕)</p>
                  <p className="font-medium text-sm text-foreground mt-1">{planet.mass}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Radius (R⊕)</p>
                  <p className="font-medium text-sm text-foreground mt-1">{planet.radius}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Distance (AU)</p>
                  <p className="font-medium text-sm text-foreground mt-1">{planet.dist}</p>
                </div>
              </div>

              {planet.moons > 0 && (
                <div className="mt-4 p-3 bg-white/5 rounded-lg border border-white/10">
                  <div className="flex items-center gap-2 mb-1">
                    <Moon className="h-4 w-4 text-purple-400" />
                    <span className="text-xs font-semibold">{planet.moons} Moons</span>
                  </div>
                  <p className="text-xs text-muted-foreground truncate">{planet.moonDetails}</p>
                </div>
              )}

              <button onClick={() => setSelectedPlanet(planet)} className="mt-4 w-full h-8 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded-md flex items-center justify-center gap-2 transition-colors">
                <Sparkles className="h-3 w-3" /> Discover
              </button>
            </div>
          ))}
        </div>

      </div>

      {/* Discover Modal */}
      {selectedPlanet && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-card border border-white/10 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl relative">
            <button 
              onClick={() => setSelectedPlanet(null)}
              className="absolute top-4 right-4 p-2 rounded-full hover:bg-white/10 transition-colors z-10"
            >
              <X className="h-5 w-5" />
            </button>
            
            <div className="p-8 pb-0 flex flex-col items-center justify-center relative overflow-hidden h-64 bg-gradient-to-b from-blue-500/10 to-background border-b border-white/10">
              <div className="absolute inset-0 flex items-center justify-center opacity-20">
                <Orbit className="h-64 w-64 animate-spin-slow text-blue-400" style={{ animationDuration: '20s' }} />
              </div>
              <div className="relative z-10 p-6 rounded-full bg-background border-4 border-white/5 shadow-2xl animate-pulse" style={{ animationDuration: '4s' }}>
                <Globe2 className={`h-20 w-20 ${selectedPlanet.type === 'Gas Giant' ? 'text-orange-400' : selectedPlanet.type === 'Ice Giant' ? 'text-blue-400' : 'text-stone-400'}`} />
              </div>
              <h2 className="mt-4 text-3xl font-bold z-10">{selectedPlanet.name}</h2>
              <p className="text-sm text-blue-400 font-medium tracking-widest uppercase z-10 mb-4">{selectedPlanet.type}</p>
            </div>

            <div className="p-8 grid grid-cols-2 gap-6 bg-card">
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground uppercase">Average Temperature</p>
                <p className="font-medium text-lg">{selectedPlanet.temp}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground uppercase">Surface Gravity</p>
                <p className="font-medium text-lg">{selectedPlanet.gravity}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground uppercase">Atmosphere</p>
                <p className="font-medium text-lg">{selectedPlanet.atmosphere}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground uppercase">Distance from Sun</p>
                <p className="font-medium text-lg">{selectedPlanet.dist} AU</p>
              </div>
            </div>
            
          </div>
        </div>
      )}
    </div>
  );
};

export default SolarSystem;
