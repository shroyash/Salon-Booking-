import React from 'react';
import type { AppointmentStatusType } from '../api/appointmentsApi';
import { Button } from '../../../components/Button';

interface StatusTransitionActionsProps {
  currentStatus: AppointmentStatusType;
  onTransition: (targetStatus: AppointmentStatusType) => void;
  isLoading?: boolean;
}

export const StatusTransitionActions: React.FC<StatusTransitionActionsProps> = ({
  currentStatus,
  onTransition,
  isLoading = false,
}) => {
  if (currentStatus === 'PENDING') {
    return (
      <div className="status-action-buttons">
        <Button
          variant="success"
          size="sm"
          onClick={() => onTransition('CONFIRMED')}
          disabled={isLoading}
        >
          Confirm
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onTransition('CANCELLED')}
          disabled={isLoading}
        >
          Cancel
        </Button>
      </div>
    );
  }

  if (currentStatus === 'CONFIRMED') {
    return (
      <div className="status-action-buttons">
        <Button
          variant="primary"
          size="sm"
          onClick={() => onTransition('COMPLETED')}
          disabled={isLoading}
        >
          Complete
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onTransition('CANCELLED')}
          disabled={isLoading}
        >
          Cancel
        </Button>
      </div>
    );
  }

  return <span className="text-muted text-sm">No actions</span>;
};
