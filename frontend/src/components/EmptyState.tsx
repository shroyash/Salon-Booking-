import React from 'react';
import { Button } from './Button';

interface EmptyStateProps {
  title?: string;
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No records found',
  message = 'No appointments found matching your criteria. for this',
  actionLabel,
  onAction,
}) => {
  return (
    <div className="state-container empty-state">
      <h3 className="empty-title">{title}</h3>
      <p className="state-message">{message}</p>
      {actionLabel && onAction && (
        <Button variant="primary" onClick={onAction} className="mt-4">
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
