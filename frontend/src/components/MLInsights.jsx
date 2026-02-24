import React, { useState, useEffect } from 'react';
import { Loader, Zap, TrendingDown } from 'lucide-react';

export function MLInsights({ analysisId }) {
  const [recommendations, setRecommendations] = useState(null);
  const [patterns, setPatterns] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!analysisId) return;
    
    fetchInsights();
  }, [analysisId]);

  const fetchInsights = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch recommendations
      const recRes = await fetch(
        `http://localhost:8000/api/ml/budget-recommendations?analysis_id=${analysisId}&percentile=75`,
        { method: 'POST' }
      );
      if (recRes.ok) {
        const recData = await recRes.json();
        setRecommendations(recData);
      }

      // Fetch patterns
      const patRes = await fetch(
        `http://localhost:8000/api/ml/patterns?analysis_id=${analysisId}`,
        { method: 'POST' }
      );
      if (patRes.ok) {
        const patData = await patRes.json();
        setPatterns(patData);
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
        <span className="text-foreground/60">Analyse en cours...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-card border border-red-500/30 rounded-lg p-6">
        <p className="text-red-400 text-sm">Erreur: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Budget Recommendations */}
      {recommendations?.recommendations && (
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Zap className="h-5 w-5 text-amber-500" />
            Recommandations de Budget
          </h3>

          <div className="space-y-4">
            {Object.entries(recommendations.recommendations).map(([category, data]) => (
              <div key={category} className="bg-background/50 rounded-lg p-4 border border-border/50">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-foreground">{category}</h4>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-primary">{data.recommended_budget.toFixed(2)}€</p>
                    <p className="text-xs text-foreground/50">Recommandé (75e percentile)</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div>
                    <p className="text-foreground/60 text-xs">Moyenne</p>
                    <p className="font-semibold">{data.average_spent.toFixed(2)}€</p>
                  </div>
                  <div>
                    <p className="text-foreground/60 text-xs">Min</p>
                    <p className="font-semibold text-emerald-500">{data.min_spent.toFixed(2)}€</p>
                  </div>
                  <div>
                    <p className="text-foreground/60 text-xs">Max</p>
                    <p className="font-semibold text-red-500">{data.max_spent.toFixed(2)}€</p>
                  </div>
                </div>

                <p className="text-xs text-foreground/40 mt-2">
                  {data.total_transactions} transactions
                </p>
              </div>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-border bg-primary/5 rounded-lg p-3">
            <p className="text-sm text-foreground/70">
              <strong>Budget total recommandé:</strong> {recommendations.total_budget_recommended?.toFixed(2)}€
            </p>
            <p className="text-xs text-foreground/50 mt-1">
              Dépense actuelle: {recommendations.total_spent?.toFixed(2)}€
            </p>
          </div>
        </div>
      )}

      {/* Spending Patterns */}
      {patterns?.patterns && (
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingDown className="h-5 w-5 text-secondary" />
            Patterns de Dépenses
          </h3>

          <div className="space-y-4">
            {/* Spending Trend */}
            {patterns.patterns.spending_trend && (
              <div className="bg-background/50 rounded-lg p-4 border border-border/50">
                <h4 className="font-semibold mb-2">Tendance Générale</h4>
                <div className="flex items-center gap-4">
                  <div>
                    <p className="text-sm text-foreground/60">Direction</p>
                    <p className="text-lg font-bold capitalize">
                      {patterns.patterns.spending_trend.direction}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-foreground/60">Changement</p>
                    <p className={`text-lg font-bold ${
                      patterns.patterns.spending_trend.percentage_change >= 0
                        ? 'text-red-500'
                        : 'text-emerald-500'
                    }`}>
                      {patterns.patterns.spending_trend.percentage_change > 0 ? '+' : ''}
                      {patterns.patterns.spending_trend.percentage_change.toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Top Categories */}
            {patterns.patterns.top_categories && patterns.patterns.top_categories.length > 0 && (
              <div className="bg-background/50 rounded-lg p-4 border border-border/50">
                <h4 className="font-semibold mb-3">Top 5 Catégories</h4>
                <div className="space-y-2">
                  {patterns.patterns.top_categories.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between text-sm">
                      <span className="text-foreground/70">{idx + 1}. {item.category}</span>
                      <span className="font-semibold">{item.total.toFixed(2)}€</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Highest Spending Day */}
            {patterns.patterns.highest_spending_day && (
              <div className="bg-background/50 rounded-lg p-4 border border-border/50">
                <h4 className="font-semibold mb-2">Jour avec Plus de Dépenses</h4>
                <div className="flex items-center justify-between">
                  <p className="text-foreground/70">{patterns.patterns.highest_spending_day.date}</p>
                  <p className="text-lg font-bold text-primary">
                    {patterns.patterns.highest_spending_day.amount.toFixed(2)}€
                  </p>
                </div>
              </div>
            )}

            {/* Category Volatility */}
            {patterns.patterns.category_volatility && (
              <div className="bg-background/50 rounded-lg p-4 border border-border/50">
                <h4 className="font-semibold mb-3">Volatilité par Catégorie</h4>
                <div className="space-y-2">
                  {Object.entries(patterns.patterns.category_volatility)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, 5)
                    .map(([category, volatility]) => (
                      <div key={category} className="flex items-center justify-between text-sm">
                        <span className="text-foreground/70">{category}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-1.5 bg-border rounded-full">
                            <div
                              className="h-full bg-amber-500 rounded-full"
                              style={{ width: `${Math.min(volatility * 100, 100)}%` }}
                            />
                          </div>
                          <span className="text-xs text-foreground/50 w-8">
                            {(volatility * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>

          <p className="text-xs text-foreground/40 mt-4">
            📊 Analyse sur {patterns.data_points} transactions du {patterns.date_range?.start} au {patterns.date_range?.end}
          </p>
        </div>
      )}
    </div>
  );
}
