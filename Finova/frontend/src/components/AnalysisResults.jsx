import React from 'react';
import { TrendingUp, AlertTriangle, Lightbulb } from 'lucide-react';

export function AnalysisResults({ analysis }) {
  if (!analysis) return null;

  const cfoAnalysis = analysis || {};
  const summary = cfoAnalysis.summary || {};
  const trends = cfoAnalysis.trends || {};
  const recommendations = cfoAnalysis.recommendations || {};

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <TrendingUp className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2">Résumé</h3>
            <p className="text-foreground/70">
              {summary.description || 'En attente de l\'analyse...'}
            </p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-card border border-border rounded-lg p-4">
          <p className="text-sm text-foreground/50 mb-1">Total des Dépenses</p>
          <p className="text-2xl font-bold text-primary">
            {cfoAnalysis.total_expenses?.toFixed(2)}€
          </p>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <p className="text-sm text-foreground/50 mb-1">Dépense Moyenne Quotidienne</p>
          <p className="text-2xl font-bold text-secondary">
            {cfoAnalysis.average_daily_expense?.toFixed(2)}€
          </p>
        </div>
      </div>

      {/* Trends */}
      {trends.main_observations && trends.main_observations.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            Tendances Identifiées
          </h3>
          <ul className="space-y-2">
            {trends.main_observations.map((observation, idx) => (
              <li key={idx} className="flex gap-2 text-foreground/70">
                <span className="text-primary">•</span>
                {observation}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.general_recommendations && recommendations.general_recommendations.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-secondary" />
            Recommandations
          </h3>
          <ul className="space-y-2">
            {recommendations.general_recommendations.map((rec, idx) => (
              <li key={idx} className="flex gap-2 text-foreground/70">
                <span className="text-secondary">✓</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Optimization Areas */}
      {recommendations.optimization_areas && recommendations.optimization_areas.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-500" />
            Domaines d'Optimisation
          </h3>
          <div className="space-y-3">
            {recommendations.optimization_areas.map((area, idx) => (
              <div key={idx} className="border-l-2 border-primary/30 pl-4 py-2">
                <p className="font-semibold text-foreground">{area.category}</p>
                <p className="text-sm text-foreground/70">{area.recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
