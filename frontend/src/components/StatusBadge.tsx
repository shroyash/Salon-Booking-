import React from 'react';
import type { AppointmentStatusType } from '../features/appointments/api/appointmentsApi';

interface StatusBadgeProps {
  status: AppointmentStatusType | string;
  label?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label }) => {
  const displayLabel = label || status;
  
  const statusStyles: Record<string, string> = {
    PENDING: 'badge-pending',
    CONFIRMED: 'badge-confirmed',
    COMPLETED: 'badge-completed',
    CANCELLED: 'badge-cancelled',
  };

  const badgeClass = statusStyles[status] || 'badge-default';

  return <span className={`badge ${badgeClass}`}>{displayLabel}</span>;
};
