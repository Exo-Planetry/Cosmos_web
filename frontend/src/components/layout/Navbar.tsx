import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { Telescope, Menu, Search, User, X, Sun, Moon } from 'lucide-react';

const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    // Check initial theme
    const isDarkMode = document.documentElement.classList.contains('dark');
    setIsDark(isDarkMode);
  }, []);

  const toggleTheme = () => {
    if (isDark) {
      document.documentElement.classList.remove('dark');
      setIsDark(false);
    } else {
      document.documentElement.classList.add('dark');
      setIsDark(true);
    }
  };

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-white/10 bg-background/60 backdrop-blur-md">
      <div className="flex h-16 items-center px-4 md:px-6 gap-4 md:gap-8 justify-between">
        <div className="flex items-center gap-2 text-primary font-bold text-xl tracking-tight">
          <Telescope className="h-6 w-6 text-blue-500" />
          <span className="hidden sm:inline">COSMOS <span className="text-blue-500"></span></span>
        </div>
        
        <div className="hidden md:flex flex-1 items-center gap-6 text-sm font-medium text-muted-foreground">
          <NavLink to="/" className={({isActive}) => isActive ? "text-foreground transition-colors" : "hover:text-foreground transition-colors"}>Dashboard</NavLink>
          <NavLink to="/explore" className={({isActive}) => isActive ? "text-foreground transition-colors" : "hover:text-foreground transition-colors"}>Explore Planets</NavLink>
          <NavLink to="/stars" className={({isActive}) => isActive ? "text-foreground transition-colors" : "hover:text-foreground transition-colors"}>Solar System</NavLink>
          <NavLink to="/analyze" className={({isActive}) => isActive ? "text-foreground transition-colors" : "hover:text-foreground transition-colors"}>Analyzer</NavLink>
          <NavLink to="/ai" className={({isActive}) => isActive ? "text-foreground transition-colors" : "hover:text-foreground transition-colors"}>AI Assistant</NavLink>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative hidden sm:block">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="search"
              placeholder="Search targets..."
              className="h-9 w-48 lg:w-64 rounded-md border border-white/10 bg-white/5 px-8 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all"
            />
          </div>

          <button onClick={toggleTheme} className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/10 transition-colors">
            {isDark ? <Sun className="h-5 w-5 text-foreground" /> : <Moon className="h-5 w-5 text-foreground" />}
          </button>
          
          <NavLink to="/auth" className="h-9 w-9 rounded-full bg-white/5 border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors">
            <User className="h-4 w-4" />
          </NavLink>
          
          <button 
            className="md:hidden p-2 -mr-2"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-white/10 bg-background/95 backdrop-blur-xl absolute top-16 left-0 w-full">
          <div className="flex flex-col p-4 gap-4 text-sm font-medium">
            <NavLink to="/" onClick={() => setIsMobileMenuOpen(false)} className={({isActive}) => `px-4 py-3 rounded-lg ${isActive ? "bg-white/10 text-foreground" : "text-muted-foreground hover:bg-white/5"}`}>Dashboard</NavLink>
            <NavLink to="/explore" onClick={() => setIsMobileMenuOpen(false)} className={({isActive}) => `px-4 py-3 rounded-lg ${isActive ? "bg-white/10 text-foreground" : "text-muted-foreground hover:bg-white/5"}`}>Explore Planets</NavLink>
            <NavLink to="/stars" onClick={() => setIsMobileMenuOpen(false)} className={({isActive}) => `px-4 py-3 rounded-lg ${isActive ? "bg-white/10 text-foreground" : "text-muted-foreground hover:bg-white/5"}`}>Stars</NavLink>
            <NavLink to="/analyze" onClick={() => setIsMobileMenuOpen(false)} className={({isActive}) => `px-4 py-3 rounded-lg ${isActive ? "bg-white/10 text-foreground" : "text-muted-foreground hover:bg-white/5"}`}>Analyzer</NavLink>
            <NavLink to="/ai" onClick={() => setIsMobileMenuOpen(false)} className={({isActive}) => `px-4 py-3 rounded-lg ${isActive ? "bg-white/10 text-foreground" : "text-muted-foreground hover:bg-white/5"}`}>AI Assistant</NavLink>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
