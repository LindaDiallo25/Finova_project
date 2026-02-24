import React from 'react';
import { useDropZone } from '../hooks/useDropZone';
import { Upload, AlertCircle } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export function FileUploader({ onFileSelect, isLoading }) {
  const { isDragActive, getRootProps, getInputProps } = useDropZone(onFileSelect);
  const { isDark } = useTheme();

  return (
    <div className="w-full space-y-4">
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all
          ${isLoading ? 'opacity-50 pointer-events-none' : ''}
          ${
            isDragActive
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
              : isDark 
                ? 'border-slate-700 hover:border-blue-500/50'
                : 'border-slate-300 hover:border-blue-500/50'
          }`}
      >
        <input {...getInputProps()} disabled={isLoading} />
        <div className="space-y-2">
          <div className="flex justify-center">
            <div className={`transition-transform duration-300 ${
              isLoading ? 'animate-pulse' : isDragActive ? 'scale-110' : ''
            }`}>
              <Upload className={`h-12 w-12 ${
                isDragActive 
                  ? 'text-blue-600 dark:text-blue-400' 
                  : isDark
                    ? 'text-slate-500'
                    : 'text-slate-400'
              }`} />
            </div>
          </div>
          <p className={`text-sm font-medium transition-colors ${
            isDark ? 'text-slate-300' : 'text-slate-700'
          }`}>
            {isLoading ? 'Traitement en cours...' : isDragActive ? 'Déposer les fichiers ici' : 'Glissez-déposez vos fichiers'}
          </p>
          {!isLoading && (
            <p className={`text-xs transition-colors ${
              isDark ? 'text-slate-500' : 'text-slate-500'
            }`}>
              Ou cliquez pour parcourir (CSV, Excel)
            </p>
          )}
        </div>
      </div>
      
      {/* Loading spinner pendant le traitement */}
      {isLoading && (
        <div className={`flex items-center justify-center gap-3 p-4 rounded-lg ${
          isDark 
            ? 'bg-blue-950/30 border border-blue-900' 
            : 'bg-blue-50 border border-blue-200'
        }`}>
          <div className="flex gap-1">
            <div className={`h-2 w-2 rounded-full animate-bounce ${
              isDark ? 'bg-blue-400' : 'bg-blue-600'
            }`} style={{animationDelay: '0s'}} />
            <div className={`h-2 w-2 rounded-full animate-bounce ${
              isDark ? 'bg-blue-400' : 'bg-blue-600'
            }`} style={{animationDelay: '0.15s'}} />
            <div className={`h-2 w-2 rounded-full animate-bounce ${
              isDark ? 'bg-blue-400' : 'bg-blue-600'
            }`} style={{animationDelay: '0.3s'}} />
          </div>
          <span className={`text-sm font-medium ${
            isDark ? 'text-blue-300' : 'text-blue-700'
          }`}>
            Analyse en cours...
          </span>
        </div>
      )}
      
      {!isLoading && (
        <p className={`text-xs flex items-center gap-1 ${
          isDark ? 'text-slate-500' : 'text-slate-600'
        }`}>
          <AlertCircle className="h-3 w-3" />
          Fichiers acceptés: .csv, .xlsx, .xls
        </p>
      )}
    </div>
  );
}
