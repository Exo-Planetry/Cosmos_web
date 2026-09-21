import React, { useState } from 'react';
import { Telescope, Loader2, ArrowRight } from 'lucide-react';

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccessMessage('');

    const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
    const payload = isLogin 
      ? { email, password } 
      : { email, password, display_name: displayName, role: 'researcher' };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      
      if (!res.ok) {
        setError(data.detail || 'Authentication failed.');
      } else {
        if (data.token) {
          localStorage.setItem('cosmos_token', data.token);
          setSuccessMessage(isLogin ? 'Logged in successfully!' : 'Registration successful!');
          setTimeout(() => {
            window.location.href = '/';
          }, 1500);
        }
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4 min-h-[calc(100vh-4rem)]">
      <div className="w-full max-w-md space-y-8">
        <div className="flex flex-col items-center justify-center text-center">
          <Telescope className="h-12 w-12 text-blue-500 mb-4" />
          <h2 className="text-3xl font-bold tracking-tight text-foreground">
            {isLogin ? 'Welcome back' : 'Create an account'}
          </h2>
          <p className="text-muted-foreground mt-2">
            {isLogin ? 'Sign in to access your analysis tools.' : 'Join the Cosmos network.'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6 bg-card border border-white/10 p-6 sm:p-8 rounded-xl shadow-lg">
          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-500 text-sm rounded-md">
              {error}
            </div>
          )}
          {successMessage && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-sm rounded-md">
              {successMessage}
            </div>
          )}
          <div className="space-y-4">
            {!isLogin && (
              <div>
                <label className="text-sm font-medium text-muted-foreground block mb-1">Display Name</label>
                <input
                  type="text"
                  required
                  value={displayName}
                  onChange={e => setDisplayName(e.target.value)}
                  className="w-full h-10 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500 transition-colors"
                  placeholder="Carl Sagan"
                />
              </div>
            )}
            <div>
              <label className="text-sm font-medium text-muted-foreground block mb-1">Email address</label>
              <input
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full h-10 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500 transition-colors"
                placeholder="astronomer@example.com"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground block mb-1">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full h-10 rounded-md border border-white/10 bg-white/5 px-3 text-sm focus:outline-none focus:border-blue-500 transition-colors"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full h-10 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-medium flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            {isLogin ? 'Sign In' : 'Sign Up'}
            {!isLoading && <ArrowRight className="h-4 w-4" />}
          </button>

          <div className="text-center text-sm text-muted-foreground">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-blue-400 hover:text-blue-300 transition-colors font-medium"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Auth;
