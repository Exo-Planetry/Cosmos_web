import { useState, useEffect } from 'react';
import { Filter, Search, Loader2 } from 'lucide-react';

const Explore = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [planets, setPlanets] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Filters
  const [minMass, setMinMass] = useState('');
  const [maxMass, setMaxMass] = useState('');
  const [method, setMethod] = useState('');
  const [minYear, setMinYear] = useState('');

  useEffect(() => {
    // Fetch top 500 planets from NASA TAP archive
    fetch('/api/planets/all?limit=500')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'Success') {
          setPlanets(data.data || []);
        }
      })
      .catch(err => console.error(err))
      .finally(() => setIsLoading(false));
  }, []);

  const filteredPlanets = planets.filter((planet: any) => {
    // Search
    const matchSearch = (planet.pl_name || '').toLowerCase().includes(searchTerm.toLowerCase());
    
    // Filters
    const mass = parseFloat(planet.pl_masse);
    const matchMinMass = minMass === '' || (!isNaN(mass) && mass >= parseFloat(minMass));
    const matchMaxMass = maxMass === '' || (!isNaN(mass) && mass <= parseFloat(maxMass));
    
    const year = parseInt(planet.disc_year);
    const matchMinYear = minYear === '' || (!isNaN(year) && year >= parseInt(minYear));
    
    const methodMatch = method === '' || (planet.discoverymethod || '').toLowerCase().includes(method.toLowerCase());

    return matchSearch && matchMinMass && matchMaxMass && matchMinYear && methodMatch;
  });

  return (
    <div className="flex-1 p-4 md:p-8 overflow-auto">
      <div className="max-w-7xl mx-auto space-y-6">
        
        <header className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight">Explore Exoplanets</h1>
          <p className="text-muted-foreground">
            Browse and filter the NASA Exoplanet Archive (Showing up to 500 records).
          </p>
        </header>

        <div className="bg-card border border-white/10 rounded-xl p-6 mb-6 flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search planet name..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="w-full h-9 rounded-md border border-white/10 bg-white/5 px-8 py-2 text-sm focus:outline-none focus:border-blue-500"
            />
          </div>
          
          <div className="flex flex-wrap gap-4">
             <input type="number" placeholder="Min Mass (M⊕)" value={minMass} onChange={e => setMinMass(e.target.value)} className="w-32 h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
             <input type="number" placeholder="Max Mass (M⊕)" value={maxMass} onChange={e => setMaxMass(e.target.value)} className="w-32 h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
             <input type="number" placeholder="From Year" value={minYear} onChange={e => setMinYear(e.target.value)} className="w-28 h-9 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500" />
             
             <select value={method} onChange={e => setMethod(e.target.value)} className="w-40 h-9 rounded-md border border-white/10 bg-card px-3 text-sm text-foreground focus:outline-none focus:border-blue-500">
                <option value="" className="bg-card text-foreground">All Methods</option>
                <option value="transit" className="bg-card text-foreground">Transit</option>
                <option value="radial velocity" className="bg-card text-foreground">Radial Velocity</option>
                <option value="imaging" className="bg-card text-foreground">Direct Imaging</option>
                <option value="microlensing" className="bg-card text-foreground">Microlensing</option>
             </select>
          </div>
        </div>

        <div className="rounded-xl border border-white/10 bg-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-white/5 text-muted-foreground text-xs uppercase font-semibold">
                <tr>
                  <th className="px-6 py-4">Name</th>
                  <th className="px-6 py-4">Disc. Year</th>
                  <th className="px-6 py-4">Method</th>
                  <th className="px-6 py-4">Mass (M⊕)</th>
                  <th className="px-6 py-4">Radius (R⊕)</th>
                  <th className="px-6 py-4">Period (d)</th>
                  <th className="px-6 py-4">Host Star</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {isLoading ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-muted-foreground">
                      <div className="flex flex-col items-center justify-center gap-3">
                         <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
                         <span>Querying NASA Exoplanet Archive...</span>
                      </div>
                    </td>
                  </tr>
                ) : filteredPlanets.length > 0 ? (
                  filteredPlanets.map((planet: any) => (
                    <tr key={planet.pl_name} className="hover:bg-white/[0.02] transition-colors">
                      <td className="px-6 py-4 font-medium text-foreground">{planet.pl_name}</td>
                      <td className="px-6 py-4 text-muted-foreground">{planet.disc_year || 'N/A'}</td>
                      <td className="px-6 py-4 text-muted-foreground">{planet.discoverymethod || 'Unknown'}</td>
                      <td className="px-6 py-4 text-muted-foreground">{planet.pl_masse ? planet.pl_masse.toFixed(2) : 'N/A'}</td>
                      <td className="px-6 py-4 text-muted-foreground">{planet.pl_rade ? planet.pl_rade.toFixed(2) : 'N/A'}</td>
                      <td className="px-6 py-4 text-muted-foreground">{planet.pl_orbper ? planet.pl_orbper.toFixed(2) : 'N/A'}</td>
                      <td className="px-6 py-4 text-muted-foreground">{planet.hostname || 'Unknown'}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-muted-foreground">
                      No exoplanets match the selected filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Explore;
