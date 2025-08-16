import React, { useEffect, useMemo, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Alert,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
} from '@mui/material';
import { Psychology, Build, School, Quiz, Analytics, PlayArrow } from '@mui/icons-material';

import AIStatusWidget from '../components/AIStatusWidget';
import {
  aiAPI,
  practiceAPI,
  learningPathsAPI,
  enhancedStatsAPI,
  getCurrentUserId,
  sessionManager,
  Problem,
  LearningPath,
} from '../services/api';

const DevTools: React.FC = () => {
  const userId = getCurrentUserId();
  const [sessionId, setSessionId] = useState<string>(sessionManager.getCurrentSessionId());

  const [practiceResult, setPracticeResult] = useState<{ problems?: Problem[] } | null>(null);
  const [learningPath, setLearningPath] = useState<LearningPath | null>(null);
  const [overview, setOverview] = useState<any>(null);
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [retryAfter, setRetryAfter] = useState<number | null>(null);

  const setBusy = (key: string, value: boolean) => setLoading((p) => ({ ...p, [key]: value }));

  const handleError = (err: any) => {
    const status = err?.response?.status;
    if (status === 403) {
      setError('AI is disabled or provider is not ready (403).');
    } else if (status === 429) {
      setError('Rate limited (429).');
      const ra = parseInt(err?.response?.headers?.['retry-after'] || '0');
      if (ra > 0) setRetryAfter(ra);
    } else if (status === 404) {
      setError('Resource not found (404).');
    } else {
      setError(err?.response?.data?.detail || err?.message || 'Request failed');
    }
  };

  const triggerPractice = async () => {
    try {
      setBusy('practice', true);
      setError(null);
      setRetryAfter(null);
      const res = await practiceAPI.startSession({ user_id: userId, size: 5, interleaving: true });
      setPracticeResult(res);
    } catch (e: any) {
      handleError(e);
    } finally {
      setBusy('practice', false);
    }
  };

  const triggerLearningPath = async () => {
    try {
      setBusy('lp', true);
      setError(null);
      setRetryAfter(null);
      const res = await learningPathsAPI.generateLearningPath({ user_id: userId, duration_weeks: 8, goal: 'google_interview' });
      setLearningPath(res.learning_path || res);
    } catch (e: any) {
      handleError(e);
    } finally {
      setBusy('lp', false);
    }
  };

  const loadOverview = async () => {
    try {
      setBusy('overview', true);
      setError(null);
      setRetryAfter(null);
      const res = await enhancedStatsAPI.getOverview();
      setOverview(res);
    } catch (e: any) {
      handleError(e);
    } finally {
      setBusy('overview', false);
    }
  };

  useEffect(() => {
    loadOverview();
  }, []);

  const firstWeek = useMemo(() => learningPath?.weekly_plan?.[0], [learningPath]);

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom display="flex" alignItems="center" gap={1}>
            <Build /> Dev Tools
          </Typography>
          <Typography variant="subtitle1" color="textSecondary">
            Thin wiring to exercise API endpoints and validate payloads
          </Typography>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {retryAfter && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Retry after {retryAfter}s
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <AIStatusWidget sessionId={sessionId} onSessionIdChange={setSessionId} showDevControls />
        </Grid>

        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <Quiz /> Practice Session
              </Typography>
              <Button variant="contained" onClick={triggerPractice} disabled={!!loading.practice} startIcon={loading.practice ? <CircularProgress size={16} /> : <PlayArrow />}>
                {loading.practice ? 'Generating…' : 'Generate 5-Problem Session'}
              </Button>
              {practiceResult?.problems && (
                <Box mt={2}>
                  <List dense>
                    {practiceResult.problems.slice(0, 5).map((p: Problem) => (
                      <ListItem key={p.id} sx={{ px: 0 }}>
                        <ListItemText
                          primary={p.title}
                          secondary={
                            <Box display="flex" gap={1} alignItems="center">
                              <Chip size="small" label={p.difficulty} />
                              <Chip size="small" variant="outlined" label={p.platform} />
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <School /> Learning Path (First Week)
              </Typography>
              <Button variant="contained" onClick={triggerLearningPath} disabled={!!loading.lp} startIcon={loading.lp ? <CircularProgress size={16} /> : <Psychology />}>
                {loading.lp ? 'Generating…' : 'Generate Path'}
              </Button>
              {firstWeek && (
                <Box mt={2}>
                  <Typography variant="subtitle2">Week {firstWeek.week} • {firstWeek.estimated_hours}h</Typography>
                  <Divider sx={{ my: 1 }} />
                  <List dense>
                    {firstWeek.problems.slice(0, 5).map((p: Problem) => (
                      <ListItem key={p.id} sx={{ px: 0 }}>
                        <ListItemText primary={p.title} secondary={<Chip size="small" label={p.difficulty} />} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <Analytics /> Enhanced Stats Overview
              </Typography>
              <Button variant="outlined" onClick={loadOverview} disabled={!!loading.overview} sx={{ mb: 2 }}>
                {loading.overview ? 'Refreshing…' : 'Refresh'}
              </Button>
              {overview ? (
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Card variant="outlined"><CardContent><Typography variant="subtitle2">Total Problems</Typography><Typography variant="h5">{overview.overview?.total_problems ?? '—'}</Typography></CardContent></Card>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Card variant="outlined"><CardContent><Typography variant="subtitle2">Interview-Ready</Typography><Typography variant="h5">{overview.overview?.total_interview_ready ?? '—'}</Typography></CardContent></Card>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Card variant="outlined"><CardContent><Typography variant="subtitle2">Avg Google Rel.</Typography><Typography variant="h5">{overview.overview?.average_google_relevance?.toFixed?.(1) ?? '—'}</Typography></CardContent></Card>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Card variant="outlined"><CardContent><Typography variant="subtitle2">Avg Quality</Typography><Typography variant="h5">{overview.overview?.average_quality_score?.toFixed?.(1) ?? '—'}</Typography></CardContent></Card>
                  </Grid>
                </Grid>
              ) : (
                <Typography color="textSecondary">No overview data yet.</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DevTools;


