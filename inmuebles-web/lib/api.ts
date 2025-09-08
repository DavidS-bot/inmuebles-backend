import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

export function setAuthToken(token?: string) {
  if (token) api.defaults.headers.common.Authorization = `Bearer ${token}`;
  else delete api.defaults.headers.common.Authorization;
}

// Request interceptor to log requests
api.interceptors.request.use(
  (config) => {
    console.log(`🔵 ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error("🔴 Request error:", error);
    return Promise.reject(error);
  }
);

// Response interceptor for auth and error handling
api.interceptors.response.use(
  (response) => {
    console.log(`🟢 ${response.status} ${response.config.url}`);
    return response;
  },
  (err) => {
    console.error("🔴 Response error:", {
      message: err.message,
      code: err.code,
      status: err.response?.status,
      url: err.config?.url,
      method: err.config?.method
    });

    if (err?.response?.status === 401 && typeof window !== "undefined") {
      // borra token y vete al login
      localStorage.removeItem("auth_token");
      document.cookie = "t=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax";
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;
