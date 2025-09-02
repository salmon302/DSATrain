import React, { useState } from 'react';
import { Box, Card, CardContent, Typography, Grid, TextField, Slider, Button, Alert, LinearProgress } from '@mui/material';
import { cognitiveAPI, settingsAPI } from '../services/api';

const CognitiveAssessment: React.FC = () => {
  const [workingMemory, setWorkingMemory] = useState(5);
  const [visualPref, setVisualPref] = useState(0.5);
  const [speed, setSpeed] = useState<'slow' | 'average' | 'fast'>('average');
  const [style, setStyle] = useState<'visual' | 'verbal' | 'balanced'>('balanced');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    try {
      setLoading(true);
      setError(null);
      // Backend expects: working_memory_quiz, style_preference, visual_vs_verbal, processing_speed_hint
      const payload = {
        working_memory_quiz: workingMemory,
        style_preference: style,
        visual_vs_verbal: visualPref,
        processing_speed_hint: speed,
      } as any;
      const resp = await cognitiveAPI.assess(payload);
      setResult(resp);
      // Persist into settings for reflection in UI (optional best-effort)
      try {
        await settingsAPI.updateCognitiveProfile({
          working_memory_capacity: resp?.working_memory_capacity ?? workingMemory,
          learning_style_preference: resp?.learning_style_preference ?? style,
          visual_vs_verbal: resp?.visual_vs_verbal ?? visualPref,
          processing_speed: resp?.processing_speed ?? speed,
        });
      } catch {}
    } catch (e) {
      setError('Cognitive assessment endpoint not available.');
    } finally {
      setLoading(false);
    }
  };

  const slider = (label: string, value: number, setValue: (n: number) => void, min: number, max: number, step: number) => (
    <Box>
      <Typography gutterBottom>
        {label}: {step >= 1 ? Math.round(value) : value.toFixed(2)}
      </Typography>
      <Slider value={value} min={min} max={max} step={step} marks onChange={(_, v) => setValue(v as number)} />
    </Box>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>🧠 Cognitive Assessment</Typography>
  <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Help us adapt the UI to your working memory and learning style
      </Typography>

      {error && <Alert severity="warning" sx={{ mb: 2 }}>{error}</Alert>}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <Card>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              {slider('Working memory (1–10)', workingMemory, setWorkingMemory, 1, 10, 1)}
              {slider('Visual vs Verbal (0–1)', visualPref, setVisualPref, 0, 1, 0.05)}
              <Box mt={2}>
                <Typography variant="body2" gutterBottom>Style Preference</Typography>
                <Box display="flex" gap={1}>
                  <Button variant={style === 'visual' ? 'contained' : 'outlined'} onClick={() => setStyle('visual')}>Visual</Button>
                  <Button variant={style === 'balanced' ? 'contained' : 'outlined'} onClick={() => setStyle('balanced')}>Balanced</Button>
                  <Button variant={style === 'verbal' ? 'contained' : 'outlined'} onClick={() => setStyle('verbal')}>Verbal</Button>
                </Box>
              </Box>
              <Box mt={2}>
                <Typography variant="body2" gutterBottom>Processing Speed</Typography>
                <Box display="flex" gap={1}>
                  <Button variant={speed === 'slow' ? 'contained' : 'outlined'} onClick={() => setSpeed('slow')}>Slow</Button>
                  <Button variant={speed === 'average' ? 'contained' : 'outlined'} onClick={() => setSpeed('average')}>Average</Button>
                  <Button variant={speed === 'fast' ? 'contained' : 'outlined'} onClick={() => setSpeed('fast')}>Fast</Button>
                </Box>
              </Box>
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
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
              {JSON.stringify({
                user_id: result.user_id,
                working_memory_capacity: result.working_memory_capacity,
                learning_style_preference: result.learning_style_preference,
                visual_vs_verbal: result.visual_vs_verbal,
                processing_speed: result.processing_speed,
                updated_at: result.updated_at,
              }, null, 2)}
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default CognitiveAssessment;


