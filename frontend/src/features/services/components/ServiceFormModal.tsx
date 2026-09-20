import React, { useState, useEffect } from 'react';
import { Modal } from '../../../components/Modal';
import { Input } from '../../../components/Input';
import { Button } from '../../../components/Button';
import type { Service } from '../api/servicesApi';
import { createService, updateService } from '../api/servicesApi';
import { ApiError } from '../../../api/httpClient';

interface ServiceFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  serviceToEdit?: Service | null;
}

export const ServiceFormModal: React.FC<ServiceFormModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  serviceToEdit,
}) => {
  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [durationMinutes, setDurationMinutes] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (serviceToEdit) {
      setName(serviceToEdit.name);
      setPrice(serviceToEdit.price);
      setDurationMinutes(String(serviceToEdit.duration_minutes));
    } else {
      setName('');
      setPrice('');
      setDurationMinutes('30');
    }
    setErrors({});
    setApiError(null);
  }, [serviceToEdit, isOpen]);

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!name.trim()) errs.name = 'Service name is required.';
    if (!price || parseFloat(price) <= 0) errs.price = 'Price must be greater than zero.';
    if (!durationMinutes || parseInt(durationMinutes, 10) <= 0) {
      errs.duration_minutes = 'Duration must be greater than zero.';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      if (serviceToEdit) {
        await updateService(serviceToEdit.id, {
          name: name.trim(),
          price: price,
          duration_minutes: parseInt(durationMinutes, 10),
        });
      } else {
        await createService({
          name: name.trim(),
          price: price,
          duration_minutes: parseInt(durationMinutes, 10),
        });
      }
      onSuccess();
      onClose();
    } catch (err) {
      if (err instanceof ApiError) {
        setApiError(err.message);
      } else {
        setApiError('An unexpected error occurred while saving the service.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={serviceToEdit ? 'Edit Service' : 'Add New Service'}
    >
      <form onSubmit={handleSubmit} noValidate>
        {apiError && <div className="alert alert-danger mb-4">{apiError}</div>}

        <Input
          label="Service Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Haircut, Facial, Coloring"
          error={errors.name}
          required
        />

        <Input
          label="Price (NPR)"
          type="number"
          step="0.01"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          placeholder="e.g. 500.00"
          error={errors.price}
          required
        />

        <Input
          label="Duration (Minutes)"
          type="number"
          value={durationMinutes}
          onChange={(e) => setDurationMinutes(e.target.value)}
          placeholder="e.g. 30"
          error={errors.duration_minutes}
          required
        />

        <div className="form-actions mt-6">
          <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" isLoading={isSubmitting}>
            {serviceToEdit ? 'Update Service' : 'Create Service'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
