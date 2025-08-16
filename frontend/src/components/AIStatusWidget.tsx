import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Grid,
  Alert,
  Button,
  CircularProgress,
  Tooltip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  Refresh,
  Psychology,
  Timer,
  Warning,
  Check,
  Error as ErrorIcon,
  RestartAlt,
  Settings,
  Info,
} from '@mui/icons-material';

import { apiService } from '../services/api';

interface AIStatus {
  enabled: boolean;
  provider: string;
  model: string | null;
  rate_limit_per_minute: number;
  rate_limit_used: number;
  rate_limit_window_seconds: number;
  rate_limit_reset_seconds: number;
  hint_budget_per_session: number;
  hints_used_this_session: number | null;
  session_id?: string;
}

interface RetryCountdownProps {
  retryAfterSeconds: number;
  onRetryReady: () => void;
}

const RetryCountdown: React.FC<RetryCountdownProps> = ({ retryAfterSeconds, onRetryReady }) => {
  const [timeLeft, setTimeLeft] = useState(retryAfterSeconds);

  useEffect(() => {
    if (timeLeft <= 0) {
      onRetryReady();
      return;
    }

    const timer = setTimeout(() => {
      setTimeLeft(timeLeft - 1);
    }, 1000);

    return () => clearTimeout(timer);
  }, [timeLeft, onRetryReady]);

  if (timeLeft <= 0) {
    return null;
  }

  return (
    <Alert severity="warning" sx={{ mt: 1 }}>
      <Typography variant="body2">
        Rate limit exceeded. Please wait {timeLeft} seconds before trying again.
      </Typography>
      <LinearProgress 
        variant="determinate" 
        value={(retryAfterSeconds - timeLeft) / retryAfterSeconds * 100}
        sx={{ mt: 1 }}
      />
    </Alert>
  );
};

interface AIStatusWidgetProps {
  sessionId?: string;
  onSessionIdChange?: (sessionId: string) => void;
  showDevControls?: boolean;
  compact?: boolean;
}

const AIStatusWidget: React.FC<AIStatusWidgetProps> = ({
  sessionId,
  onSessionIdChange,
  showDevControls = false,
  compact = false,
}) => {
  const [status, setStatus] = useState<AIStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryAfter, setRetryAfter] = useState<number | null>(null);
  const [showResetDialog, setShowResetDialog] = useState(false);
  const [resetGlobal, setResetGlobal] = useState(true);
  const [resetSessionId, setResetSessionId] = useState('');

  // Load AI status
  const loadStatus = async (showLoader = true) => {
    try {
      if (showLoader) setLoading(true);
      setError(null);

      const params = sessionId ? { session_id: sessionId } : {};
      const response = await apiService.get('/ai/status', { params });
      setStatus(response.data);

    } catch (error: any) {
      console.error('Error loading AI status:', error);
      setError(error.response?.data?.detail || 'Failed to load AI status');
    } finally {
      if (showLoader) setLoading(false);
    }
  };

  // Reset AI counters
  const resetCounters = async () => {
    try {
      setLoading(true);
      setError(null);

      const payload: any = { reset_global: resetGlobal };
      if (resetSessionId) {
        payload.session_id = resetSessionId;
      }

      await apiService.post('/ai/reset', payload);
      await loadStatus(false);
      setShowResetDialog(false);

    } catch (error: any) {
      console.error('Error resetting AI counters:', error);
      setError(error.response?.data?.detail || 'Failed to reset AI counters');
    } finally {
      setLoading(false);
    }
  };

  // Handle rate limit retry
  const handleRetryReady = () => {
    setRetryAfter(null);
    loadStatus(false);
  };

  // Auto-refresh status
  useEffect(() => {
    loadStatus();
    
    // Set up periodic refresh
    const interval = setInterval(() => {
      loadStatus(false);
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [sessionId]);

  // Handle API errors with retry-after
  useEffect(() => {
    const handleAPIError = (error: any) => {
      if (error.response?.status === 429) {
        const retryAfterHeader = error.response.headers['retry-after'];
        if (retryAfterHeader) {
          setRetryAfter(parseInt(retryAfterHeader));
        }
      }
    };

    // Add response interceptor for this component
    const interceptor = apiService.interceptors.response.use(
      response => response,
      error => {
        handleAPIError(error);
        return Promise.reject(error);
      }
    );

    return () => {
      apiService.interceptors.response.eject(interceptor);
    };
  }, []);

  if (loading && !status) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" py={2}>
            <CircularProgress size={24} />
            <Typography variant="body2" sx={{ ml: 1 }}>
              Loading AI status...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error && !status) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">
            {error}
            <Button size="small" onClick={() => loadStatus()} sx={{ mt: 1 }}>
              Retry
            </Button>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return null;
  }

  const rateLimitUsage = status.rate_limit_per_minute > 0 
    ? (status.rate_limit_used / status.rate_limit_per_minute) * 100 
    : 0;

  const sessionUsage = status.hint_budget_per_session > 0 
    ? (((status.hints_used_this_session ?? 0) / status.hint_budget_per_session) * 100) 
    : 0;

  const getStatusColor = () => {
    if (!status.enabled) return 'default';
    if (rateLimitUsage >= 90 || sessionUsage >= 90) return 'warning';
    return 'success';
  };

  const getStatusIcon = () => {
    if (!status.enabled) return <Settings />;
    if (rateLimitUsage >= 90 || sessionUsage >= 90) return <Warning />;
    return <Check />;
  };

  const getStatusText = () => {
    if (!status.enabled) return 'Disabled';
    if (rateLimitUsage >= 90) return 'Rate Limited';
    if (sessionUsage >= 90) return 'Session Limit';
    return 'Ready';
  };

  if (compact) {
    return (
      <Box display="flex" alignItems="center" gap={1}>
        <Chip
          icon={getStatusIcon()}
          label={`AI: ${getStatusText()}`}
          color={getStatusColor() as any}
          size="small"
        />
        {sessionId && (
          <Tooltip title="Session ID">
            <Chip
              label={sessionId.split('_')[0]}
              size="small"
              variant="outlined"
            />
          </Tooltip>
        )}
        <IconButton size="small" onClick={() => loadStatus()}>
          <Refresh fontSize="small" />
        </IconButton>
      </Box>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" display="flex" alignItems="center" gap={1}>
            <Psychology />
            AI Status
          </Typography>
          <Box display="flex" gap={1}>
            <IconButton size="small" onClick={() => loadStatus()}>
              <Refresh />
            </IconButton>
            {showDevControls && (
              <IconButton size="small" onClick={() => setShowResetDialog(true)}>
                <RestartAlt />
              </IconButton>
            )}
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2}>
          {/* Main Status */}
          <Grid item xs={12}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="body2">Overall Status:</Typography>
              <Chip
                icon={getStatusIcon()}
                label={getStatusText()}
                color={getStatusColor() as any}
                size="small"
              />
            </Box>
          </Grid>

          {/* Provider Info */}
          <Grid item xs={12} sm={6}>
            <Typography variant="caption" color="textSecondary">
              Provider: {status.provider}
            </Typography>
            <br />
            <Typography variant="caption" color="textSecondary">
              Model: {status.model || 'None'}
            </Typography>
          </Grid>

          {/* Session Info */}
          {sessionId && (
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="textSecondary">
                Session: {sessionId.split('_')[0]}...
              </Typography>
            </Grid>
          )}

          {/* Rate Limiting */}
          {status.enabled && status.rate_limit_per_minute > 0 && (
            <Grid item xs={12}>
              <Box mb={1}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">Rate Limit:</Typography>
                  <Typography variant="caption">
                    {status.rate_limit_used} / {status.rate_limit_per_minute} per minute
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={rateLimitUsage}
                  color={rateLimitUsage >= 90 ? 'error' : rateLimitUsage >= 70 ? 'warning' : 'primary'}
                  sx={{ height: 6, borderRadius: 3 }}
                />
                {status.rate_limit_reset_seconds > 0 && (
                  <Typography variant="caption" color="textSecondary">
                    Resets in {status.rate_limit_reset_seconds}s
                  </Typography>
                )}
              </Box>
            </Grid>
          )}

          {/* Session Budget */}
          {status.enabled && status.hint_budget_per_session > 0 && sessionId && (
            <Grid item xs={12}>
              <Box>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">Hints (Session):</Typography>
                  <Typography variant="caption">
                    {status.hints_used_this_session} / {status.hint_budget_per_session}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={sessionUsage}
                  color={sessionUsage >= 90 ? 'error' : sessionUsage >= 70 ? 'warning' : 'primary'}
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
            </Grid>
          )}
        </Grid>

        {/* Retry Countdown */}
        {retryAfter && (
          <RetryCountdown
            retryAfterSeconds={retryAfter}
            onRetryReady={handleRetryReady}
          />
        )}

        {/* Reset Dialog */}
        <Dialog open={showResetDialog} onClose={() => setShowResetDialog(false)}>
          <DialogTitle>Reset AI Counters</DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="textSecondary" paragraph>
              Reset AI rate limiting and session counters. This is for development use only.
            </Typography>
            
            <FormControlLabel
              control={
                <Switch
                  checked={resetGlobal}
                  onChange={(e) => setResetGlobal(e.target.checked)}
                />
              }
              label="Reset global rate limiter"
            />
            
            <TextField
              fullWidth
              label="Session ID (optional)"
              value={resetSessionId}
              onChange={(e) => setResetSessionId(e.target.value)}
              placeholder="Leave empty to reset current session"
              sx={{ mt: 2 }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowResetDialog(false)}>Cancel</Button>
            <Button onClick={resetCounters} variant="contained" disabled={loading}>
              {loading ? 'Resetting...' : 'Reset'}
            </Button>
          </DialogActions>
        </Dialog>
      </CardContent>
    </Card>
  );
};

export default AIStatusWidget;
