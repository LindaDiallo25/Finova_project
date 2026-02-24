import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader, Copy, Check, AlertCircle } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { cleanMarkdown } from '../utils/markdownCleaner';

export function ChatBot({ analysisId, expenses }) {
  const { isDark } = useTheme();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Bonjour! Je suis votre assistant financier. Je peux vous aider à analyser vos dépenses, vous proposer des optimisations et répondre à vos questions budgétaires. Comment puis-je vous aider?',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const suggestedQuestions = [
    'Quelle est ma plus grande catégorie de dépenses?',
    'Comment puis-je réduire mes dépenses?',
    'Quels sont mes restaurants préférés?',
    'Analyse mon budget mensuel'
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleSendMessage = async (messageText = null) => {
    const textToSend = messageText || input;
    if (!textToSend.trim()) return;

    // Ajouter le message utilisateur
    const userMessage = { 
      role: 'user', 
      content: textToSend,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: textToSend,
          analysis_id: analysisId
        })
      });

      const data = await response.json();
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        relevant_expenses: data.relevant_expenses || [],
        timestamp: new Date()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Erreur: ${error.message}`,
        isError: true,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`flex flex-col h-full rounded-lg overflow-hidden border transition-colors ${
      isDark ? 'bg-slate-900 border-slate-700' : 'bg-white border-slate-200'
    }`}>
      {/* Header */}
      <div className={`px-6 py-4 border-b transition-colors ${
        isDark ? 'bg-slate-800 border-slate-700' : 'bg-slate-50 border-slate-200'
      }`}>
        <h2 className={`text-lg font-semibold transition-colors ${
          isDark ? 'text-white' : 'text-slate-900'
        }`}>
          Assistant Financier
        </h2>
        <p className={`text-sm transition-colors ${
          isDark ? 'text-slate-400' : 'text-slate-600'
        }`}>
          Poser des questions sur vos dépenses
        </p>
      </div>

      {/* Messages List */}
      <div className={`flex-1 overflow-y-auto p-4 space-y-4 transition-colors ${
        isDark ? 'bg-slate-900' : 'bg-white'
      }`}>
        {messages.map((msg, idx) => (
          <div key={idx} className="space-y-2">
            <div className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className="flex gap-3 max-w-2xl">
                {msg.role === 'assistant' && (
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-semibold transition-colors ${
                    isDark 
                      ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white' 
                      : 'bg-gradient-to-br from-blue-400 to-purple-500 text-white'
                  }`}>
                    AI
                  </div>
                )}
                
                <div className="flex-1">
                  <div
                    className={`px-4 py-3 rounded-lg transition-colors ${
                      msg.role === 'user'
                        ? isDark 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-blue-500 text-white'
                        : isDark
                          ? msg.isError ? 'bg-red-900/30 text-red-200' : 'bg-slate-800 text-slate-100'
                          : msg.isError ? 'bg-red-50 text-red-900' : 'bg-slate-100 text-slate-900'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{cleanMarkdown(msg.content)}</p>
                  </div>
                  
                  {/* Relevant Expenses Display */}
                  {msg.relevant_expenses && msg.relevant_expenses.length > 0 && (
                    <div className={`mt-3 p-3 rounded-lg border transition-colors ${
                      isDark
                        ? 'bg-slate-800/50 border-slate-700'
                        : 'bg-slate-50 border-slate-200'
                    }`}>
                      <p className={`text-xs font-semibold mb-2 transition-colors ${
                        isDark ? 'text-slate-300' : 'text-slate-600'
                      }`}>
                        📊 Transactions trouvées ({msg.relevant_expenses.length}):
                      </p>
                      <div className="space-y-2">
                        {msg.relevant_expenses.map((exp, expIdx) => (
                          <div key={expIdx} className={`text-xs p-2 rounded transition-colors ${
                            isDark
                              ? 'bg-slate-700/50 text-slate-200'
                              : 'bg-white text-slate-700'
                          }`}>
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <p className="font-medium">{exp.merchant || exp.category}</p>
                                <p className={`transition-colors ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                                  {exp.description} • {exp.date}
                                </p>
                              </div>
                              <p className="font-semibold text-right ml-2">{exp.amount}€</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Message Footer */}
                  <div className="flex items-center justify-between mt-2 px-1">
                    <span className={`text-xs transition-colors ${
                      isDark ? 'text-slate-500' : 'text-slate-400'
                    }`}>
                      {formatTime(msg.timestamp)}
                    </span>
                    {msg.role === 'assistant' && !msg.isError && (
                      <button
                        onClick={() => copyToClipboard(msg.content, idx)}
                        className={`p-1 rounded hover:opacity-70 transition-all ${
                          copiedId === idx
                            ? isDark ? 'text-green-400' : 'text-green-600'
                            : isDark ? 'text-slate-500 hover:text-slate-400' : 'text-slate-400 hover:text-slate-600'
                        }`}
                      >
                        {copiedId === idx ? (
                          <Check className="h-4 w-4" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </button>
                    )}
                  </div>
                </div>

                {msg.role === 'user' && (
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-semibold transition-colors ${
                    isDark
                      ? 'bg-slate-700 text-slate-200'
                      : 'bg-slate-300 text-slate-700'
                  }`}>
                    👤
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="flex gap-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-semibold transition-colors ${
                isDark 
                  ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white' 
                  : 'bg-gradient-to-br from-blue-400 to-purple-500 text-white'
              }`}>
                AI
              </div>
              <div className={`px-4 py-3 rounded-lg transition-colors ${
                isDark ? 'bg-slate-800' : 'bg-slate-100'
              }`}>
                <div className="flex gap-1 items-center">
                  <Loader className="h-4 w-4 animate-spin" />
                  <span className={`text-sm transition-colors ${
                    isDark ? 'text-slate-300' : 'text-slate-600'
                  }`}>L'assistant réfléchit...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions */}
      {messages.length === 1 && (
        <div className={`px-4 py-3 border-t transition-colors ${
          isDark 
            ? 'bg-slate-800/50 border-slate-700' 
            : 'bg-slate-50 border-slate-200'
        }`}>
          <p className={`text-xs font-semibold mb-2 transition-colors ${
            isDark ? 'text-slate-400' : 'text-slate-600'
          }`}>
            Questions suggérées:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {suggestedQuestions.map((question, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(question)}
                className={`text-left text-xs px-3 py-2 rounded transition-all hover:scale-105 active:scale-95 ${
                  isDark
                    ? 'bg-slate-700 text-slate-200 hover:bg-slate-600'
                    : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 hover:border-slate-300'
                }`}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className={`border-t transition-colors ${
        isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'
      }`}>
        <div className="p-4">
          <div className="flex gap-3">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Posez votre question financière..."
              className={`flex-1 rounded-lg px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 transition-all ${
                isDark
                  ? 'bg-slate-700 border-slate-600 text-white placeholder-slate-400 focus:ring-blue-500'
                  : 'bg-slate-50 border-slate-200 text-slate-900 placeholder-slate-400 focus:ring-blue-400 border'
              }`}
              rows="2"
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={isLoading || !input.trim()}
              className={`h-fit px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                isLoading || !input.trim()
                  ? isDark
                    ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                    : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                  : isDark
                    ? 'bg-blue-600 hover:bg-blue-700 active:scale-95 text-white'
                    : 'bg-blue-500 hover:bg-blue-600 active:scale-95 text-white'
              }`}
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
          <p className={`text-xs mt-2 transition-colors ${
            isDark ? 'text-slate-500' : 'text-slate-400'
          }`}>
            Appuyez sur Entrée pour envoyer
          </p>
        </div>
      </div>
    </div>
  );
}

