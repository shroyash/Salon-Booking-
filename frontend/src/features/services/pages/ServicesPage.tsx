import React, { useEffect, useState, useCallback } from 'react';
import type { Service } from '../api/servicesApi';
import { fetchServices, deleteService } from '../api/servicesApi';
import { ServiceFormModal } from '../components/ServiceFormModal';
import { Button } from '../../../components/Button';
import { Modal } from '../../../components/Modal';
import { LoadingState } from '../../../components/LoadingState';
import { EmptyState } from '../../../components/EmptyState';
import { ErrorState } from '../../../components/ErrorState';

export const ServicesPage: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [serviceToEdit, setServiceToEdit] = useState<Service | null>(null);

  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const loadServices = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchServices();
      setServices(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load services.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadServices();
  }, [loadServices]);

  const handleOpenAdd = () => {
    setServiceToEdit(null);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (service: Service) => {
    setServiceToEdit(service);
    setIsModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteId) return;
    setIsDeleting(true);
    try {
      await deleteService(deleteId);
      setDeleteId(null);
      loadServices();
    } catch (err: any) {
      alert(err.message || 'Failed to delete service.');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Salon Service Offerings</h1>
          <p className="page-subtitle">Manage service pricing and duration for appointment bookings</p>
        </div>
        <Button variant="primary" onClick={handleOpenAdd}>
          Add Service
        </Button>
      </div>

      {isLoading && <LoadingState message="Loading salon services..." />}

      {!isLoading && error && <ErrorState message={error} onRetry={loadServices} />}

      {!isLoading && !error && services.length === 0 && (
        <EmptyState
          title="No services created"
          message="Create your first salon service (e.g. Haircut, Facial) to start accepting customer appointments."
          actionLabel="Add Service"
          onAction={handleOpenAdd}
        />
      )}

      {!isLoading && !error && services.length > 0 && (
        <div className="services-grid">
          {services.map((service) => (
            <div key={service.id} className="service-card">
              <div className="service-card-header">
                <h3 className="service-name">{service.name}</h3>
                <span className="service-price">NPR {service.price}</span>
              </div>
              <div className="service-card-body">
                <span className="service-duration">{service.duration_minutes} min</span>
              </div>
              <div className="service-card-actions">
                <Button variant="outline" size="sm" onClick={() => handleOpenEdit(service)}>
                  Edit
                </Button>
                <Button variant="danger" size="sm" onClick={() => setDeleteId(service.id)}>
                  Delete
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <ServiceFormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={loadServices}
        serviceToEdit={serviceToEdit}
      />

      <Modal
        isOpen={deleteId !== null}
        onClose={() => setDeleteId(null)}
        title="Confirm Service Deletion"
      >
        <p>Are you sure you want to delete this service? If active appointments exist, it will be safely soft-deleted.</p>
        <div className="form-actions mt-6">
          <Button variant="outline" onClick={() => setDeleteId(null)} disabled={isDeleting}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDeleteConfirm} isLoading={isDeleting}>
            Delete Service
          </Button>
        </div>
      </Modal>
    </div>
  );
};
