import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Explore from './pages/Explore';
import Stars from './pages/Stars';
import AIAssistant from './pages/AIAssistant';
import Analyzer from './pages/Analyzer';
import Auth from './pages/Auth';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="explore" element={<Explore />} />
          <Route path="stars" element={<Stars />} />
          <Route path="analyze" element={<Analyzer />} />
          <Route path="ai" element={<AIAssistant />} />
          <Route path="auth" element={<Auth />} />
          <Route path="*" element={<div className="p-8 text-destructive">404 Not Found</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
