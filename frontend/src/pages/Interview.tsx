import React, { useEffect, useState } from 'react';
import { Box, Card, CardContent, Typography, Button, Grid, LinearProgress, Alert, Chip } from '@mui/material';
import { interviewAPI, problemsAPI, getCurrentUserId, generateSessionId, Problem } from '../services/api';
import GoogleStyleCodeEditor from '../components/GoogleStyleCodeEditor';

const Interview: React.FC = () => {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null);
  const [interviewId, setInterviewId] = useState<string | null>(null);
  const [duration, setDuration] = useState<number>(45);
  const [timeLeft, setTimeLeft] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [latestCode, setLatestCode] = useState('');
  const [latestLang, setLatestLang] = useState('python');

  const userId = getCurrentUserId();
  const sessionId = generateSessionId();

  useEffect(() => {
    const timer = timeLeft > 0 ? setTimeout(() => setTimeLeft(timeLeft - 1), 1000) : undefined;
    return () => { if (timer) clearTimeout(timer); };
  }, [timeLeft]);

  const loadProblems = async () => {
    try {
      setLoading(true);
      const resp = await problemsAPI.getProblems({ limit: 10 });
      setProblems(resp.problems || []);
    } catch (e) {
      setError('Failed to load problems');
    } finally {
      setLoading(false);
    }
  };

  const startInterview = async () => {
    if (!selectedProblem) return;
    try {
      setLoading(true);
      const resp = await interviewAPI.start({ problem_id: selectedProblem.id, duration_minutes: duration, session_id: sessionId });
      setInterviewId(resp.interview_id || resp.id);
      setTimeLeft((resp.duration_minutes || duration) * 60);
      setError(null);
    } catch (e) {
      setError('Interview endpoints not available.');
    } finally {
      setLoading(false);
    }
  };

  const completeInterview = async () => {
    if (!interviewId) return;
    try {
      setLoading(true);
      await interviewAPI.complete({ interview_id: interviewId, code: latestCode, language: latestLang, metrics: { time_spent_seconds: (duration * 60) - timeLeft } });
      setSubmitted(true);
    } catch (e) {
      setError('Failed to submit interview.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadProblems(); }, []);

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>🧪 Timed Interview</Typography>
          <Typography variant="subtitle1" color="textSecondary">Start a timed interview session with rubric overview and Google-style editor</Typography>
        </Box>
        {timeLeft > 0 && (
          <Chip label={`⏳ ${Math.floor(timeLeft/60)}:${(timeLeft%60).toString().padStart(2,'0')}`} color={timeLeft < 300 ? 'error' : 'primary'} />
        )}
      </Box>

      {error && <Alert severity="warning" sx={{ mb: 2 }}>{error}</Alert>}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {!interviewId ? (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Select a problem</Typography>
            <Grid container spacing={2}>
              {problems.map((p) => (
                <Grid item xs={12} sm={6} md={4} key={p.id}>
                  <Card onClick={() => setSelectedProblem(p)} sx={{ cursor: 'pointer' }}>
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight="bold">{p.title}</Typography>
                      <Chip label={p.difficulty} size="small" sx={{ mt: 1 }} />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
            <Box mt={2} display="flex" gap={1}>
              <Button variant="contained" disabled={!selectedProblem} onClick={startInterview}>Start {duration}m Interview</Button>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Interview Workspace</Typography>
            <GoogleStyleCodeEditor
              problemId={selectedProblem?.id}
              onCodeChange={(c) => setLatestCode(c)}
              onSubmit={(c, lang) => { setLatestCode(c); setLatestLang(lang); completeInterview(); }}
              interviewMode
            />
            <Box mt={2} display="flex" gap={1}>
              <Button variant="outlined" onClick={() => completeInterview()} disabled={submitted}>Submit</Button>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default Interview;


