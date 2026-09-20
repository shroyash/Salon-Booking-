import { request } from '../../../api/httpClient';

export interface Service {
  id: number;
  name: string;
  price: string;
  duration_minutes: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateServiceInput {
  name: string;
  price: string;
  duration_minutes: number;
}

export interface UpdateServiceInput {
  name: string;
  price: string;
  duration_minutes: number;
  is_active?: boolean;
}

export function fetchServices(): Promise<Service[]> {
  return request<Service[]>('/services/');
}

export function createService(data: CreateServiceInput): Promise<Service> {
  return request<Service>('/services/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function updateService(id: number, data: UpdateServiceInput): Promise<Service> {
  return request<Service>(`/services/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export function deleteService(id: number): Promise<void> {
  return request<void>(`/services/${id}/`, {
    method: 'DELETE',
  });
}
