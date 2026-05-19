export interface Article {
  id: number;
  slug: string;
  category: string;
  title: string;
  excerpt: string;
  body?: string;
  coverImage: string;
  author: Author;
  publishedAt: string;
  readTime: number;
  featured?: boolean;
  tags?: string[];
}

export interface Author {
  name: string;
  role: string;
  avatarInitial: string;
}

export interface Comment {
  id: number;
  author: string;
  avatarInitial: string;
  text: string;
  publishedAt: string;
}

export type Category =
  | 'Todos'
  | 'Música'
  | 'Moda'
  | 'Cinema'
  | 'Literatura'
  | 'Cultura Digital';

export type UserRole = 'user' | 'admin';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  avatarInitial: string;
  joinedAt: string;
  postsCount: number;
}

export interface BannedUser {
  id: number;
  userId: number;
  userName: string;
  userEmail: string;
  avatarInitial: string;
  reason: string;
  /** The specific message/comment that triggered the ban — displayed highlighted in the UI. */
  triggerMessage?: string;
  bannedAt: string;
  bannedBy: string;
}

export interface NewPost {
  title: string;
  excerpt: string;
  body: string;
  category: string;
  coverImage: string;
}
