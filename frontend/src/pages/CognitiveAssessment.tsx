import React, { useState } from 'react';
import { Box, Card, CardContent, Typography, Grid, TextField, Slider, Button, Alert, LinearProgress } from '@mui/material';
import { cognitiveAPI, settingsAPI } from '../services/api';

const CognitiveAssessment: React.FC = () => {
  const [workingMemory, setWorkingMemory] = useState(3);
  const [visualLearner, setVisualLearner] = useState(3);
  const [verbalLearner, setVerbalLearner] = useState(3);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    try {
      setLoading(true);
      setError(null);
      const payload = {
        working_memory: workingMemory,
        learning_style: {
          visual: visualLearner,
          verbal: verbalLearner,
        },
        notes: notes || undefined,
      };
      const resp = await cognitiveAPI.assess(payload);
      setResult(resp);
      // Persist into settings for reflection in UI
      try {
        await settingsAPI.updateCognitiveProfile(resp?.profile || payload);
      } catch {}
    } catch (e) {
      setError('Cognitive assessment endpoint not available.');
    } finally {
      setLoading(false);
    }
  };

  const slider = (label: string, value: number, setValue: (n: number) => void) => (
    <Box>
      <Typography gutterBottom>{label}: {value}</Typography>
      <Slider value={value} min={1} max={5} marks step={1} onChange={(_, v) => setValue(v as number)} />
    </Box>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>🧠 Cognitive Assessment</Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Help us adapt the UI to your working memory and learning style
      </Typography>

      {error && <Alert severity="warning" sx={{ mb: 2 }}>{error}</Alert>}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <Card>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              {slider('Working memory (1–5)', workingMemory, setWorkingMemory)}
              {slider('Visual preference (1–5)', visualLearner, setVisualLearner)}
              {slider('Verbal preference (1–5)', verbalLearner, setVerbalLearner)}
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Notes (optional)"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                multiline
                minRows={6}
              />
            </Grid>
          </Grid>

          <Box mt={2}>
            <Button variant="contained" onClick={submit}>Submit Assessment</Button>
          </Box>
        </CardContent>
      </Card>

      {result && (
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Assessment Results</Typography>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(result, null, 2)}</Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default CognitiveAssessment;


