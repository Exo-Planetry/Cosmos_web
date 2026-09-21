import { Telescope, Globe, Activity, Star } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const CHART_DATA = [
  { year: '2010', planets: 120 },
  { year: '2012', planets: 250 },
  { year: '2014', planets: 850 },
  { year: '2016', planets: 1400 },
  { year: '2018', planets: 3800 },
  { year: '2020', planets: 4300 },
  { year: '2022', planets: 5200 },
  { year: '2024', planets: 5500 },
];

const MetricCard = ({ title, value, icon: Icon, description }: any) => (
  <div className="rounded-xl border border-white/10 bg-card p-6 shadow-sm flex flex-col gap-2 hover:border-white/20 transition-all duration-300">
    <div className="flex items-center gap-4">
      <div className="p-3 rounded-lg bg-blue-500/10 text-blue-500">
        <Icon className="h-6 w-6" />
      </div>
      <div>
        <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
        <p className="text-3xl font-bold text-foreground">{value}</p>
      </div>
    </div>
    {description && (
      <p className="text-xs text-muted-foreground mt-2">{description}</p>
    )}
  </div>
);

const Dashboard = () => {
  return (
    <div className="flex-1 p-4 md:p-8 overflow-auto">
      <div className="max-w-7xl mx-auto space-y-8">
        
        <header className="flex flex-col gap-2">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Research Dashboard</h1>
          <p className="text-muted-foreground text-base md:text-lg">
            Welcome to the Exoplanet & Habitable Planet Explorer.
          </p>
        </header>

        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          <MetricCard 
            title="Confirmed Planets" 
            value="5,500+" 
            icon={Globe} 
            description="From NASA Exoplanet Archive" 
          />
          <MetricCard 
            title="Potentially Habitable" 
            value="60+" 
            icon={Activity} 
            description="In conservative habitable zone" 
          />
          <MetricCard 
            title="Host Stars" 
            value="4,100+" 
            icon={Star} 
            description="Analyzed stellar systems" 
          />
          <MetricCard 
            title="Recent Observations" 
            value="12" 
            icon={Telescope} 
            description="Latest spectra imports" 
          />
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 rounded-xl border border-white/10 bg-card p-4 md:p-6 min-h-[400px] flex flex-col">
            <h3 className="font-semibold text-lg mb-6">Exoplanet Discoveries Over Time</h3>
            <div className="flex-1 min-h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={CHART_DATA} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorPlanets" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="year" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#18181b', borderColor: '#333', borderRadius: '8px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Area type="monotone" dataKey="planets" stroke="#3b82f6" fillOpacity={1} fill="url(#colorPlanets)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="rounded-xl border border-white/10 bg-card p-6 min-h-[400px]">
             <h3 className="font-semibold text-lg mb-4">Recent Discoveries</h3>
             <ul className="space-y-4">
                {[1,2,3,4].map((i) => (
                  <li key={i} className="flex items-center justify-between border-b border-white/5 pb-4 last:border-0">
                    <div>
                      <p className="font-medium text-foreground">K2-18 b</p>
                      <p className="text-xs text-muted-foreground">Water vapor detected</p>
                    </div>
                    <span className="text-xs px-2 py-1 bg-blue-500/10 text-blue-400 rounded-full">Atmosphere</span>
                  </li>
                ))}
             </ul>
          </div>
        </section>

      </div>
    </div>
  );
};

export default Dashboard;
