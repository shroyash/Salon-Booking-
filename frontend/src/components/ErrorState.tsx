import React from 'react';
import { Button } from './Button';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  message = 'Failed to load appointments.',
  onRetry,
}) => {
  return (
    <div className="state-container error-state">
      <h3 className="error-title">Something went wrong</h3>
      <p className="state-message text-danger">{message}</p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry} className="mt-4">
          Retry
        </Button>
      )}
    </div>
  );
};
