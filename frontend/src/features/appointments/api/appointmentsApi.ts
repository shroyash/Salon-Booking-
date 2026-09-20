import { request } from '../../../api/httpClient';
import type { Service } from '../../services/api/servicesApi';

export type AppointmentStatusType = 'PENDING' | 'CONFIRMED' | 'COMPLETED' | 'CANCELLED';

export interface Appointment {
  id: number;
  customer_name: string;
  customer_phone: string;
  service: Service;
  appointment_date: string;
  appointment_time: string;
  notes: string;
  status: AppointmentStatusType;
  status_label: string;
  created_at: string;
  updated_at: string;
}

export interface CreateAppointmentInput {
  customer_name: string;
  customer_phone: string;
  service: number;
  appointment_date: string;
  appointment_time: string;
  notes?: string;
}

export function fetchAppointments(statusFilter?: string): Promise<Appointment[]> {
  const query = statusFilter && statusFilter !== 'ALL' ? `?status=${statusFilter}` : '';
  return request<Appointment[]>(`/appointments/${query}`);
}

export function createAppointment(data: CreateAppointmentInput): Promise<Appointment> {
  return request<Appointment>('/appointments/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function updateAppointmentStatus(id: number, status: AppointmentStatusType): Promise<Appointment> {
  return request<Appointment>(`/appointments/${id}/status/`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

export function deleteAppointment(id: number): Promise<void> {
  return request<void>(`/appointments/${id}/`, {
    method: 'DELETE',
  });
}
