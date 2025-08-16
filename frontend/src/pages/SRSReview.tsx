import React, { useEffect, useState } from 'react';
import { Box, Card, CardContent, Typography, Button, LinearProgress, Grid, Chip, Alert, Slider, TextField } from '@mui/material';
import { srsAPI, getCurrentUserId } from '../services/api';

const SRSReview: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [timeSpent, setTimeSpent] = useState(0);
  const [notes, setNotes] = useState('');

  const userId = getCurrentUserId();

  useEffect(() => {
    const timer = setInterval(() => setTimeSpent((t) => t + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  const loadNextDue = async () => {
    try {
      setLoading(true);
      setError(null);
      const resp = await srsAPI.getNextDue({ user_id: userId, limit: 10 });
      setItems(resp.items || []);
      setCurrentIndex(0);
      setTimeSpent(0);
      setNotes('');
    } catch (e: any) {
      setError('SRS endpoints not available.');
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  const submitRating = async (rating: 0 | 1 | 2 | 3 | 4 | 5) => {
    const current = items[currentIndex];
    if (!current) return;
    try {
      await srsAPI.submitReview({
        user_id: userId,
        item_id: current.id,
        item_type: current.type || 'problem',
        rating,
        time_spent_seconds: timeSpent,
        notes: notes || undefined,
      });
      if (currentIndex + 1 < items.length) {
        setCurrentIndex(currentIndex + 1);
        setTimeSpent(0);
        setNotes('');
      } else {
        await loadNextDue();
      }
    } catch (e) {
      // ignore
    }
  };

  useEffect(() => {
    loadNextDue();
  }, []);

  const current = items[currentIndex];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            🔁 Spaced Repetition Review
          </Typography>
          <Typography variant="subtitle1" color="textSecondary">
            Practice due problems and patterns to reinforce learning
          </Typography>
        </Box>
        <Button variant="outlined" onClick={loadNextDue}>Refresh</Button>
      </Box>

      {error && <Alert severity="warning" sx={{ mb: 2 }}>{error}</Alert>}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {current ? (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {current.title || current.name}
            </Typography>
            <Box display="flex" gap={1} mb={2}>
              {current.difficulty && <Chip label={current.difficulty} size="small" />}
              {current.tags?.slice(0, 3).map((t: string, i: number) => (
                <Chip key={i} label={t} size="small" variant="outlined" />
              ))}
            </Box>

            {current.description && (
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                {current.description}
              </Typography>
            )}

            <Box mt={3}>
              <Typography variant="subtitle2" gutterBottom>How well did you recall it?</Typography>
              <Grid container spacing={1}>
                {[0,1,2,3,4,5].map((r) => (
                  <Grid item key={r}>
                    <Button variant="outlined" onClick={() => submitRating(r as 0|1|2|3|4|5)}>{r}</Button>
                  </Grid>
                ))}
              </Grid>
            </Box>

            <Box mt={2}>
              <TextField
                fullWidth
                label="Notes (optional)"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                multiline
                minRows={2}
              />
            </Box>

            <Box mt={2} display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="caption">Time: {timeSpent}s</Typography>
              <Typography variant="caption">Item {currentIndex + 1} / {items.length}</Typography>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <Typography variant="h6" gutterBottom>No items due</Typography>
            <Typography variant="body2" color="textSecondary">
              Great job! You have no items to review right now.
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default SRSReview;


