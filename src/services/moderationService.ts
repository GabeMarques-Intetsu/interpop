import api from './api';
import type { ApiUser } from './authService';

export interface ApiBan {
  id: string;
  user: ApiUser;
  banned_by: ApiUser;
  unbanned_by: ApiUser | null;
  reason: string;
  /** Specific message/content that triggered the ban — shown highlighted in UI. */
  trigger_message: string;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
  unbanned_at: string | null;
}

export interface BanPayload {
  user_id: string;
  reason: string;
  trigger_message?: string;
}

const moderationService = {
  listUsers: (params?: Record<string, string>) =>
    api.get<{ results: ApiUser[]; count: number }>('/api/auth/users/', { params }),

  listBans: (params?: Record<string, string>) =>
    api.get<{ results: ApiBan[]; count: number }>('/api/moderation/bans/', { params }),

  ban: (payload: BanPayload) =>
    api.post<ApiBan>('/api/moderation/bans/', payload),

  unban: (banId: string) =>
    api.delete(`/api/moderation/bans/${banId}/`),
};

export default moderationService;
