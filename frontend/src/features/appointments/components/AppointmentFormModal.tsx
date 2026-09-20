import React, { useState, useEffect } from 'react';
import { Modal } from '../../../components/Modal';
import { Input } from '../../../components/Input';
import { Select } from '../../../components/Select';
import { Button } from '../../../components/Button';
import { createAppointment } from '../api/appointmentsApi';
import type { Service } from '../../services/api/servicesApi';
import { fetchServices } from '../../services/api/servicesApi';
import { ApiError } from '../../../api/httpClient';

interface AppointmentFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const AppointmentFormModal: React.FC<AppointmentFormModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [serviceId, setServiceId] = useState<number | ''>('');
  const [appointmentDate, setAppointmentDate] = useState('');
  const [appointmentTime, setAppointmentTime] = useState('');
  const [notes, setNotes] = useState('');

  const [services, setServices] = useState<Service[]>([]);
  const [isLoadingServices, setIsLoadingServices] = useState(false);

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsLoadingServices(true);
      fetchServices()
        .then((data) => {
          setServices(data);
          if (data.length > 0 && !serviceId) {
            setServiceId(data[0].id);
          }
        })
        .catch(() => {
          setApiError('Failed to load available salon services.');
        })
        .finally(() => setIsLoadingServices(false));

      // Set default date to today
      const today = new Date().toISOString().split('T')[0];
      setAppointmentDate(today);
      setAppointmentTime('10:00');
      setCustomerName('');
      setCustomerPhone('');
      setNotes('');
      setErrors({});
      setApiError(null);
    }
  }, [isOpen]);

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!customerName.trim()) errs.customer_name = 'Customer name is required.';
    if (!customerPhone.trim()) errs.customer_phone = 'Customer phone is required.';
    if (!serviceId) errs.service = 'Please select a salon service.';
    if (!appointmentDate) errs.appointment_date = 'Date is required.';
    if (!appointmentTime) errs.appointment_time = 'Time is required.';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      const formattedTime = appointmentTime.length === 5 ? `${appointmentTime}:00` : appointmentTime;

      await createAppointment({
        customer_name: customerName.trim(),
        customer_phone: customerPhone.trim(),
        service: Number(serviceId),
        appointment_date: appointmentDate,
        appointment_time: formattedTime,
        notes: notes.trim(),
      });

      onSuccess();
      onClose();
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 409) {
          setApiError('This time slot is already booked for this service. Please choose another time.');
        } else {
          setApiError(err.message);
        }
      } else {
        setApiError('An unexpected error occurred while booking the appointment.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const serviceOptions = [
    { value: '', label: '-- Select Salon Service --' },
    ...services.map((s) => ({
      value: s.id,
      label: `${s.name} (${s.duration_minutes} mins) - NPR ${s.price}`,
    })),
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Book New Salon Appointment">
      <form onSubmit={handleSubmit} noValidate>
        {apiError && (
          <div className="alert alert-danger mb-4 flex items-start">
            <span className="mr-2">⚠️</span>
            <div>{apiError}</div>
          </div>
        )}

        <Input
          label="Customer Name"
          value={customerName}
          onChange={(e) => setCustomerName(e.target.value)}
          placeholder="e.g. Ram Sharma"
          error={errors.customer_name}
          required
        />

        <Input
          label="Customer Phone Number"
          type="tel"
          value={customerPhone}
          onChange={(e) => setCustomerPhone(e.target.value)}
          placeholder="e.g. 9841000000"
          error={errors.customer_phone}
          required
        />

        <Select
          label="Salon Service"
          options={serviceOptions}
          value={serviceId}
          onChange={(e) => setServiceId(Number(e.target.value) || '')}
          error={errors.service}
          disabled={isLoadingServices}
          required
        />

        <div className="form-row">
          <Input
            label="Appointment Date"
            type="date"
            value={appointmentDate}
            onChange={(e) => setAppointmentDate(e.target.value)}
            error={errors.appointment_date}
            required
          />

          <Input
            label="Appointment Time"
            type="time"
            value={appointmentTime}
            onChange={(e) => setAppointmentTime(e.target.value)}
            error={errors.appointment_time}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Notes (Optional)</label>
          <textarea
            className="form-textarea"
            rows={3}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Special requests or haircut specifications..."
          />
        </div>

        <div className="form-actions mt-6">
          <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" isLoading={isSubmitting}>
            Book Appointment
          </Button>
        </div>
      </form>
    </Modal>
  );
};
