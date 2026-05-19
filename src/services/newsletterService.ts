import api from './api';

const newsletterService = {
  subscribe: (email: string) =>
    api.post<{ detail: string }>('/api/newsletter/subscribe/', { email }),

  unsubscribe: (token: string) =>
    api.post<{ detail: string }>('/api/newsletter/unsubscribe/', { token }),
};

export default newsletterService;
