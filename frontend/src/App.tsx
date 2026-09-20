
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="explore" element={<div className="p-8 text-muted-foreground">Planet Explorer Component Under Construction...</div>} />
          <Route path="stars" element={<div className="p-8 text-muted-foreground">Star Explorer Component Under Construction...</div>} />
          <Route path="ai" element={<div className="p-8 text-muted-foreground">AI Assistant Component Under Construction...</div>} />
          <Route path="*" element={<div className="p-8 text-destructive">404 Not Found</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
