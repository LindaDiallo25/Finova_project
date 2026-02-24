import React, { useState, useMemo } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { TrendingUp, Calendar, Wallet, X } from 'lucide-react';

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

export function DynamicDashboard({ expenses, context }) {
  // États des filtres
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [minAmount, setMinAmount] = useState('');
  const [maxAmount, setMaxAmount] = useState('');

  // Appliquer les filtres
  const filteredExpenses = useMemo(() => {
    let filtered = expenses;

    // Filtre par catégories
    if (selectedCategories.length > 0) {
      filtered = filtered.filter(exp => selectedCategories.includes(exp.category));
    }

    // Filtre par date
    if (dateRange.start) {
      filtered = filtered.filter(exp => exp.date >= dateRange.start);
    }
    if (dateRange.end) {
      filtered = filtered.filter(exp => exp.date <= dateRange.end);
    }

    // Filtre par montant
    if (minAmount) {
      filtered = filtered.filter(exp => exp.amount >= parseFloat(minAmount));
    }
    if (maxAmount) {
      filtered = filtered.filter(exp => exp.amount <= parseFloat(maxAmount));
    }

    return filtered;
  }, [expenses, selectedCategories, dateRange, minAmount, maxAmount]);

  // Récalculer les données avec les filtres appliqués
  const dashboardData = useMemo(() => {
    if (!filteredExpenses || filteredExpenses.length === 0) return null;

    // 1. Dépenses par catégorie
    const byCategory = {};
    filteredExpenses.forEach(exp => {
      byCategory[exp.category] = (byCategory[exp.category] || 0) + exp.amount;
    });

    const categoryData = Object.entries(byCategory).map(([cat, amount]) => ({
      name: cat,
      value: parseFloat(amount.toFixed(2)),
      percentage: ((amount / Object.values(byCategory).reduce((a, b) => a + b, 0)) * 100).toFixed(1)
    })).sort((a, b) => b.value - a.value);

    // 2. Timeline des dépenses par jour
    const byDate = {};
    filteredExpenses.forEach(exp => {
      byDate[exp.date] = (byDate[exp.date] || 0) + exp.amount;
    });

    const timelineData = Object.entries(byDate)
      .sort(([dateA], [dateB]) => dateA.localeCompare(dateB))
      .map(([date, amount]) => ({
        date,
        amount: parseFloat(amount.toFixed(2))
      }));

    // 3. Top 5 catégories
    const topCategories = categoryData.slice(0, 5);

    // 4. Distribution pie chart
    const pieData = categoryData.map(item => ({
      name: item.name,
      value: item.value
    }));

    // 5. Statistiques
    const totalFiltered = Object.values(byCategory).reduce((a, b) => a + b, 0);
    const stats = {
      totalExpenses: totalFiltered,
      averageDaily: filteredExpenses.length > 0 ? totalFiltered / new Set(filteredExpenses.map(e => e.date)).size : 0,
      topCategory: categoryData[0]?.name || 'N/A',
      topAmount: categoryData[0]?.value || 0,
      expenseCount: filteredExpenses.length
    };

    return {
      categoryData,
      timelineData,
      topCategories,
      pieData,
      stats
    };
  }, [filteredExpenses]);

  // Récupérer toutes les catégories uniques
  const allCategories = useMemo(() => {
    const cats = new Set(expenses.map(e => e.category));
    return Array.from(cats).sort();
  }, [expenses]);

  // Récupérer la plage de dates
  const dates = useMemo(() => {
    const sortedDates = expenses.map(e => e.date).sort();
    return {
      min: sortedDates[0] || '',
      max: sortedDates[sortedDates.length - 1] || ''
    };
  }, [expenses]);

  const handleCategoryToggle = (category) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const handleReset = () => {
    setSelectedCategories([]);
    setDateRange({ start: '', end: '' });
    setMinAmount('');
    setMaxAmount('');
  };

  const hasFiltersApplied = selectedCategories.length > 0 || dateRange.start || dateRange.end || minAmount || maxAmount;

  if (!dashboardData) {
    return (
      <div className="bg-card border border-border rounded-lg p-8 text-center">
        <p className="text-foreground/50">Aucune donnée à afficher</p>
      </div>
    );
  }

  const { categoryData, timelineData, topCategories, pieData, stats } = dashboardData;

  return (
    <div className="space-y-6">
      {/* Filters Section */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Filtres</h3>
          {hasFiltersApplied && (
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-3 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg text-sm transition-colors"
            >
              <X className="h-4 w-4" />
              Réinitialiser
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Categories Filter */}
          <div>
            <label className="text-sm font-medium text-foreground/70 block mb-2">
              Catégories ({selectedCategories.length}/{allCategories.length})
            </label>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {allCategories.map(cat => (
                <label key={cat} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedCategories.includes(cat)}
                    onChange={() => handleCategoryToggle(cat)}
                    className="w-4 h-4 rounded border-border bg-background cursor-pointer"
                  />
                  <span className="text-sm">{cat}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Date Range Filter */}
          <div>
            <label className="text-sm font-medium text-foreground/70 block mb-2">Date de début</label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
              min={dates.min}
              max={dates.max}
              className="w-full bg-background border border-border rounded-lg px-3 py-2 text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-foreground/70 block mb-2">Date de fin</label>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
              min={dates.min}
              max={dates.max}
              className="w-full bg-background border border-border rounded-lg px-3 py-2 text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Amount Range Filter */}
          <div className="flex gap-2">
            <div className="flex-1">
              <label className="text-sm font-medium text-foreground/70 block mb-2">Min (€)</label>
              <input
                type="number"
                value={minAmount}
                onChange={(e) => setMinAmount(e.target.value)}
                placeholder="0"
                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div className="flex-1">
              <label className="text-sm font-medium text-foreground/70 block mb-2">Max (€)</label>
              <input
                type="number"
                value={maxAmount}
                onChange={(e) => setMaxAmount(e.target.value)}
                placeholder="∞"
                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>
        </div>

        {hasFiltersApplied && (
          <p className="text-sm text-foreground/50 mt-4">
            Affichage de {filteredExpenses.length}/{expenses.length} dépenses
          </p>
        )}
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-foreground/50 mb-1">Total Dépenses</p>
              <p className="text-2xl font-bold text-primary">{stats.totalExpenses.toFixed(2)}€</p>
            </div>
            <Wallet className="h-8 w-8 text-primary/30" />
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-foreground/50 mb-1">Moyenne/Jour</p>
              <p className="text-2xl font-bold text-secondary">{stats.averageDaily.toFixed(2)}€</p>
            </div>
            <Calendar className="h-8 w-8 text-secondary/30" />
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-foreground/50 mb-1">Top Catégorie</p>
              <p className="text-2xl font-bold text-amber-500">{stats.topCategory}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-amber-500/30" />
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-foreground/50 mb-1">Transactions</p>
              <p className="text-2xl font-bold text-emerald-500">{stats.expenseCount}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-emerald-500/30" />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart - Top Categories */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Top 5 Catégories</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topCategories}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#999" angle={-45} textAnchor="end" height={80} />
              <YAxis stroke="#999" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                labelStyle={{ color: '#fff' }}
              />
              <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart - Distribution */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Distribution par Catégorie</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => {
                  const percentage = ((value / stats.totalExpenses) * 100).toFixed(1);
                  return `${name}: ${percentage}%`;
                }}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                labelStyle={{ color: '#fff' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Timeline Chart */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Tendance Quotidienne</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={timelineData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="date" stroke="#999" />
            <YAxis stroke="#999" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
              labelStyle={{ color: '#fff' }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="amount"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ fill: '#3b82f6', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Détails par Catégorie */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Détails par Catégorie</h3>
        <div className="space-y-2">
          {categoryData.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between py-2 border-b border-border last:border-b-0">
              <div className="flex items-center gap-3">
                <div
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                />
                <span className="font-medium">{item.name}</span>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-primary font-bold">{item.value.toFixed(2)}€</span>
                <span className="text-foreground/50 text-sm">{item.percentage}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
