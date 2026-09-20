
import { NavLink } from 'react-router-dom';
import { Telescope, Menu, Search, User } from 'lucide-react';

const Navbar = () => {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-white/10 bg-background/60 backdrop-blur-md">
      <div className="flex h-16 items-center px-6 gap-8">
        <div className="flex items-center gap-2 text-primary font-bold text-xl tracking-tight">
          <Telescope className="h-6 w-6 text-blue-500" />
          <span>COSMOS <span className="text-blue-500">5.0</span></span>
        </div>
        
        <div className="hidden md:flex flex-1 items-center gap-6 text-sm font-medium text-muted-foreground">
          <NavLink to="/" className={({isActive}) => isActive ? "text-foreground transition-colors" : "hover:text-foreground transition-colors"}>Dashboard</NavLink>
          <NavLink to="/explore" className={({isActive}) => isActive ? "text-foreground transition-colors" : "hover:text-foreground transition-colors"}>Explore Planets</NavLink>
          <NavLink to="/stars" className={({isActive}) => isActive ? "text-foreground transition-colors" : "hover:text-foreground transition-colors"}>Stars</NavLink>
          <NavLink to="/ai" className={({isActive}) => isActive ? "text-foreground transition-colors" : "hover:text-foreground transition-colors"}>AI Assistant</NavLink>
        </div>

        <div className="flex items-center gap-4 ml-auto">
          <div className="relative hidden sm:block">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="search"
              placeholder="Search targets..."
              className="h-9 w-64 rounded-md border border-white/10 bg-white/5 px-8 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all"
            />
          </div>
          <button className="h-9 w-9 rounded-full bg-white/5 flex items-center justify-center border border-white/10 hover:bg-white/10 transition-colors">
            <User className="h-4 w-4 text-foreground" />
          </button>
          <button className="md:hidden h-9 w-9 flex items-center justify-center">
            <Menu className="h-5 w-5 text-foreground" />
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
