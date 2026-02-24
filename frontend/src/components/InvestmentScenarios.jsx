import React from 'react';
import { TrendingUp, AlertTriangle, TrendingDown } from 'lucide-react';

const getRiskColor = (riskLevel) => {
  switch (riskLevel?.toLowerCase()) {
    case 'faible':
      return 'bg-green-500/10 text-green-400 border-green-500/30';
    case 'modéré':
      return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30';
    case 'élevé':
      return 'bg-red-500/10 text-red-400 border-red-500/30';
    default:
      return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
  }
};

const getRiskIcon = (riskLevel) => {
  switch (riskLevel?.toLowerCase()) {
    case 'faible':
      return <TrendingDown className="h-5 w-5" />;
    case 'modéré':
      return <AlertTriangle className="h-5 w-5" />;
    case 'élevé':
      return <TrendingUp className="h-5 w-5" />;
    default:
      return null;
  }
};

export function InvestmentScenarios({ scenarios, marketComparison }) {
  if (!scenarios || scenarios.length === 0) {
    return (
      <div className="bg-card border border-border rounded-lg p-8 text-center">
        <p className="text-foreground/50">En attente de scénarios d'investissement...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Market Comparison */}
      {marketComparison && (
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Comparaison Marché</h3>
          <div className="grid grid-cols-2 gap-4">
            {marketComparison.average_market_return && (
              <div className="p-4 bg-primary/5 border border-primary/20 rounded-lg">
                <p className="text-sm text-foreground/50 mb-1">Rendement Marché Moyen</p>
                <p className="text-2xl font-bold text-primary">
                  {marketComparison.average_market_return.toFixed(1)}%
                </p>
              </div>
            )}
            {marketComparison.inflation_rate && (
              <div className="p-4 bg-secondary/5 border border-secondary/20 rounded-lg">
                <p className="text-sm text-foreground/50 mb-1">Taux d'Inflation</p>
                <p className="text-2xl font-bold text-secondary">
                  {marketComparison.inflation_rate.toFixed(1)}%
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Scenarios */}
      <div className="grid gap-6">
        {scenarios.map((scenario, idx) => (
          <div key={idx} className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-colors">
            <div className="mb-4">
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-xl font-bold">{scenario.title}</h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium border flex items-center gap-2 ${getRiskColor(scenario.risk_level)}`}>
                  {getRiskIcon(scenario.risk_level)}
                  {scenario.risk_level}
                </span>
              </div>
              <p className="text-foreground/70">{scenario.description}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="p-3 bg-primary/5 border border-primary/20 rounded-lg">
                <p className="text-xs text-foreground/50 mb-1">Rendement Attendu</p>
                <p className="text-lg font-bold text-primary">{scenario.expected_return}%</p>
              </div>
              <div className="p-3 bg-secondary/5 border border-secondary/20 rounded-lg">
                <p className="text-xs text-foreground/50 mb-1">Scénario</p>
                <p className="text-lg font-bold text-secondary">#{scenario.scenario_number}</p>
              </div>
            </div>

            {scenario.details && (
              <div className="text-sm text-foreground/60 space-y-1">
                {Object.entries(scenario.details).map(([key, value]) => (
                  <p key={key}>
                    <span className="text-foreground/40">{key}:</span> {JSON.stringify(value)}
                  </p>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
