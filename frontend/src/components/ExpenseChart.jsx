import React from 'react';
import {
  LineChart, Line, AreaChart, Area,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';

export function ExpenseChart({ data }) {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className="bg-card border border-border rounded-lg p-8 text-center">
        <p className="text-foreground/50">Aucune donnée à afficher</p>
      </div>
    );
  }

  // Vérifier si les données sont déjà agrégées (ont category et amount directement)
  const isAggregated = data[0]?.category && data[0]?.amount !== undefined;
  
  const chartData = isAggregated 
    ? data 
    : data.reduce((acc, item) => {
        const existing = acc.find(d => d.category === item.category);
        if (existing) {
          existing.amount += parseFloat(item.amount || 0);
        } else {
          acc.push({
            category: item.category,
            amount: parseFloat(item.amount || 0)
          });
        }
        return acc;
      }, []);

  return (
    <div className="space-y-6">
      <div className="bg-card border border-border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Dépenses par Catégorie</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="category" stroke="#999" />
            <YAxis stroke="#999" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
              labelStyle={{ color: '#fff' }}
            />
            <Bar dataKey="amount" fill="#3b82f6" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-card border border-border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Tendance des Dépenses</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="category" stroke="#999" />
            <YAxis stroke="#999" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
              labelStyle={{ color: '#fff' }}
            />
            <Area type="monotone" dataKey="amount" fill="#3b82f6" stroke="#3b82f6" opacity={0.6} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
