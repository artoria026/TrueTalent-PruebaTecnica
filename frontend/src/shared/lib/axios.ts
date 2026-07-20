import axios, { type AxiosInstance } from 'axios';

// Falls back to the page's own origin so this works on any host/port.
const DEFAULT_API_BASE_URL = `${window.location.origin}/api/v1`;

const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL;

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
