import React, { useEffect, useState } from 'react';
import { Navigation, BarChart3, Zap, Brain, TrendingUp, ArrowRight, Moon, Sun } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { analysisApi } from '../hooks/useApi';

export function Home() {
  const [isHealthy, setIsHealthy] = useState(null);
  const { isDark, toggleTheme } = useTheme();

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await analysisApi.healthCheck();
        setIsHealthy(true);
      } catch (err) {
        setIsHealthy(false);
      }
    };

    checkHealth();
  }, []);

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      isDark 
        ? 'bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950'
        : 'bg-gradient-to-br from-slate-50 via-white to-slate-50'
    }`}>
      {/* Animated background gradient */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-20 left-1/4 w-96 h-96 rounded-full blur-3xl opacity-30 ${
          isDark ? 'bg-blue-500' : 'bg-blue-300'
        } animate-pulse`} />
        <div className={`absolute bottom-20 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-30 ${
          isDark ? 'bg-violet-500' : 'bg-violet-300'
        } animate-pulse`} style={{ animationDelay: '1s' }} />
      </div>

      {/* Navigation Header */}
      <nav className={`relative flex items-center justify-between px-6 py-4 border-b transition-all duration-300 ${
        isDark
          ? 'border-slate-800 bg-slate-950/95 backdrop-blur-lg'
          : 'border-slate-200 bg-white/95 backdrop-blur-lg'
      }`}>
        <div className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity" onClick={() => window.location.href = '/'}>
          <img src="/Logo.png" alt="Finova" className="h-10 w-10 rounded-lg shadow-lg" />
          <span className={`text-2xl font-bold bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent`}>
            Finova
          </span>
        </div>
        
        <div className="flex items-center gap-4">
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
            onClick={() => window.location.href = '/dashboard'}
            disabled={isHealthy === false}
            className={`px-6 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
              isHealthy === false
                ? 'opacity-50 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-600 to-violet-600 hover:shadow-lg hover:shadow-blue-500/50 text-white hover:scale-105'
            }`}
          >
            Démarrer
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-[calc(100vh-80px)] flex flex-col items-center justify-center px-4 py-12">
        <div className="text-center max-w-4xl mx-auto z-10">
          {/* Logo Large */}
          <div className="mb-8 flex justify-center group">
            <div className="relative">
              <div className={`absolute inset-0 rounded-2xl blur-2xl opacity-40 group-hover:opacity-60 transition-opacity ${
                isDark ? 'bg-blue-500' : 'bg-blue-400'
              }`} />
              <img 
                src="/Logo.png" 
                alt="Finova" 
                className="relative h-28 w-28 rounded-2xl shadow-2xl transform group-hover:scale-105 transition-transform duration-300"
              />
            </div>
          </div>

          <h1 className={`text-7xl md:text-8xl font-black mb-6 bg-gradient-to-r from-blue-600 via-violet-600 to-cyan-600 bg-clip-text text-transparent animate-pulse`}>
            Finova
          </h1>

          <p className={`text-3xl md:text-4xl font-bold mb-6 ${
            isDark ? 'text-slate-100' : 'text-slate-900'
          }`}>
            Maîtrisez votre budget avec l'IA
          </p>

          <p className={`text-xl md:text-2xl mb-12 max-w-2xl mx-auto leading-relaxed ${
            isDark ? 'text-slate-400' : 'text-slate-600'
          }`}>
            Analysez vos dépenses, obtenez des insights intelligents et planifiez votre avenir financier avec notre chatbot IA alimenté par Gemini.
          </p>

          {/* CTA Button */}
          <div className="flex gap-4 justify-center mb-12 flex-col sm:flex-row">
            <button
              onClick={() => window.location.href = '/dashboard'}
              disabled={isHealthy === false}
              className={`group px-8 py-4 rounded-xl font-bold transition-all duration-300 flex items-center justify-center gap-2 text-lg ${
                isHealthy === false
                  ? 'opacity-50 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-violet-600 hover:shadow-2xl hover:shadow-blue-500/50 text-white hover:scale-105 active:scale-95'
              }`}
            >
              Commencer Maintenant
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

          {/* Status indicator */}
          {isHealthy && (
            <p className={`text-sm font-medium flex items-center justify-center gap-2 ${
              isDark ? 'text-green-400' : 'text-green-600'
            }`}>
              <span className={`h-2.5 w-2.5 rounded-full animate-pulse ${
                isDark ? 'bg-green-400' : 'bg-green-600'
              }`} />
              Service actif et opérationnel
            </p>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className={`relative py-24 px-4 transition-colors duration-300 ${
        isDark
          ? 'bg-gradient-to-b from-slate-950 to-slate-900'
          : 'bg-gradient-to-b from-slate-100 to-white'
      }`}>
        <div className="max-w-6xl mx-auto">
          <h2 className={`text-5xl font-bold text-center mb-16 ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            Fonctionnalités
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className={`group bg-gradient-to-br rounded-2xl p-8 transition-all duration-300 border ${
              isDark
                ? 'from-slate-800 to-slate-900 border-slate-700 hover:border-blue-500 hover:shadow-xl hover:shadow-blue-500/20'
                : 'from-white to-slate-50 border-slate-200 hover:border-blue-400 hover:shadow-xl hover:shadow-blue-400/20'
            }`}>
              <div className="mb-4 p-3 bg-gradient-to-r from-blue-600 to-blue-500 rounded-lg w-fit group-hover:scale-110 transition-transform">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
              <h3 className={`text-2xl font-bold mb-3 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                Analyse Intelligente
              </h3>
              <p className={isDark ? 'text-slate-400' : 'text-slate-600'}>
                Upload CSV ou Excel, obtenez des insights complets sur vos dépenses en quelques secondes.
              </p>
            </div>

            {/* Feature 2 */}
            <div className={`group bg-gradient-to-br rounded-2xl p-8 transition-all duration-300 border ${
              isDark
                ? 'from-slate-800 to-slate-900 border-slate-700 hover:border-violet-500 hover:shadow-xl hover:shadow-violet-500/20'
                : 'from-white to-slate-50 border-slate-200 hover:border-violet-400 hover:shadow-xl hover:shadow-violet-400/20'
            }`}>
              <div className="mb-4 p-3 bg-gradient-to-r from-violet-600 to-violet-500 rounded-lg w-fit group-hover:scale-110 transition-transform">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <h3 className={`text-2xl font-bold mb-3 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                Chatbot IA
              </h3>
              <p className={isDark ? 'text-slate-400' : 'text-slate-600'}>
                Discutez avec notre assistant intelligent pour des conseils budgétaires et des recommandations.
              </p>
            </div>

            {/* Feature 3 */}
            <div className={`group bg-gradient-to-br rounded-2xl p-8 transition-all duration-300 border ${
              isDark
                ? 'from-slate-800 to-slate-900 border-slate-700 hover:border-cyan-500 hover:shadow-xl hover:shadow-cyan-500/20'
                : 'from-white to-slate-50 border-slate-200 hover:border-cyan-400 hover:shadow-xl hover:shadow-cyan-400/20'
            }`}>
              <div className="mb-4 p-3 bg-gradient-to-r from-cyan-600 to-cyan-500 rounded-lg w-fit group-hover:scale-110 transition-transform">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
              <h3 className={`text-2xl font-bold mb-3 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                ML & Prédictions
              </h3>
              <p className={isDark ? 'text-slate-400' : 'text-slate-600'}>
                Détection d'anomalies et prédictions intelligentes pour anticiper vos patterns de dépenses.
              </p>
            </div>

            {/* Feature 4 */}
            <div className={`group bg-gradient-to-br rounded-2xl p-8 transition-all duration-300 border ${
              isDark
                ? 'from-slate-800 to-slate-900 border-slate-700 hover:border-green-500 hover:shadow-xl hover:shadow-green-500/20'
                : 'from-white to-slate-50 border-slate-200 hover:border-green-400 hover:shadow-xl hover:shadow-green-400/20'
            }`}>
              <div className="mb-4 p-3 bg-gradient-to-r from-green-600 to-green-500 rounded-lg w-fit group-hover:scale-110 transition-transform">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <h3 className={`text-2xl font-bold mb-3 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                Dashboards Dynamiques
              </h3>
              <p className={isDark ? 'text-slate-400' : 'text-slate-600'}>
                Visualisez vos données avec des graphiques interactifs et des filtres avancés.
              </p>
            </div>

            {/* Feature 5 */}
            <div className={`group bg-gradient-to-br rounded-2xl p-8 transition-all duration-300 border ${
              isDark
                ? 'from-slate-800 to-slate-900 border-slate-700 hover:border-amber-500 hover:shadow-xl hover:shadow-amber-500/20'
                : 'from-white to-slate-50 border-slate-200 hover:border-amber-400 hover:shadow-xl hover:shadow-amber-400/20'
            }`}>
              <div className="mb-4 p-3 bg-gradient-to-r from-amber-600 to-amber-500 rounded-lg w-fit group-hover:scale-110 transition-transform">
                <Navigation className="h-6 w-6 text-white" />
              </div>
              <h3 className={`text-2xl font-bold mb-3 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                Interface Épurée
              </h3>
              <p className={isDark ? 'text-slate-400' : 'text-slate-600'}>
                Design moderne et performant pour une navigation fluide et agréable.
              </p>
            </div>

            {/* Feature 6 */}
            <div className={`group bg-gradient-to-br rounded-2xl p-8 transition-all duration-300 border ${
              isDark
                ? 'from-slate-800 to-slate-900 border-slate-700 hover:border-pink-500 hover:shadow-xl hover:shadow-pink-500/20'
                : 'from-white to-slate-50 border-slate-200 hover:border-pink-400 hover:shadow-xl hover:shadow-pink-400/20'
            }`}>
              <div className="mb-4 p-3 bg-gradient-to-r from-pink-600 to-pink-500 rounded-lg w-fit group-hover:scale-110 transition-transform">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <h3 className={`text-2xl font-bold mb-3 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                Mode Nuit
              </h3>
              <p className={isDark ? 'text-slate-400' : 'text-slate-600'}>
                Toggle facile entre mode clair et sombre pour une expérience confortable.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={`border-t transition-colors duration-300 py-8 px-4 text-center ${
        isDark
          ? 'border-slate-800 bg-slate-950 text-slate-400'
          : 'border-slate-200 bg-white text-slate-600'
      }`}>
        <p>Finova © 2026 • Plateforme de Gestion Budgétaire Intelligente</p>
      </footer>
    </div>
  );
}

