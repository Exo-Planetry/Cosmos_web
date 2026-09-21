import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';

const INITIAL_MESSAGES = [
  { id: 1, role: 'assistant', text: 'Hello! I am the Cosmos AI Assistant. Ask me anything about exoplanets, stellar data, or astrobiology.' },
];

const AIAssistant = () => {
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { id: Date.now(), role: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Basic NLP: Extract potential target name from input
      const targetSearch = input.replace(/analyze|tell me about|what is|search for/gi, '').trim();
      
      const res = await fetch(`/api/targets/${encodeURIComponent(targetSearch)}`);
      const data = await res.json();
      
      if (data.status === 'Success') {
        const p = data.data;
        const text = `I found data for ${p.pl_name || targetSearch}. It is a confirmed exoplanet with a mass of ${p.pl_masse ? p.pl_masse + ' Earths' : 'Unknown'}, a radius of ${p.pl_rade ? p.pl_rade + ' Earths' : 'Unknown'}, and an orbital period of ${p.pl_orbper ? p.pl_orbper + ' days' : 'Unknown'}. It was discovered in ${p.disc_year || 'Unknown'}.`;
        
        setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', text }]);
      } else {
        setMessages(prev => [...prev, { 
          id: Date.now() + 1, 
          role: 'assistant', 
          text: `I couldn't find detailed telemetry for "${targetSearch}". It might not be in the confirmed catalog, or my models failed to parse it.` 
        }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { 
        id: Date.now() + 1, 
        role: 'assistant', 
        text: `Error connecting to the Cosmos backend AI services.` 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 p-4 md:p-8 flex flex-col h-[calc(100vh-64px)]">
      <div className="max-w-4xl mx-auto w-full flex-1 flex flex-col bg-card border border-white/10 rounded-xl overflow-hidden shadow-sm">
        
        <header className="p-4 border-b border-white/10 bg-white/5 flex items-center gap-3">
          <div className="p-2 bg-blue-500/20 text-blue-400 rounded-lg">
            <Bot className="h-6 w-6" />
          </div>
          <div>
            <h2 className="font-semibold text-foreground">Cosmos AI</h2>
            <p className="text-xs text-muted-foreground">Scientific Research Assistant</p>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                msg.role === 'user' ? 'bg-primary border border-white/20' : 'bg-blue-500/20 text-blue-400'
              }`}>
                {msg.role === 'user' ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
              </div>
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-sm' 
                  : 'bg-white/5 border border-white/10 text-foreground rounded-tl-sm'
              }`}>
                <p className="text-sm leading-relaxed">{msg.text}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4 flex-row">
              <div className="flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center bg-blue-500/20 text-blue-400">
                <Bot className="h-5 w-5" />
              </div>
              <div className="max-w-[80%] rounded-2xl px-4 py-3 bg-white/5 border border-white/10 text-foreground rounded-tl-sm flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Analyzing...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 bg-background border-t border-white/10">
          <form onSubmit={handleSend} className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about exoplanet transit data..."
              className="w-full bg-white/5 border border-white/10 rounded-full pl-6 pr-12 py-3 text-sm focus:outline-none focus:border-white/20 focus:ring-1 focus:ring-blue-500/50 transition-all text-foreground placeholder:text-muted-foreground"
            />
            <button 
              type="submit" 
              disabled={!input.trim() || isLoading}
              className="absolute right-2 p-2 rounded-full bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
          <div className="text-center mt-3">
             <p className="text-[10px] text-muted-foreground">AI responses may be simulated. Do not use for actual astrometric measurements.</p>
          </div>
        </div>

      </div>
    </div>
  );
};

export default AIAssistant;
