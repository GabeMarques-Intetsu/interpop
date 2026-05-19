import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { PageLayout } from '../components/layout/PageLayout';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { CommentItem } from '../components/ui/CommentItem';
import { useAuth } from '../contexts/AuthContext';
import articleService, { type ApiArticle } from '../services/articleService';
import commentService, { type ApiComment } from '../services/commentService';
import { renderArticleBody } from '../utils/renderArticleBody';
import './Article.css';

function readingTime(body: string): number {
  const words = body.trim().split(/\s+/).length;
  return Math.max(1, Math.ceil(words / 200));
}

function formatDate(iso: string): string {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit', month: 'long', year: 'numeric',
  }).format(new Date(iso));
}

/** Lista de plataformas para o bloco "Compartilhar". Cada uma traz ícone
 *  inline (currentColor → herda cor do botão, escala perfeito em qualquer
 *  densidade) e label. Mantém em sync com `handleShare()` via `key`. */
const SHARE_TARGETS = [
  {
    key:   'Twitter/X',
    label: 'Twitter/X',
    icon: (
      <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
      </svg>
    ),
  },
  {
    key:   'LinkedIn',
    label: 'LinkedIn',
    icon: (
      <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true">
        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.063 2.063 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0z"/>
      </svg>
    ),
  },
  {
    key:   'WhatsApp',
    label: 'WhatsApp',
    icon: (
      <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true">
        <path d="M.057 24l1.687-6.163a11.867 11.867 0 01-1.587-5.946C.157 5.335 5.493 0 12.05 0a11.817 11.817 0 018.413 3.488 11.824 11.824 0 013.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 01-5.688-1.448L.057 24zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884a9.86 9.86 0 001.51 5.26L3.673 18.78l1.984-.595zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.371-.025-.52-.075-.149-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/>
      </svg>
    ),
  },
  {
    key:   'Copiar link',
    label: 'Copiar link',
    icon: (
      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
      </svg>
    ),
  },
] as const;

export function Article() {
  const { slug }                = useParams<{ slug: string }>();
  const navigate                = useNavigate();
  const { currentUser }         = useAuth();

  const [article, setArticle]   = useState<ApiArticle | null>(null);
  const [loadError, setLoadError] = useState<string>('');
  const [comments, setComments] = useState<ApiComment[]>([]);
  const [totalComments, setTotalComments] = useState(0);
  const [loadingArticle, setLoadingArticle] = useState(true);
  const [commentText, setCommentText]     = useState('');
  const [submitting, setSubmitting]       = useState(false);
  const [progress, setProgress]           = useState(0);
  const viewedRef                         = useRef(false);

  // Reading progress bar
  useEffect(() => {
    const onScroll = () => {
      const el    = document.documentElement;
      const total = el.scrollHeight - el.clientHeight;
      setProgress(total > 0 ? (el.scrollTop / total) * 100 : 0);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Load article
  useEffect(() => {
    if (!slug) { navigate('/'); return; }
    setLoadingArticle(true);
    setLoadError('');
    articleService.get(slug)
      .then(r => setArticle(r.data))
      .catch((err: unknown) => {
        const e = err as {
          response?: { status?: number; data?: { detail?: string } };
          request?: unknown;
        };
        const status = e?.response?.status;
        const detail = e?.response?.data?.detail;
        if (status === 404) {
          setLoadError('Artigo não encontrado.');
        } else if (status) {
          setLoadError(detail ?? `Erro inesperado do servidor (HTTP ${status}).`);
        } else if (e?.request) {
          setLoadError('Não foi possível alcançar o servidor. Verifique se o backend está rodando.');
        } else {
          setLoadError('Erro inesperado ao carregar o artigo.');
        }
      })
      .finally(() => setLoadingArticle(false));
  }, [slug, navigate]);

  // Record view once
  useEffect(() => {
    if (article && !viewedRef.current) {
      viewedRef.current = true;
      articleService.recordView(article.slug).catch(() => {});
    }
  }, [article]);

  // Load comments
  useEffect(() => {
    if (!slug) return;
    commentService.list(slug)
      .then(r => {
        setComments(r.data.results);
        setTotalComments(r.data.count);
      })
      .catch(() => {});
  }, [slug]);

  const [commentError, setCommentError] = useState('');

  const handleSubmitComment = useCallback(async () => {
    if (!commentText.trim() || submitting || !slug) return;
    setSubmitting(true);
    setCommentError('');
    try {
      const { data } = await commentService.add(slug, commentText.trim());
      setComments(prev => [data, ...prev]);
      setTotalComments(n => n + 1);
      setCommentText('');
    } catch (err: unknown) {
      const e = err as {
        response?: { status?: number; data?: Record<string, unknown> | string };
        request?: unknown;
      };
      const data = e?.response?.data;
      let msg = 'Não foi possível publicar o comentário.';
      if (typeof data === 'string') {
        msg = data;
      } else if (data && typeof data === 'object') {
        const detail = (data as { detail?: string }).detail;
        if (detail) {
          msg = detail;
        } else {
          const firstField = Object.entries(data)[0];
          if (firstField) {
            const [, v] = firstField;
            msg = Array.isArray(v) ? String(v[0]) : String(v);
          }
        }
      } else if (e?.response?.status === 401) {
        msg = 'Você precisa estar logado para comentar.';
      } else if (!e?.response && e?.request) {
        msg = 'Não foi possível alcançar o servidor.';
      }
      setCommentError(msg);
    } finally {
      setSubmitting(false);
    }
  }, [commentText, slug, submitting]);

  const handleDelete = useCallback((id: string) => {
    const removeFromList = (list: ApiComment[]): ApiComment[] =>
      list
        .filter(c => c.id !== id)
        .map(c => ({ ...c, replies: removeFromList(c.replies ?? []) }));
    setComments(prev => removeFromList(prev));
    setTotalComments(n => Math.max(0, n - 1));
  }, []);

  const handleReplyAdded = useCallback((parentId: string, reply: ApiComment) => {
    setComments(prev =>
      prev.map(c =>
        c.id === parentId
          ? { ...c, replies: [...(c.replies ?? []), reply], replies_count: c.replies_count + 1 }
          : c
      )
    );
    setTotalComments(n => n + 1);
  }, []);

  const handleLikeToggled = useCallback((id: string, liked: boolean, count: number) => {
    const update = (list: ApiComment[]): ApiComment[] =>
      list.map(c => {
        if (c.id === id) return { ...c, is_liked: liked, likes_count: count };
        return { ...c, replies: update(c.replies ?? []) };
      });
    setComments(prev => update(prev));
  }, []);

  const handleShare = (platform: string) => {
    const url = window.location.href;
    const text = article?.title ?? '';
    const urls: Record<string, string> = {
      'Twitter/X': `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`,
      'LinkedIn': `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
      'WhatsApp': `https://wa.me/?text=${encodeURIComponent(`${text} ${url}`)}`,
    };
    if (platform === 'Copiar link') {
      navigator.clipboard.writeText(url).catch(() => {});
      return;
    }
    if (urls[platform]) window.open(urls[platform], '_blank', 'noopener');
  };

  if (loadingArticle) {
    return (
      <PageLayout>
        <div className="article-loading" role="status" aria-label="Carregando artigo">
          <div className="article-loading__spinner" />
        </div>
      </PageLayout>
    );
  }

  if (loadError || !article) {
    return (
      <PageLayout>
        <div className="container-sm" style={{ padding: '4rem 0', textAlign: 'center' }}>
          <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: '2rem', marginBottom: '1rem' }}>
            {loadError ? 'Não foi possível abrir o artigo' : 'Artigo indisponível'}
          </h1>
          <p style={{ color: 'var(--clr-muted)', marginBottom: '2rem' }}>
            {loadError || 'Tente novamente em instantes.'}
          </p>
          <Button variant="primary" onClick={() => navigate('/')}>
            Voltar ao início
          </Button>
        </div>
      </PageLayout>
    );
  }


  return (
    <PageLayout>
      <div
        className="article-progress"
        role="progressbar"
        aria-valuenow={Math.round(progress)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Progresso de leitura"
      >
        <div className="article-progress__fill" style={{ width: `${progress}%` }} />
      </div>

      <article className="article-page">
        <div className="container-sm">
          <nav className="article-breadcrumb" aria-label="Localização atual">
            <Link to="/">Início</Link>
            <span aria-hidden="true">›</span>
            {article.category && <Link to="/">{article.category.name}</Link>}
            {article.category && <span aria-hidden="true">›</span>}
            <span aria-current="page">Artigo</span>
          </nav>

          <header className="article-header">
            {article.category && <Badge variant="subtle">{article.category.name}</Badge>}
            <h1 className="article-title">{article.title}</h1>
            <p className="article-excerpt">{article.excerpt}</p>

            <div className="article-byline">
              <div className="article-author">
                <div className="article-author__avatar" aria-hidden="true">
                  {article.author.avatar_initial}
                </div>
                <div className="article-author__info">
                  <strong>{article.author.full_name}</strong>
                  <span>{article.author.role === 'admin' ? 'Editor' : 'Colaborador'}</span>
                </div>
              </div>
              <div className="article-meta">
                {article.published_at && (
                  <time dateTime={article.published_at}>{formatDate(article.published_at)}</time>
                )}
                <span aria-hidden="true">·</span>
                <span>{readingTime(article.body ?? '')} min de leitura</span>
              </div>
            </div>

            <div className="article-share" aria-label="Compartilhar artigo">
              <span>Compartilhar:</span>
              {SHARE_TARGETS.map(({ key, label, icon }) => (
                <button
                  key={key}
                  className="article-share__btn"
                  onClick={() => handleShare(key)}
                  aria-label={`Compartilhar no ${label}`}
                >
                  <span className="article-share__icon" aria-hidden="true">{icon}</span>
                  {label}
                </button>
              ))}
            </div>
          </header>
        </div>

        {article.cover_image && (
          <figure className="article-cover">
            <img
              src={article.cover_image}
              alt={article.title}
              loading="eager"
              decoding="async"
              fetchPriority="high"
            />
            {article.cover_caption && (
              <figcaption className="article-cover__caption">
                {article.cover_caption}
              </figcaption>
            )}
          </figure>
        )}

        <div className="container-sm">
          <div className="article-body">
            {renderArticleBody(article.body ?? '', article.author.full_name)}
          </div>

          <hr className="article-divider" />

          <div className="article-author-card">
            <div className="article-author-card__avatar">{article.author.avatar_initial}</div>
            <div>
              <p className="article-author-card__name">{article.author.full_name}</p>
              <p className="article-author-card__role">
                {article.author.role === 'admin' ? 'Editor' : 'Colaborador'}
              </p>
            </div>
          </div>

          <hr className="article-divider" />

          {/* Comments */}
          <section className="article-comments" aria-labelledby="comments-heading">
            <h2 id="comments-heading">
              Comentários <span>({totalComments})</span>
            </h2>

            {currentUser ? (
              <div className="article-comment-form">
                <textarea
                  value={commentText}
                  onChange={e => setCommentText(e.target.value)}
                  placeholder="Deixe seu comentário…"
                  rows={3}
                  maxLength={2000}
                  aria-label="Escrever comentário"
                />
                {commentError && (
                  <p
                    role="alert"
                    style={{
                      color: '#991B1B',
                      background: '#FEE2E2',
                      padding: 'var(--sp-2) var(--sp-3)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: 'var(--text-sm)',
                      marginTop: 'var(--sp-2)',
                    }}
                  >
                    {commentError}
                  </p>
                )}
                <div className="article-comment-form__actions">
                  <Button
                    variant="primary"
                    size="md"
                    disabled={!commentText.trim() || submitting}
                    onClick={handleSubmitComment}
                  >
                    {submitting ? 'Publicando…' : 'Publicar comentário'}
                  </Button>
                </div>
              </div>
            ) : (
              <p className="article-comments__login-prompt">
                <Link to="/login" className="auth-link auth-link--strong">Entre</Link> ou{' '}
                <Link to="/cadastro" className="auth-link auth-link--strong">crie uma conta</Link>{' '}
                para comentar.
              </p>
            )}

            {comments.length > 0 ? (
              <ol className="article-comments-list">
                {comments.map(c => (
                  <CommentItem
                    key={c.id}
                    comment={c}
                    articleSlug={article.slug}
                    onDelete={handleDelete}
                    onReplyAdded={handleReplyAdded}
                    onLikeToggled={handleLikeToggled}
                  />
                ))}
              </ol>
            ) : (
              <p className="article-comments__empty">Seja o primeiro a comentar.</p>
            )}
          </section>
        </div>
      </article>
    </PageLayout>
  );
}
