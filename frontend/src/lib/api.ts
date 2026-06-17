import axios from "axios";
import { getToken, clearToken } from "./auth";

const api = axios.create({
  baseURL: "",  // Use relative URLs — Next.js rewrites /api/* -> http://localhost:8000/api/*
  timeout: 30_000,
  withCredentials: false,
});

// Attach JWT to every request
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle expired tokens globally
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      clearToken();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export default api;
