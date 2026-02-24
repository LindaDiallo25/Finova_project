import React from 'react';
import { Loader2 } from 'lucide-react';

export function LoadingSpinner({ message = 'Chargement...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader2 className="h-8 w-8 animate-spin text-primary mb-3" />
      <p className="text-foreground/70">{message}</p>
    </div>
  );
}
