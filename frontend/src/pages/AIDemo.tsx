import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
} from '@mui/material';
import {
  Psychology,
  Code,
  HelpOutline,
  RateReview,
  MenuBook,
} from '@mui/icons-material';

import AIStatusWidget from '../components/AIStatusWidget';
import { aiAPI, problemsAPI, sessionManager } from '../services/api';

const AIDemo: React.FC = () => {
  const [sessionId, setSessionId] = useState<string>('');
  const [problems, setProblems] = useState<any[]>([]);
  const [selectedProblem, setSelectedProblem] = useState<string>('');
  const [hintQuery, setHintQuery] = useState<string>('');
  const [code, setCode] = useState<string>('');
  const [hintResult, setHintResult] = useState<any>(null);
  const [reviewResult, setReviewResult] = useState<any>(null);
  const [elaborateResult, setElaborateResult] = useState<any>(null);
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({});
  const [error, setError] = useState<string | null>(null);
  const [retryAfter, setRetryAfter] = useState<{ [key: string]: number }>({});

  // Initialize session
  useEffect(() => {
    const currentSessionId = sessionManager.getCurrentSessionId();
    setSessionId(currentSessionId);
    
    // Load some problems for demo
    loadProblems();
  }, []);

  const loadProblems = async () => {
    try {
      const response = await problemsAPI.getProblems({ limit: 10 });
      setProblems(response.problems || []);
      if (response.problems?.length > 0) {
        setSelectedProblem(response.problems[0].id);
      }
    } catch (error) {
      console.error('Error loading problems:', error);
    }
  };

  const setLoadingState = (action: string, isLoading: boolean) => {
    setLoading(prev => ({ ...prev, [action]: isLoading }));
  };

  const handleAPIError = (error: any, action: string) => {
    if (error.response?.status === 429) {
      const retryAfterHeader = error.response.headers['retry-after'];
      if (retryAfterHeader) {
        const total = parseInt(retryAfterHeader);
        setRetryAfter(prev => ({ ...prev, [action]: total }));
        // Tick down every second for label updates
        const interval = setInterval(() => {
          setRetryAfter(prev => {
            const next = { ...prev } as any;
            const current = next[action] || 0;
            const updated = Math.max(0, (current as number) - 1);
            if (updated <= 0) {
              delete next[action];
              clearInterval(interval);
            } else {
              next[action] = updated;
            }
            return next;
          });
        }, 1000);
      }
    }
    setError(error.response?.data?.detail || error.message || 'An error occurred');
  };

  const getHint = async () => {
    if (!selectedProblem) return;
    
    try {
      setLoadingState('hint', true);
      setError(null);
      setHintResult(null);

      const result = await aiAPI.getHint(selectedProblem, hintQuery || undefined, sessionId);
      setHintResult(result);

    } catch (error: any) {
      handleAPIError(error, 'hint');
    } finally {
      setLoadingState('hint', false);
    }
  };

  const reviewCode = async () => {
    if (!code.trim()) return;
    
    try {
      setLoadingState('review', true);
      setError(null);
      setReviewResult(null);

      const result = await aiAPI.reviewCode(code, undefined, selectedProblem);
      setReviewResult(result);

    } catch (error: any) {
      handleAPIError(error, 'review');
    } finally {
      setLoadingState('review', false);
    }
  };

  const elaborate = async () => {
    if (!selectedProblem) return;
    
    try {
      setLoadingState('elaborate', true);
      setError(null);
      setElaborateResult(null);

      const result = await aiAPI.elaborate(selectedProblem);
      setElaborateResult(result);

    } catch (error: any) {
      handleAPIError(error, 'elaborate');
    } finally {
      setLoadingState('elaborate', false);
    }
  };

  const newSession = () => {
    const newSessionId = sessionManager.generateSessionId();
    sessionManager.setSessionId(newSessionId);
    setSessionId(newSessionId);
    setHintResult(null);
    setReviewResult(null);
    setElaborateResult(null);
  };

  const isActionDisabled = (action: string) => {
    return loading[action] || retryAfter[action] > 0;
  };

  const getActionButtonText = (action: string, defaultText: string) => {
    if (loading[action]) return 'Loading...';
    if (retryAfter[action] > 0) return `Wait ${retryAfter[action]}s`;
    return defaultText;
  };

  return (
    <Box>
      {/* Header */}
      <Typography variant="h4" gutterBottom display="flex" alignItems="center" gap={1}>
        <Psychology />
        AI Features Demo
      </Typography>
      
      <Typography variant="body1" color="textSecondary" paragraph>
        Demonstrate AI features including hints, code review, and problem elaboration with rate limiting and session management.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* AI Status */}
        <Grid item xs={12} md={4}>
          <AIStatusWidget
            sessionId={sessionId}
            onSessionIdChange={setSessionId}
            showDevControls={process.env.NODE_ENV === 'development'}
          />
        </Grid>

        {/* Session Controls */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Session Management
              </Typography>
              
              <Box display="flex" gap={2} alignItems="center" mb={2}>
                <Chip label={`Session: ${sessionId.split('_')[0]}...`} />
                <Button variant="outlined" size="small" onClick={newSession}>
                  New Session
                </Button>
              </Box>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Select Problem</InputLabel>
                <Select
                  value={selectedProblem}
                  onChange={(e) => setSelectedProblem(e.target.value)}
                >
                  {problems.map((problem) => (
                    <MenuItem key={problem.id} value={problem.id}>
                      {problem.title} ({problem.difficulty})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        {/* Hint Feature */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <HelpOutline />
                Get Hint
              </Typography>
              
              <TextField
                fullWidth
                label="Hint Query (optional)"
                value={hintQuery}
                onChange={(e) => setHintQuery(e.target.value)}
                placeholder="What specific aspect do you need help with?"
                sx={{ mb: 2 }}
              />
              
              <Button
                variant="contained"
                onClick={getHint}
                disabled={isActionDisabled('hint') || !selectedProblem}
                fullWidth
              >
                {getActionButtonText('hint', 'Get Hint')}
              </Button>

              {retryAfter.hint > 0 && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  Rate limited. Please wait {retryAfter.hint} seconds.
                </Alert>
              )}

              {hintResult && (
                <Box sx={{ mt: 2 }}>
                  <Divider sx={{ mb: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Hint Response:
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(hintResult, null, 2)}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Code Review Feature */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <RateReview />
                Code Review
              </Typography>
              
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Your Code"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Paste your code here for review..."
                sx={{ mb: 2 }}
              />
              
              <Button
                variant="contained"
                onClick={reviewCode}
                disabled={isActionDisabled('review') || !code.trim()}
                fullWidth
              >
                {getActionButtonText('review', 'Review Code')}
              </Button>

              {retryAfter.review > 0 && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  Rate limited. Please wait {retryAfter.review} seconds.
                </Alert>
              )}

              {reviewResult && (
                <Box sx={{ mt: 2 }}>
                  <Divider sx={{ mb: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Review Response:
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(reviewResult, null, 2)}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Elaborate Feature */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <MenuBook />
                Problem Elaboration
              </Typography>
              
              <Button
                variant="contained"
                onClick={elaborate}
                disabled={isActionDisabled('elaborate') || !selectedProblem}
                sx={{ mb: 2 }}
              >
                {getActionButtonText('elaborate', 'Elaborate Problem')}
              </Button>

              {retryAfter.elaborate > 0 && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  Rate limited. Please wait {retryAfter.elaborate} seconds.
                </Alert>
              )}

              {elaborateResult && (
                <Box>
                  <Divider sx={{ mb: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Elaboration Response:
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(elaborateResult, null, 2)}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AIDemo;
