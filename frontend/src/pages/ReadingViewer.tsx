import React, { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import { Box, Typography, Stack, Chip, LinearProgress, Divider, Button, Rating, List, ListItemButton, ListItemText, Grid, Link } from '@mui/material';
import { ReadingMaterial, readingsAPI } from '../services/readingsAPI';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

// Simple slugify for heading IDs
function slugify(text: string): string {
  return (text || '')
    .toString()
    .normalize('NFKD')
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '') // remove non-alphanum
    .replace(/\s+/g, '-') // spaces to dashes
    .replace(/-+/g, '-') // collapse
    .replace(/^-|-$/g, ''); // trim
}

const ReadingViewer: React.FC = () => {
  const { id } = useParams();
  const [material, setMaterial] = useState<ReadingMaterial | null>(null);
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(0);
  const [rating, setRating] = useState<number | null>(null);
  const [ratingSaved, setRatingSaved] = useState(false);
  const [ratingError, setRatingError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const headingIdsRef = useRef<string[]>([]);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const contentRef = useRef<HTMLDivElement | null>(null);
  const [relatedTitles, setRelatedTitles] = useState<Record<string, string>>({});
  const lastSectionKey = useMemo(() => material ? `reading:lastSection:${material.id}` : '', [material]);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const m = await readingsAPI.getMaterial(id as string, true);
        if (!mounted) return;
  setMaterial(m);
        setProgress(m.user_progress?.progress_percentage ?? 0);
        // initial small progress touch so analytics can count a view; tolerate failures silently
        try {
          await readingsAPI.updateProgress(m.id, {
            progress_percentage: m.user_progress?.progress_percentage ?? 1,
            reading_time_seconds: (m.user_progress?.reading_time_seconds ?? 0) + 5,
          });
        } catch {}
      } finally {
        if (mounted) setLoading(false);
      }
    };
    if (id) void load();
    return () => { mounted = false; };
  }, [id]);

  // Load titles for prerequisite and follow-up materials (best-effort)
  useEffect(() => {
    let cancel = false;
    const loadRelated = async () => {
      if (!material) return;
      const ids = [...(material.prerequisite_materials || []), ...(material.follow_up_materials || [])];
      const unique = Array.from(new Set(ids));
    const entries = unique.map(async (mid) => {
        try {
          const m = await readingsAPI.getMaterial(mid, false);
      return [mid, m.title || mid] as [string, string];
        } catch {
      return [mid, mid] as [string, string];
        }
      });
    const results: [string, string][] = await Promise.all(entries);
      if (!cancel) {
        const map: Record<string, string> = {};
        results.forEach(([k, v]) => { map[k] = v; });
        setRelatedTitles(map);
      }
    };
    void loadRelated();
    return () => { cancel = true; };
  }, [material]);

  const components = useMemo(() => ({
    h1({ children }: any) {
      const text = String(children?.[0] ?? '');
      const id = slugify(text);
      return <Typography id={id} variant="h3" sx={{ mt: 2 }}>{children}</Typography>;
    },
    h2({ children }: any) {
      const text = String(children?.[0] ?? '');
      const id = slugify(text);
      return <Typography id={id} variant="h5" sx={{ mt: 2 }}>{children}</Typography>;
    },
    h3({ children }: any) {
      const text = String(children?.[0] ?? '');
      const id = slugify(text);
      return <Typography id={id} variant="h6" sx={{ mt: 2 }}>{children}</Typography>;
    },
    code({ inline, className, children, ...props }: any) {
      const match = /language-(\w+)/.exec(className || '');
      return !inline && match ? (
        <SyntaxHighlighter style={oneDark} language={match[1]} PreTag="div" {...props}>
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
  }), []);

  // Note: Don't early-return before hooks; guards are placed just before render below

  const saveRating = async (value: number | null) => {
    if (!material || value == null) return;
    setRating(value);
    setRatingSaved(false);
    setRatingError(null);
    try {
      await readingsAPI.rate(material.id, { user_rating: value });
      setRatingSaved(true);
      setTimeout(() => setRatingSaved(false), 2000);
    } catch (e: any) {
      setRatingError('Failed to save rating');
    }
  };

  // Build sections: prefer provided content_sections; fallback to parsing markdown H2s
  const sections = useMemo(() => {
    const provided = (material?.content_sections || []).filter((s: any) => s && typeof s.title === 'string' && s.title.trim().length > 0);
    if (provided.length > 0) {
      return provided.map((s: any) => ({ title: s.title, id: slugify(s.title || '') }));
    }
    const md = material?.content_markdown || '';
    const derived: Array<{ title: string; id: string }> = [];
    for (const line of md.split(/\r?\n/)) {
      if (line.startsWith('## ')) {
        const title = line.slice(3).trim();
        if (title) derived.push({ title, id: slugify(title) });
      }
    }
    return derived;
  }, [material?.content_sections, material?.content_markdown]);
  headingIdsRef.current = sections.map(s => s.id);

  // Scroll spy observer
  useEffect(() => {
    if (!contentRef.current || sections.length === 0) return;
    if (observerRef.current) {
      observerRef.current.disconnect();
    }
    const obs = new IntersectionObserver(
      (entries) => {
        // pick the entry most visible near top
        const visible = entries
          .filter(e => e.isIntersecting)
          .sort((a, b) => Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top));
        if (visible[0]?.target?.id) {
          const id = visible[0].target.id;
          setActiveSection(id);
          if (lastSectionKey) {
            try { localStorage.setItem(lastSectionKey, id); } catch {}
          }
        }
      },
      { root: null, rootMargin: '0px 0px -70% 0px', threshold: [0, 1.0] }
    );
    observerRef.current = obs;
    headingIdsRef.current.forEach(id => {
      const el = document.getElementById(id);
      if (el) obs.observe(el);
    });
    return () => { obs.disconnect(); };
  // eslint-disable-next-line
  }, [material?.id, contentRef.current, sections.length]);

  const scrollTo = useCallback((id: string) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, []);

  // Restore last-read section on load
  useEffect(() => {
    if (!material) return;
    let target: string | null = null;
    if (lastSectionKey) {
      try { target = localStorage.getItem(lastSectionKey); } catch {}
    }
    if (target) {
      // delay to allow markdown render and observer attach
      const t = setTimeout(() => scrollTo(target as string), 200);
      return () => clearTimeout(t);
    }
    return;
  }, [material, lastSectionKey, scrollTo]);

  // Place guards after all hooks to satisfy rules-of-hooks
  if (loading) return <LinearProgress />;
  if (!material) return <Typography>Not found</Typography>;

  return (
    <Grid container spacing={3}>
      {/* Sticky ToC (left on wide screens) */}
      <Grid item xs={12} md={3} lg={3} sx={{ display: { xs: 'none', md: 'block' } }}>
        <Box sx={{ position: 'sticky', top: 80 }}>
          <Typography variant="overline" color="text.secondary">Contents</Typography>
          <List dense>
            {sections.map((s) => (
              <ListItemButton key={s.id} selected={activeSection === s.id} onClick={() => scrollTo(s.id)}>
                <ListItemText primary={s.title} />
              </ListItemButton>
            ))}
          </List>
        </Box>
      </Grid>

      {/* Main content */}
      <Grid item xs={12} md={9} lg={9}>
        <Typography variant="h3" gutterBottom>{material.title}</Typography>
  {material.subtitle && <Typography color="text.secondary" gutterBottom>{material.subtitle}</Typography>}
        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          <Chip label={material.difficulty_level} size="small" />
          <Chip label={material.content_type} size="small" />
          {typeof material.estimated_read_time === 'number' && <Chip label={`${material.estimated_read_time} min`} size="small" />}
        </Stack>

        <Divider sx={{ my: 2 }} />

        <Box ref={contentRef} sx={{ '& pre': { borderRadius: 1, overflow: 'auto' }, '& code': { bgcolor: 'action.hover', px: 0.5, borderRadius: 0.5 } }}>
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
            {material.content_markdown || ''}
          </ReactMarkdown>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ xs: 'flex-start', sm: 'center' }}>
          <Typography variant="body2">Progress: {progress.toFixed(0)}%</Typography>
          <Button onClick={async () => {
            const next = Math.min(100, progress + 10);
            setProgress(next);
            try {
              await readingsAPI.updateProgress(material.id, { progress_percentage: next, reading_time_seconds: (material.user_progress?.reading_time_seconds ?? 0) + 30 });
            } catch {}
          }}>+10%</Button>
          <Divider flexItem orientation="vertical" />
          <Stack direction="row" spacing={1} alignItems="center">
            <Typography variant="body2">Rate this:</Typography>
            <Rating
              value={rating}
              onChange={(
                _event: React.SyntheticEvent<Element, Event>,
                v: number | null
              ) => void saveRating(v)}
              size="small"
            />
            {ratingSaved && <Typography variant="caption" color="success.main">Saved</Typography>}
            {ratingError && <Typography variant="caption" color="error.main">{ratingError}</Typography>}
          </Stack>
        </Stack>

        {/* Related materials */}
        {(material.prerequisite_materials?.length || material.follow_up_materials?.length) && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>Related Materials</Typography>
            {material.prerequisite_materials?.length ? (
              <Box sx={{ mb: 1 }}>
                <Typography variant="subtitle2" color="text.secondary">Prerequisites</Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {material.prerequisite_materials.map(mid => (
                    <Link key={`pre-${mid}`} component={RouterLink} to={`/readings/material/${mid}`} underline="hover">{relatedTitles[mid] || mid}</Link>
                  ))}
                </Stack>
              </Box>
            ) : null}
            {material.follow_up_materials?.length ? (
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Follow-ups</Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {material.follow_up_materials.map(mid => (
                    <Link key={`post-${mid}`} component={RouterLink} to={`/readings/material/${mid}`} underline="hover">{relatedTitles[mid] || mid}</Link>
                  ))}
                </Stack>
              </Box>
            ) : null}
          </Box>
        )}
      </Grid>
    </Grid>
  );
};

export default ReadingViewer;
