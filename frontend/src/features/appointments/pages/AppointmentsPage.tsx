import React, { useEffect, useState, useCallback } from 'react';
import type { Appointment, AppointmentStatusType } from '../api/appointmentsApi';
import {
  fetchAppointments,
  updateAppointmentStatus,
  deleteAppointment,
} from '../api/appointmentsApi';
import { AppointmentFormModal } from '../components/AppointmentFormModal';
import { StatusTransitionActions } from '../components/StatusTransitionActions';
import { Button } from '../../../components/Button';
import { Modal } from '../../../components/Modal';
import { StatusBadge } from '../../../components/StatusBadge';
import { LoadingState } from '../../../components/LoadingState';
import { EmptyState } from '../../../components/EmptyState';
import { ErrorState } from '../../../components/ErrorState';

export const AppointmentsPage: React.FC = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isBookModalOpen, setIsBookModalOpen] = useState(false);

  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const loadAppointments = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchAppointments(statusFilter);
      setAppointments(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load appointments.');
    } finally {
      setIsLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    loadAppointments();
  }, [loadAppointments]);

  const handleStatusTransition = async (id: number, newStatus: AppointmentStatusType) => {
    setUpdatingId(id);
    try {
      await updateAppointmentStatus(id, newStatus);
      loadAppointments();
    } catch (err: any) {
      alert(err.message || 'Failed to update appointment status.');
    } finally {
      setUpdatingId(null);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteId) return;
    setIsDeleting(true);
    try {
      await deleteAppointment(deleteId);
      setDeleteId(null);
      loadAppointments();
    } catch (err: any) {
      alert(err.message || 'Failed to delete appointment.');
    } finally {
      setIsDeleting(false);
    }
  };

  const filterTabs = [
    { key: 'ALL', label: 'All' },
    { key: 'PENDING', label: 'Pending' },
    { key: 'CONFIRMED', label: 'Confirmed' },
    { key: 'COMPLETED', label: 'Completed' },
    { key: 'CANCELLED', label: 'Cancelled' },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Appointment Bookings</h1>
          <p className="page-subtitle">Track, filter, and transition customer appointment statuses</p>
        </div>
        <Button variant="primary" onClick={() => setIsBookModalOpen(true)}>
          Book Appointment
        </Button>
      </div>

      <div className="filter-bar mb-6">
        <div className="filter-tabs">
          {filterTabs.map((tab) => (
            <button
              key={tab.key}
              className={`filter-tab ${statusFilter === tab.key ? 'active' : ''}`}
              onClick={() => setStatusFilter(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading && <LoadingState message="Loading appointments..." />}

      {!isLoading && error && <ErrorState message={error} onRetry={loadAppointments} />}

      {!isLoading && !error && appointments.length === 0 && (
        <EmptyState
          title="No appointments found"
          message={
            statusFilter === 'ALL'
              ? 'No appointments have been booked yet.'
              : `No appointments found with status ${statusFilter}.`
          }
          actionLabel="Book Appointment"
          onAction={() => setIsBookModalOpen(true)}
        />
      )}

      {!isLoading && !error && appointments.length > 0 && (
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Phone</th>
                <th>Service</th>
                <th>Date & Time</th>
                <th>Status</th>
                <th>Status Actions</th>
                <th>Delete</th>
              </tr>
            </thead>
            <tbody>
              {appointments.map((app) => (
                <tr key={app.id}>
                  <td>
                    <div className="font-semibold text-main">{app.customer_name}</div>
                    {app.notes && <div className="text-muted text-xs italic">"{app.notes}"</div>}
                  </td>
                  <td>{app.customer_phone}</td>
                  <td>
                    <div className="font-medium">{app.service?.name || 'Unknown Service'}</div>
                    <div className="text-muted text-xs">
                      NPR {app.service?.price} • {app.service?.duration_minutes}m
                    </div>
                  </td>
                  <td>
                    <div className="font-medium">{app.appointment_date}</div>
                    <div className="text-muted text-xs">{app.appointment_time}</div>
                  </td>
                  <td>
                    <StatusBadge status={app.status} label={app.status_label} />
                  </td>
                  <td>
                    <StatusTransitionActions
                      currentStatus={app.status}
                      onTransition={(target) => handleStatusTransition(app.id, target)}
                      isLoading={updatingId === app.id}
                    />
                  </td>
                  <td>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => setDeleteId(app.id)}
                      aria-label={`Delete appointment for ${app.customer_name}`}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <AppointmentFormModal
        isOpen={isBookModalOpen}
        onClose={() => setIsBookModalOpen(false)}
        onSuccess={loadAppointments}
      />

      <Modal
        isOpen={deleteId !== null}
        onClose={() => setDeleteId(null)}
        title="Confirm Appointment Deletion"
      >
        <p>Are you sure you want to cancel and delete this appointment booking?</p>
        <div className="form-actions mt-6">
          <Button variant="outline" onClick={() => setDeleteId(null)} disabled={isDeleting}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDeleteConfirm} isLoading={isDeleting}>
            Delete Appointment
          </Button>
        </div>
      </Modal>
    </div>
  );
};
