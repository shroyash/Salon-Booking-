const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, data: any, message?: string) {
    let errorMessage = message;
    if (!errorMessage) {
      if (data?.detail) {
        errorMessage = data.detail;
      } else if (typeof data === 'object' && data !== null) {
        const firstKey = Object.keys(data)[0];
        const val = data[firstKey];
        if (Array.isArray(val) && val.length > 0) {
          errorMessage = `${firstKey}: ${val[0]}`;
        } else if (typeof val === 'string') {
          errorMessage = `${firstKey}: ${val}`;
        } else {
          errorMessage = `HTTP Error ${status}`;
        }
      } else {
        errorMessage = `HTTP Error ${status}`;
      }
    }

    super(errorMessage);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL.replace(/\/$/, '')}/${endpoint.replace(/^\//, '')}`;
  const headers = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...options.headers,
  };

  const response = await fetch(url, { ...options, headers });

  if (response.status === 204) {
    return {} as T;
  }

  let data: any = null;
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    throw new ApiError(response.status, data);
  }

  return data as T;
}
