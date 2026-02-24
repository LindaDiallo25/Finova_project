import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingDown, Loader } from 'lucide-react';

export function AnomalyDetection({ analysisId }) {
  const [anomalies, setAnomalies] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    fetchAnomalies();
  }, [analysisId]);

  const fetchAnomalies = async () => {
    if (!analysisId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/ml/anomalies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysis_id: analysisId,
          contamination: 0.1
        })
      });

      if (!response.ok) throw new Error('Erreur ML');
      
      const data = await response.json();
      setAnomalies(data);
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
        <span className="text-foreground/60">Analyse des anomalies...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-card border border-red-500/30 rounded-lg p-6">
        <p className="text-red-400">Erreur: {error}</p>
      </div>
    );
  }

  if (!anomalies || anomalies.anomalies?.length === 0) {
    return (
      <div className="bg-card border border-border rounded-lg p-6">
        <p className="text-foreground/60">✓ Aucune anomalie détectée - Dépenses normales</p>
      </div>
    );
  }

  const getSeverityColor = (severity) => {
    if (severity >= 0.8) return 'text-red-500';
    if (severity >= 0.5) return 'text-amber-500';
    return 'text-yellow-500';
  };

  const getSeverityBg = (severity) => {
    if (severity >= 0.8) return 'bg-red-500/10 border-red-500/30';
    if (severity >= 0.5) return 'bg-amber-500/10 border-amber-500/30';
    return 'bg-yellow-500/10 border-yellow-500/30';
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-amber-500" />
          Anomalies Détectées
        </h3>
        <span className="px-3 py-1 bg-amber-500/20 text-amber-400 rounded-full text-sm font-medium">
          {anomalies.anomaly_count} / {anomalies.total_transactions}
        </span>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {anomalies.anomalies.map((anomaly, idx) => (
          <div
            key={idx}
            className={`border rounded-lg p-4 cursor-pointer transition-colors ${getSeverityBg(anomaly.severity)}`}
            onClick={() => setExpanded(expanded === idx ? null : idx)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <div className={`h-3 w-3 rounded-full ${getSeverityColor(anomaly.severity)}`} />
                  <div>
                    <p className="font-semibold">{anomaly.category}</p>
                    <p className="text-sm text-foreground/60">{anomaly.date}</p>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <p className="font-bold text-lg">{anomaly.amount.toFixed(2)}€</p>
                <p className={`text-sm font-medium ${getSeverityColor(anomaly.severity)}`}>
                  +{anomaly.deviation_percent.toFixed(1)}%
                </p>
              </div>
            </div>

            {expanded === idx && (
              <div className="mt-4 pt-4 border-t border-border/40 space-y-2 text-sm">
                <p className="text-foreground/70">
                  <strong>Raison:</strong> {anomaly.reason}
                </p>
                <p className="text-foreground/70">
                  <strong>Moyenne catégorie:</strong> {anomaly.category_average.toFixed(2)}€
                </p>
                <p className="text-foreground/70">
                  <strong>Description:</strong> {anomaly.description}
                </p>
                <div className="mt-3 flex gap-2">
                  <div className="flex-1 bg-background/50 rounded px-3 py-2">
                    <p className="text-xs text-foreground/50">Sévérité</p>
                    <div className="w-full bg-border rounded-full h-1.5 mt-1">
                      <div
                        className={`h-full rounded-full ${getSeverityColor(anomaly.severity).replace('text-', 'bg-')}`}
                        style={{ width: `${anomaly.severity * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <p className="text-xs text-foreground/40 mt-4">
        {anomalies.anomaly_percentage.toFixed(1)}% des transactions sont anormales
      </p>
    </div>
  );
}
