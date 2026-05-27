import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Car, Send, Sparkles, Shield, Users, Fuel, ChevronRight, Menu, X, Home } from 'lucide-react';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const loadingMessages = [
    'Menganalisis kebutuhan Anda...',
    'Mencari informasi mobil yang sesuai...',
    'Memproses data dengan RAG pipeline...',
    'Membandingkan spesifikasi...',
    'Menyiapkan rekomendasi...'
  ];

  const quickActions = [
    {
      icon: Shield,
      text: 'Keamanan & Keselamatan',
      prompt: 'Rekomendasikan mobil dengan fitur keselamatan terbaik untuk keluarga saya'
    },
    {
      icon: Users,
      text: 'Kapasitas Penumpang',
      prompt: 'Saya butuh mobil yang muat 7 orang untuk keluarga besar'
    },
    {
      icon: Fuel,
      text: 'Efisiensi BBM',
      prompt: 'Mobil apa yang paling irit bensin untuk penggunaan sehari-hari?'
    }
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    const conversationHistory = messages.map(({ role, content }) => ({ role, content }));
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setLoadingMessage(loadingMessages[0]);

    let messageIndex = 0;
    const intervalId = setInterval(() => {
      setLoadingMessage(loadingMessages[messageIndex % loadingMessages.length]);
      messageIndex++;
    }, 2000);

    try {
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          conversation_history: conversationHistory
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiContent = '';
      let firstChunk = true;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        aiContent += chunk;
        
        if (firstChunk) {
          setMessages(prev => [...prev, { role: 'ai', content: aiContent }]);
          firstChunk = false;
        } else {
          setMessages(prev => {
            const updated = [...prev];
            updated[updated.length - 1] = { ...updated[updated.length - 1], content: aiContent };
            return updated;
          });
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { role: 'ai', content: 'Maaf, terjadi kesalahan. Silakan coba lagi.' }]);
    } finally {
      setLoading(false);
      setLoadingMessage('');
      clearInterval(intervalId);
    }
  };

  const handleQuickAction = (prompt) => {
    setInput(prompt);
    inputRef.current?.focus();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen gradient-bg gradient-mesh">
      <header className="glass sticky top-0 z-50 border-b border-slate-200/50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <Car className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-slate-800" style={{ fontFamily: 'Plus Jakarta Sans, system-ui' }}>
                  Tony
                </h1>
                <p className="text-xs text-slate-500">AI Car Assistant</p>
              </div>
            </div>

            <nav className="hidden md:flex items-center gap-1">
              <a
                href="/"
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-cyan-600 bg-cyan-50"
              >
                <Home className="w-4 h-4" />
                Chat
              </a>
            </nav>

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden border-t border-slate-200 bg-white">
            <nav className="px-4 py-3 space-y-1">
              <a
                href="/"
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-cyan-600 bg-cyan-50"
              >
                <Home className="w-4 h-4" />
                Chat
              </a>
            </nav>
          </div>
        )}
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-6">
        <div className="flex flex-col min-h-[calc(100vh-8rem)]">
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center py-12 animate-fade-in">
              <div className="text-center max-w-lg">
                <div className="relative inline-block mb-8">
                  <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center shadow-2xl shadow-cyan-500/30 car-float">
                    <Car className="w-12 h-12 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-gradient-to-br from-orange-400 to-orange-500 flex items-center justify-center shadow-lg">
                    <Sparkles className="w-4 h-4 text-white" />
                  </div>
                </div>

                <h2 className="text-2xl sm:text-3xl font-bold text-slate-800 mb-3" style={{ fontFamily: 'Plus Jakarta Sans, system-ui' }}>
                  Halo! Saya <span className="gradient-text">Tony</span>
                </h2>
                <p className="text-slate-600 mb-8 leading-relaxed">
                  asisten AI yang siap membantu Anda menemukan mobil impian. Tanyakan tentang spesifikasi, fitur, atau minta rekomendasi sesuai kebutuhan Anda!
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full">
                  {quickActions.map((action, index) => (
                    <button
                      key={index}
                      onClick={() => handleQuickAction(action.prompt)}
                      className={`quick-action rounded-2xl p-4 text-left animate-fade-in-up stagger-${index + 1}`}
                      style={{ opacity: 0, animationFillMode: 'forwards' }}
                    >
                      <action.icon className="w-5 h-5 text-cyan-600 mb-2" />
                      <p className="text-sm font-medium text-slate-700">{action.text}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto pb-24 hide-scrollbar">
              <div className="space-y-4">
                {messages.map((message, index) => {
                  if (message.role === 'ai' && !message.content && loading) {
                    return null;
                  }
                  return (
                    <div
                      key={index}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}
                      style={{ animationDelay: `${index * 50}ms`, animationFillMode: 'forwards', opacity: 0 }}
                    >
                      <div className={`message-bubble ${message.role === 'user' ? 'message-bubble-user' : 'message-bubble-ai'}`}>
                        {message.role === 'ai' && (
                          <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
                            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center">
                              <Car className="w-3 h-3 text-white" />
                            </div>
                            <span className="text-xs font-semibold text-slate-600">Tony</span>
                          </div>
                        )}
                        {message.role === 'user' ? (
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        ) : (
                          <div className="prose-custom">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {message.content}
                            </ReactMarkdown>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}

                {loading && messages.every(m => m.role === 'user') && (
                  <div className="flex justify-start animate-fade-in">
                    <div className="message-bubble message-bubble-ai">
                      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
                        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center">
                          <Car className="w-3 h-3 text-white" />
                        </div>
                        <span className="text-xs font-semibold text-slate-600">Tony</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="flex gap-1">
                          <span className="typing-dot"></span>
                          <span className="typing-dot"></span>
                          <span className="typing-dot"></span>
                        </div>
                        <span className="text-xs text-slate-500">{loadingMessage}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div ref={messagesEndRef} />
            </div>
          )}

          {messages.length > 0 && (
            <div className="mt-4">
              <div className="flex gap-2 mb-3">
                {quickActions.map((action, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickAction(action.prompt)}
                    className="quick-action rounded-full px-3 py-1.5 text-xs font-medium text-slate-600 flex items-center gap-1.5"
                  >
                    <ChevronRight className="w-3 h-3" />
                    {action.text}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>

      <div className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-sm border-t border-slate-200 shadow-2xl shadow-slate-200/50">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-end gap-3">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ketik pertanyaan Anda di sini..."
                disabled={loading}
                rows={1}
                className="chat-input w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl resize-none text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-cyan-400 focus:bg-white"
                style={{ maxHeight: '120px', minHeight: '48px' }}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="btn-hover flex-shrink-0 w-12 h-12 rounded-2xl bg-gradient-to-br from-cyan-500 to-cyan-600 text-white flex items-center justify-center shadow-lg shadow-cyan-500/30 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none transition-all"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <p className="text-xs text-slate-400 mt-2 text-center">
            Tekan Enter untuk mengirim • Shift + Enter untuk baris baru
          </p>
        </div>
      </div>
    </div>
  );
}

export default Chat;
