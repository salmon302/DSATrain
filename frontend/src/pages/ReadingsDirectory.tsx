import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Box, Typography, TextField, Stack, Chip, ToggleButton, ToggleButtonGroup, Card, CardContent, CardActions, Button, Skeleton } from '@mui/material';
import { readingsAPI, ReadingMaterial } from '../services/readingsAPI';

const difficultyOptions = ['beginner', 'intermediate', 'advanced'] as const;
const typeOptions = ['guide', 'reference', 'tutorial', 'case_study', 'interactive'] as const;

const ReadingsDirectory: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [difficulty, setDifficulty] = useState<string | null>(searchParams.get('level'));
  const [contentType, setContentType] = useState<string | null>(searchParams.get('type'));
  const [loading, setLoading] = useState(false);
  const [materials, setMaterials] = useState<ReadingMaterial[]>([]);
  const navigate = useNavigate();

  const runSearch = useCallback(async () => {
    setLoading(true);
    try {
      const res = await readingsAPI.search({ query: query || '', difficulty_level: difficulty || undefined, content_type: contentType || undefined });
      setMaterials(res.materials || []);
    } finally {
      setLoading(false);
    }
  }, [query, difficulty, contentType]);

  useEffect(() => {
    void runSearch();
  }, [runSearch]);

  const onApplyFilters = useCallback(() => {
    const next = new URLSearchParams();
    if (query) next.set('q', query);
    if (difficulty) next.set('level', difficulty);
    if (contentType) next.set('type', contentType);
    setSearchParams(next);
    void runSearch();
  }, [query, difficulty, contentType, runSearch, setSearchParams]);

  const onOpen = useCallback((m: ReadingMaterial) => {
    navigate(`/readings/material/${m.id}`);
  }, [navigate]);

  return (
    <Box>
      <Typography variant="h2" gutterBottom>Readings</Typography>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ xs: 'stretch', md: 'center' }} sx={{ mb: 2 }}>
        <TextField label="Search" value={query} onChange={(e) => setQuery(e.target.value)} fullWidth />

        <ToggleButtonGroup
          value={difficulty}
          exclusive
          onChange={(_, v) => setDifficulty(v)}
          size="small"
        >
          {difficultyOptions.map((d) => (
            <ToggleButton key={d} value={d}>{d}</ToggleButton>
          ))}
        </ToggleButtonGroup>

        <ToggleButtonGroup
          value={contentType}
          exclusive
          onChange={(_, v) => setContentType(v)}
          size="small"
        >
          {typeOptions.map((t) => (
            <ToggleButton key={t} value={t}>{t}</ToggleButton>
          ))}
        </ToggleButtonGroup>

        <Button variant="contained" onClick={onApplyFilters}>Apply</Button>
      </Stack>

      <Stack spacing={2}>
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} variant="rectangular" height={120} />
          ))
        ) : (
          materials.map((m) => (
            <Card key={m.id} variant="outlined">
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={2}>
                  <Box>
                    <Typography variant="h5">{m.title}</Typography>
                    {m.subtitle && <Typography color="text.secondary">{m.subtitle}</Typography>}
                    <Typography variant="body2" sx={{ mt: 1 }}>{m.summary}</Typography>
                    <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                      <Chip label={m.difficulty_level} size="small" />
                      <Chip label={m.content_type} size="small" />
                      {typeof m.estimated_read_time === 'number' && (
                        <Chip label={`${m.estimated_read_time} min`} size="small" />
                      )}
                    </Stack>
                  </Box>
                  <Box textAlign="right" minWidth={120}>
                    <Typography variant="body2">⭐ {m.user_ratings?.toFixed?.(1) ?? '0.0'} ({m.total_ratings ?? 0})</Typography>
                    <Typography variant="body2">👁️ {m.view_count ?? 0}</Typography>
                  </Box>
                </Stack>
              </CardContent>
              <CardActions>
                <Button size="small" onClick={() => onOpen(m)}>Open</Button>
              </CardActions>
            </Card>
          ))
        )}
      </Stack>
    </Box>
  );
};

export default ReadingsDirectory;
