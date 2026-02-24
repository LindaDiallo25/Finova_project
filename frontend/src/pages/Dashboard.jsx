import React, { useState } from 'react';
import { FileUploader } from '../components/FileUploader';
import { DynamicDashboard } from '../components/DynamicDashboard';
import { ChatBot } from '../components/ChatBot';
import { AnomalyDetection } from '../components/AnomalyDetection';
import { ExpensePredictions } from '../components/ExpensePredictions';
import { MLInsights } from '../components/MLInsights';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { AlertCircle, CheckCircle, MessageSquare, BarChart3, Brain, Moon, Sun, Home } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export function Dashboard() {
  const [analysisId, setAnalysisId] = useState(null);
  const [expenses, setExpenses] = useState(null);
  const [context, setContext] = useState(null);
  const [initialAnalysis, setInitialAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const { isDark, toggleTheme } = useTheme();

  const handleFileSelect = async (file) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      // Affiche l'état de chargement quelques secondes pour montrer le spinner
      const response = await fetch(`${API_URL}/api/chat/upload-and-analyze`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}`);
      }

      const data = await response.json();
      
      // Garder le spinner visible un peu plus longtemps pour UX
      await new Promise(resolve => setTimeout(resolve, 800));
      
      setAnalysisId(data.analysis_id);
      setExpenses(data.expenses || []);
      setContext(data.context);
      setInitialAnalysis(data.initial_analysis);
      setActiveTab('dashboard');
    } catch (err) {
      setError('Erreur lors du téléchargement: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewAnalysis = () => {
    setAnalysisId(null);
    setExpenses(null);
    setContext(null);
    setInitialAnalysis(null);
    setError(null);
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      isDark
        ? 'bg-gradient-to-br from-slate-950 to-slate-900'
        : 'bg-gradient-to-br from-slate-50 to-white'
    }`}>
      {/* Header */}
      <header className={`border-b transition-all duration-300 ${
        isDark
          ? 'border-slate-800 bg-slate-950/95 backdrop-blur-lg'
          : 'border-slate-200 bg-white/95 backdrop-blur-lg'
      } sticky top-0 z-50`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity" onClick={() => window.location.href = '/'}>
              <img src="/Logo.png" alt="Finova" className="h-8 w-8 rounded-lg" />
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">
                Finova
              </h1>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={toggleTheme}
                className={`p-2 rounded-lg transition-all duration-200 ${
                  isDark
                    ? 'bg-slate-800 hover:bg-slate-700 text-yellow-400'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
                }`}
                title={isDark ? 'Mode clair' : 'Mode nuit'}
              >
                {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>
              
              <button
                onClick={() => window.location.href = '/'}
                className={`p-2 rounded-lg transition-all duration-200 flex items-center gap-2 ${
                  isDark
                    ? 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
                }`}
                title="Accueil"
              >
                <Home className="h-5 w-5" />
              </button>
            </div>
          </div>
          
          <p className={`text-sm mt-2 ${isDark ? 'text-slate-500' : 'text-slate-600'}`}>
            Gestion Budgétaire avec Chatbot IA et Machine Learning
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Alert */}
        {error && (
          <div className={`mb-6 p-4 rounded-lg border flex gap-3 ${
            isDark
              ? 'bg-red-500/10 border-red-500/30'
              : 'bg-red-50 border-red-200'
          }`}>
            <AlertCircle className={`h-5 w-5 flex-shrink-0 ${
              isDark ? 'text-red-400' : 'text-red-600'
            }`} />
            <p className={isDark ? 'text-red-400' : 'text-red-700'}>{error}</p>
          </div>
        )}

        {/* Upload Section */}
        {!analysisId ? (
          <div className="max-w-2xl mx-auto">
            <FileUploader onFileSelect={handleFileSelect} isLoading={isLoading} />
          </div>
        ) : (
          <>
            {/* Analysis Section */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-6 w-6 text-green-500" />
                  <div>
                    <h2 className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                      Analyse Chargée
                    </h2>
                    <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                      {expenses.length} transactions • Période: {context?.date_range}
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleNewAnalysis}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    isDark
                      ? 'bg-slate-800 hover:bg-slate-700 text-blue-400 border border-slate-700'
                      : 'bg-blue-50 hover:bg-blue-100 text-blue-600 border border-blue-200'
                  }`}
                >
                  Nouvelle Analyse
                </button>
              </div>

              {/* Initial Analysis from ChatBot */}
              {initialAnalysis && (
                <div className={`rounded-lg p-4 mb-6 border ${
                  isDark
                    ? 'bg-slate-800/50 border-slate-700'
                    : 'bg-blue-50 border-blue-200'
                }`}>
                  <p className={`${isDark ? 'text-slate-200' : 'text-slate-900'} italic`}>
                    <span className="font-semibold text-blue-600">🤖 IA:</span> {initialAnalysis}
                  </p>
                </div>
              )}
            </div>

            {/* Tabs */}
            <div className={`flex gap-2 mb-6 border-b overflow-x-auto ${
              isDark ? 'border-slate-800' : 'border-slate-200'
            }`}>
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-4 py-3 font-medium flex items-center gap-2 transition-all whitespace-nowrap border-b-2 ${
                  activeTab === 'dashboard'
                    ? `border-blue-600 ${isDark ? 'text-blue-400' : 'text-blue-600'}`
                    : `border-transparent ${isDark ? 'text-slate-400 hover:text-slate-300' : 'text-slate-600 hover:text-slate-900'}`
                }`}
              >
                <BarChart3 className="h-5 w-5" />
                Dashboards
              </button>
              <button
                onClick={() => setActiveTab('ml')}
                className={`px-4 py-3 font-medium flex items-center gap-2 transition-all whitespace-nowrap border-b-2 ${
                  activeTab === 'ml'
                    ? `border-violet-600 ${isDark ? 'text-violet-400' : 'text-violet-600'}`
                    : `border-transparent ${isDark ? 'text-slate-400 hover:text-slate-300' : 'text-slate-600 hover:text-slate-900'}`
                }`}
              >
                <Brain className="h-5 w-5" />
                ML & Insights
              </button>
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-4 py-3 font-medium flex items-center gap-2 transition-all whitespace-nowrap border-b-2 ${
                  activeTab === 'chat'
                    ? `border-cyan-600 ${isDark ? 'text-cyan-400' : 'text-cyan-600'}`
                    : `border-transparent ${isDark ? 'text-slate-400 hover:text-slate-300' : 'text-slate-600 hover:text-slate-900'}`
                }`}
              >
                <MessageSquare className="h-5 w-5" />
                Chatbot
              </button>
            </div>

            {isLoading && <LoadingSpinner message="Chargement..." />}

            {/* Tab Content */}
            <div className={activeTab === 'dashboard' ? 'block' : 'hidden'}>
              {expenses && context && (
                <DynamicDashboard expenses={expenses} context={context} />
              )}
            </div>

            <div className={activeTab === 'ml' ? 'block' : 'hidden'}>
              {analysisId && (
                <div className="space-y-6">
                  <div>
                    <h2 className={`text-2xl font-bold mb-4 flex items-center gap-2 ${
                      isDark ? 'text-white' : 'text-slate-900'
                    }`}>
                      <Brain className="h-6 w-6 text-violet-600" />
                      Machine Learning & Insights
                    </h2>
                    <p className={`${isDark ? 'text-slate-400' : 'text-slate-600'} mb-6`}>
                      Prédictions, anomalies et recommandations intelligentes basées sur vos données
                    </p>
                  </div>

                  {/* Anomalies & Predictions Grid */}
                  <div className="grid lg:grid-cols-2 gap-6">
                    <AnomalyDetection analysisId={analysisId} />
                    <ExpensePredictions analysisId={analysisId} />
                  </div>

                  {/* ML Insights */}
                  <MLInsights analysisId={analysisId} />
                </div>
              )}
            </div>

            <div className={activeTab === 'chat' ? 'block' : 'hidden'}>
              {analysisId && (
                <div style={{ height: '600px' }}>
                  <ChatBot analysisId={analysisId} expenses={expenses} />
                </div>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

