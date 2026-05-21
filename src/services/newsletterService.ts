import api from './api';

const newsletterService = {
  subscribe: (email: string) =>
    api.post<{ detail: string }>('/api/v1/newsletter/subscribe/', { email }),

  unsubscribe: (token: string) =>
    api.post<{ detail: string }>('/api/v1/newsletter/unsubscribe/', { token }),
};

export default newsletterService;
