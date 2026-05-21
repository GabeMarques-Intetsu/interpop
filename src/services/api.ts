/**
 * Axios instance shared by every service module.
 *
 * Security design:
 *  - Credentials (JWT httpOnly cookies) are sent on every request.
 *  - CSRF cookie is read automatically by axios (xsrfCookieName) and forwarded
 *    as a header (xsrfHeaderName) — matches Django's CsrfViewMiddleware.
 *  - On 401 the interceptor calls /api/v1/auth/refresh/ once, then retries.
 *    A second 401 triggers a forced logout so stale state never persists.
 */
import axios, {
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from 'axios';

export const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true, // send httpOnly JWT cookies
  xsrfCookieName: 'csrftoken', // Django CSRF cookie name
  xsrfHeaderName: 'X-CSRFToken', // Django CSRF header name
  headers: { 'Content-Type': 'application/json' },
});

// ── Token refresh interceptor ──────────────────────────────────────────────

let refreshing: Promise<void> | null = null;

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original: InternalAxiosRequestConfig & { _retry?: boolean } =
      error.config ?? {};

    // O próprio refresh NÃO passa pelo fluxo de retry — senão entra em
    // deadlock: o interceptor faz `await refreshing` enquanto está dentro
    // do promise `refreshing`, e a Promise nunca resolve. Sintoma observado:
    // me() pendurada para sempre, AuthContext.isLoading = true eterno,
    // /perfil travado em "Carregando…" até o usuário ir manualmente em
    // /login. Rejeita o erro imediatamente — o .catch() da chain de refresh
    // (abaixo) faz o dispatch do auth:logout e propaga a rejeição.
    const isRefreshRequest = original.url?.includes('/api/v1/auth/refresh/');

    if (error.response?.status !== 401 || original._retry || isRefreshRequest) {
      return Promise.reject(error);
    }

    original._retry = true;

    if (!refreshing) {
      refreshing = api
        .post('/api/v1/auth/refresh/')
        .then(() => {
          refreshing = null;
        })
        .catch(() => {
          refreshing = null;
          // Broadcast a logout event so AuthContext can clean up
          window.dispatchEvent(new CustomEvent('auth:logout'));
          return Promise.reject(error);
        });
    }

    await refreshing;
    return api(original as AxiosRequestConfig);
  },
);

export default api;
