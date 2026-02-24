import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { TrendingUp, Loader, AlertCircle } from 'lucide-react';

export function ExpensePredictions({ analysisId }) {
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [daysAhead, setDaysAhead] = useState(30);

  useEffect(() => {
    fetchPredictions();
  }, [analysisId, daysAhead]);

  const fetchPredictions = async () => {
    if (!analysisId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/ml/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysis_id: analysisId,
          days_ahead: daysAhead,
          by_category: true
        })
      });

      if (!response.ok) throw new Error('Erreur prédiction');
      
      const data = await response.json();
      setPredictions(data);
      
      // Sélectionner la première catégorie par défaut
      const categories = Object.keys(data.predictions || {});
      if (categories.length > 0 && !selectedCategory) {
        setSelectedCategory(categories[0]);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-card border border-border rounded-lg p-6 flex items-center justify-center gap-3">
        <Loader className="h-5 w-5 animate-spin text-primary" />
        <span className="text-foreground/60">Calcul des prédictions...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-card border border-red-500/30 rounded-lg p-6">
        <div className="flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-red-400" />
          <div>
            <p className="text-red-400 font-medium">Erreur de prédiction</p>
            <p className="text-sm text-red-400/70">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!predictions || !predictions.predictions || Object.keys(predictions.predictions).length === 0) {
    return (
      <div className="bg-card border border-border rounded-lg p-6">
        <p className="text-foreground/60">Pas assez de données pour prédire</p>
      </div>
    );
  }

  const categories = Object.keys(predictions.predictions).filter(k => Array.isArray(predictions.predictions[k]));
  const currentCategory = selectedCategory || categories[0];
  const chartData = predictions.predictions[currentCategory] || [];

  // Formatter les données pour le graphique
  const formattedData = chartData.map(item => ({
    date: item.date,
    predicted: parseFloat(item.predicted_amount.toFixed(2)),
    lower: parseFloat(item.lower_bound.toFixed(2)),
    upper: parseFloat(item.upper_bound.toFixed(2))
  }));

  // Calculs d'insights
  const avgPredicted = chartData.reduce((sum, item) => sum + item.predicted_amount, 0) / chartData.length;
  const totalPredicted = chartData.reduce((sum, item) => sum + item.predicted_amount, 0);
  const maxPredicted = Math.max(...chartData.map(item => item.predicted_amount));
  const minPredicted = Math.min(...chartData.map(item => item.predicted_amount));

  return (
    <div className="bg-card border border-border rounded-lg p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-primary" />
          Prédictions de Dépenses
        </h3>
        <div className="flex gap-2 items-center">
          <select
            value={daysAhead}
            onChange={(e) => setDaysAhead(parseInt(e.target.value))}
            className="bg-background border border-border rounded px-3 py-1 text-sm text-foreground"
          >
            <option value={7}>7 jours</option>
            <option value={14}>14 jours</option>
            <option value={30}>30 jours</option>
            <option value={60}>60 jours</option>
          </select>
        </div>
      </div>

      {/* Catégories Tabs */}
      <div className="flex gap-2 flex-wrap">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              currentCategory === cat
                ? 'bg-primary text-background'
                : 'bg-background border border-border hover:border-primary/50'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div className="bg-background/30 rounded-lg p-4">
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={formattedData}>
            <defs>
              <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="date" stroke="#999" tick={{ fontSize: 12 }} />
            <YAxis stroke="#999" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
              labelStyle={{ color: '#fff' }}
              formatter={(value) => `${value.toFixed(2)}€`}
            />
            <Area
              type="monotone"
              dataKey="predicted"
              stroke="#3b82f6"
              fill="url(#colorPredicted)"
              name="Prédiction"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="upper"
              stroke="none"
              fill="transparent"
              name="Limite sup."
            />
            <Area
              type="monotone"
              dataKey="lower"
              stroke="none"
              fill="transparent"
              name="Limite inf."
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Insights */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-background/50 border border-border rounded-lg p-4">
          <p className="text-sm text-foreground/60 mb-1">Total Prédit</p>
          <p className="text-2xl font-bold text-primary">{totalPredicted.toFixed(2)}€</p>
        </div>
        <div className="bg-background/50 border border-border rounded-lg p-4">
          <p className="text-sm text-foreground/60 mb-1">Moyenne/Jour</p>
          <p className="text-2xl font-bold text-secondary">{avgPredicted.toFixed(2)}€</p>
        </div>
        <div className="bg-background/50 border border-border rounded-lg p-4">
          <p className="text-sm text-foreground/60 mb-1">Pic Prédit</p>
          <p className="text-2xl font-bold text-amber-500">{maxPredicted.toFixed(2)}€</p>
        </div>
        <div className="bg-background/50 border border-border rounded-lg p-4">
          <p className="text-sm text-foreground/60 mb-1">Min Prédit</p>
          <p className="text-2xl font-bold text-emerald-500">{minPredicted.toFixed(2)}€</p>
        </div>
      </div>

      {/* Legend */}
      <p className="text-xs text-foreground/40">
        💡 Basé sur vos patterns historiques. Intervalle de confiance 80%.
      </p>
    </div>
  );
}
