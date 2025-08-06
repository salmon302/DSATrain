import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Box,
  Typography,
  Alert,
  Card,
  CardContent,
  Grid,
  Button,
  Tabs,
  Tab,
  Divider,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  LinearProgress,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  Code,
  PlayArrow,
  CheckCircle,
  Cancel,
  Star,
  Timer,
  Speed,
  School,
  Lightbulb,
  ExpandMore,
  Assessment,
  TrendingUp,
  BookmarkBorder,
  Bookmark,
  Share,
  Print,
  Refresh,
} from '@mui/icons-material';

import CodeEditor from '../components/CodeEditor';
import GoogleStyleCodeEditor from '../components/GoogleStyleCodeEditor';
import { problemsAPI, Problem, trackingAPI, getCurrentUserId, generateSessionId } from '../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
  </div>
);

const CodePractice: React.FC = () => {
  const location = useLocation();
  const [problems, setProblems] = useState<Problem[]>([]);
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null);
  const [problemDetails, setProblemDetails] = useState<any>(null);
  const [userCode, setUserCode] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [bookmarked, setBookmarked] = useState(false);
  const [solveTime, setSolveTime] = useState(0);
  const [isTimerActive, setIsTimerActive] = useState(false);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [showHints, setShowHints] = useState(false);
  const [currentHint, setCurrentHint] = useState(0);
  const [googleInterviewMode, setGoogleInterviewMode] = useState(false);

  const userId = getCurrentUserId();
  const sessionId = generateSessionId();

  // Get problem ID from navigation state if passed from ProblemBrowser
  const targetProblemId = (location.state as { problemId?: string })?.problemId;

  // Load random practice problems
  const loadPracticeProblems = async () => {
    try {
      setLoading(true);
      const response = await problemsAPI.getProblems({ 
        limit: 20,
        // min_quality: 80, // Remove this line as it's not supported by the API type
        // order_by: 'random' // Remove this line as it's not supported by the API type
      });
      setProblems(response.problems || []);
      
      // Auto-select first problem
      if (response.problems && response.problems.length > 0) {
        await selectProblem(response.problems[0]);
      }
    } catch (err: any) {
      console.error('Error loading practice problems:', err);
      setError('Failed to load practice problems. Please check if the API server is running.');
    } finally {
      setLoading(false);
    }
  };

  // Select a problem for practice
  const selectProblem = async (problem: Problem) => {
    setSelectedProblem(problem);
    setLoading(true);
    
    try {
      // Track problem selection
      await trackingAPI.trackInteraction({
        user_id: userId,
        problem_id: problem.id,
        action: 'selected_for_practice',
        session_id: sessionId
      });

      // Load problem details and solutions
      const [problemDetail, solutionsData] = await Promise.all([
        problemsAPI.getProblem(problem.id),
        fetch(`http://localhost:8000/problems/${problem.id}/solutions`).then(r => r.json())
          .catch(() => ({ solutions: [] }))
      ]);
      
      setProblemDetails({
        ...problemDetail,
        solutions: solutionsData.solutions || []
      });

      // Reset practice state
      setUserCode('');
      setSolveTime(0);
      setIsTimerActive(false);
      setSubmissions([]);
      setCurrentHint(0);
      setShowHints(false);
      
    } catch (error) {
      console.error('Error loading problem details:', error);
      setProblemDetails(problem);
    } finally {
      setLoading(false);
    }
  };

  // Start practice timer
  const startPractice = () => {
    setIsTimerActive(true);
    setSolveTime(0);
    
    const timer = setInterval(() => {
      setSolveTime(prev => prev + 1);
    }, 1000);

    // Store timer reference to clear later
    (window as any).practiceTimer = timer;
  };

  // Stop practice timer
  const stopPractice = () => {
    setIsTimerActive(false);
    if ((window as any).practiceTimer) {
      clearInterval((window as any).practiceTimer);
    }
  };

  // Handle code submission
  const handleSubmission = async (code: string, language: string) => {
    if (!selectedProblem) return;

    try {
      // Stop timer
      stopPractice();
      
      // Track submission
      await trackingAPI.trackInteraction({
        user_id: userId,
        problem_id: selectedProblem.id,
        action: 'submitted_solution',
        session_id: sessionId,
        metadata: JSON.stringify({
          language,
          solve_time: solveTime,
          code_length: code.length
        })
      });

      // Mock submission result
      const submission = {
        id: Date.now(),
        timestamp: new Date(),
        code,
        language,
        status: Math.random() > 0.3 ? 'accepted' : 'wrong_answer',
        runtime: Math.floor(Math.random() * 100) + 50,
        memory: Math.floor(Math.random() * 50) + 10,
        test_cases_passed: Math.floor(Math.random() * 10) + 8,
        total_test_cases: 12,
        solve_time: solveTime
      };

      setSubmissions(prev => [submission, ...prev]);
      
      // Switch to submissions tab
      setActiveTab(2);

    } catch (error) {
      console.error('Error submitting solution:', error);
    }
  };

  // Format time
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Get difficulty color
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  // Practice hints based on problem type
  const getHints = (problem: Problem) => {
    const hints = [
      "Read the problem statement carefully and identify the input/output format.",
      "Think about the time and space complexity requirements.",
      "Consider edge cases: empty input, single element, maximum constraints.",
      "Break down the problem into smaller subproblems.",
      "Choose the right algorithm: brute force, optimization, or advanced data structures."
    ];

    // Add specific hints based on algorithm tags
    if (problem.algorithm_tags?.includes('dynamic_programming')) {
      hints.push("Consider if this problem has overlapping subproblems that can be memoized.");
    }
    if (problem.algorithm_tags?.includes('graph')) {
      hints.push("Think about whether you need BFS, DFS, or a shortest path algorithm.");
    }
    if (problem.algorithm_tags?.includes('two_pointers')) {
      hints.push("Consider using two pointers from different positions in the array.");
    }

    return hints;
  };

  useEffect(() => {
    loadPracticeProblems();
    
    // Cleanup timer on unmount
    return () => {
      if ((window as any).practiceTimer) {
        clearInterval((window as any).practiceTimer);
      }
    };
  }, []);

  // Handle target problem selection from navigation
  useEffect(() => {
    if (targetProblemId && problems.length > 0) {
      const targetProblem = problems.find(p => p.id === targetProblemId);
      if (targetProblem) {
        selectProblem(targetProblem);
      } else {
        // Try to fetch the specific problem if not in the loaded list
        const fetchTargetProblem = async () => {
          try {
            const problemDetail = await problemsAPI.getProblem(targetProblemId);
            await selectProblem(problemDetail);
          } catch (error) {
            console.error('Failed to load target problem:', error);
          }
        };
        fetchTargetProblem();
      }
    }
  }, [targetProblemId, problems]);

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            🚀 Code Practice Arena
          </Typography>
          <Typography variant="subtitle1" color="textSecondary">
            Sharpen your coding skills with interactive problem solving
          </Typography>
        </Box>
        
        <Box display="flex" gap={1} alignItems="center">
          {isTimerActive && (
            <Paper sx={{ px: 2, py: 1, backgroundColor: 'primary.main', color: 'primary.contrastText' }}>
              <Box display="flex" alignItems="center" gap={1}>
                <Timer />
                <Typography variant="h6" fontWeight="bold">
                  {formatTime(solveTime)}
                </Typography>
              </Box>
            </Paper>
          )}
          
          <Tooltip title="Refresh Problems">
            <IconButton onClick={loadPracticeProblems}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && <LinearProgress sx={{ mb: 3 }} />}

      <Grid container spacing={3}>
        {/* Problem Selection Sidebar */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Practice Problems
              </Typography>
              <List sx={{ maxHeight: '70vh', overflow: 'auto' }}>
                {problems.map((problem) => (
                  <ListItem
                    key={problem.id}
                    button
                    selected={selectedProblem?.id === problem.id}
                    onClick={() => selectProblem(problem)}
                    sx={{
                      mb: 1,
                      borderRadius: 1,
                      border: selectedProblem?.id === problem.id ? 2 : 1,
                      borderColor: selectedProblem?.id === problem.id ? 'primary.main' : 'divider'
                    }}
                  >
                    <ListItemIcon>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Chip 
                          label={problem.difficulty}
                          size="small"
                          color={getDifficultyColor(problem.difficulty) as any}
                        />
                        <Star sx={{ fontSize: 16, color: 'gold' }} />
                        <Typography variant="caption">
                          {problem.quality_score?.toFixed(1) || 'N/A'}
                        </Typography>
                      </Box>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography 
                          variant="subtitle2" 
                          sx={{ 
                            fontWeight: selectedProblem?.id === problem.id ? 'bold' : 'normal',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical'
                          }}
                        >
                          {problem.title}
                        </Typography>
                      }
                      secondary={
                        <Box display="flex" gap={0.5} mt={0.5} flexWrap="wrap">
                          {problem.algorithm_tags?.slice(0, 2).map((tag, index) => (
                            <Chip key={index} label={tag} size="small" variant="outlined" />
                          ))}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Main Practice Area */}
        <Grid item xs={12} md={9}>
          {selectedProblem ? (
            <Box>
              {/* Problem Header */}
              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h5" fontWeight="bold">
                      {selectedProblem.title}
                    </Typography>
                    <Box display="flex" gap={1} alignItems="center">
                      <Chip 
                        label={selectedProblem.platform}
                        variant="outlined"
                      />
                      <Chip 
                        label={selectedProblem.difficulty}
                        color={getDifficultyColor(selectedProblem.difficulty) as any}
                      />
                      <IconButton 
                        onClick={() => setBookmarked(!bookmarked)}
                        color={bookmarked ? 'primary' : 'default'}
                      >
                        {bookmarked ? <Bookmark /> : <BookmarkBorder />}
                      </IconButton>
                    </Box>
                  </Box>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box textAlign="center">
                        <Typography variant="h6" color="primary" fontWeight="bold">
                          {selectedProblem.quality_score?.toFixed(1) || 'N/A'}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Quality Score
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box textAlign="center">
                        <Typography variant="h6" color="warning.main" fontWeight="bold">
                          {selectedProblem.google_interview_relevance?.toFixed(0) || 'N/A'}%
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Google Relevance
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box textAlign="center">
                        <Typography variant="h6" color="success.main" fontWeight="bold">
                          {problemDetails?.solutions?.length || 0}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Solutions Available
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box textAlign="center">
                        <Button
                          variant={isTimerActive ? "outlined" : "contained"}
                          color="primary"
                          onClick={isTimerActive ? stopPractice : startPractice}
                          startIcon={<PlayArrow />}
                          size="small"
                        >
                          {isTimerActive ? 'Stop' : 'Start'} Timer
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>

              {/* Practice Tabs */}
              <Card>
                <CardContent sx={{ p: 0 }}>
                  <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
                    <Tab label="Problem" icon={<School />} />
                    <Tab label="Code Editor" icon={<Code />} />
                    <Tab label="Submissions" icon={<Assessment />} />
                    <Tab label="Solutions" icon={<Lightbulb />} />
                  </Tabs>

                  <TabPanel value={activeTab} index={0}>
                    <Box sx={{ p: 3 }}>
                      {/* Problem Description */}
                      {problemDetails?.description && (
                        <Box mb={3}>
                          <Typography variant="h6" gutterBottom>Problem Description</Typography>
                          <Paper variant="outlined" sx={{ p: 2 }}>
                            <Typography style={{ whiteSpace: 'pre-wrap' }}>
                              {problemDetails.description}
                            </Typography>
                          </Paper>
                        </Box>
                      )}

                      {/* Algorithm Tags */}
                      <Box mb={3}>
                        <Typography variant="h6" gutterBottom>Algorithm Tags</Typography>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          {selectedProblem.algorithm_tags?.map((tag, index) => (
                            <Chip key={index} label={tag} color="primary" variant="outlined" />
                          ))}
                        </Box>
                      </Box>

                      {/* Hints */}
                      <Box>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                          <Typography variant="h6">Practice Hints</Typography>
                          <Button
                            variant="outlined"
                            onClick={() => setShowHints(!showHints)}
                            startIcon={<Lightbulb />}
                          >
                            {showHints ? 'Hide' : 'Show'} Hints
                          </Button>
                        </Box>
                        
                        {showHints && (
                          <Box>
                            {getHints(selectedProblem).map((hint, index) => (
                              <Accordion key={index} disabled={index > currentHint}>
                                <AccordionSummary expandIcon={<ExpandMore />}>
                                  <Typography variant="subtitle2">
                                    Hint {index + 1} {index <= currentHint ? '✓' : '🔒'}
                                  </Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                  <Typography>{hint}</Typography>
                                  {index === currentHint && (
                                    <Button
                                      size="small"
                                      onClick={() => setCurrentHint(prev => prev + 1)}
                                      sx={{ mt: 1 }}
                                    >
                                      Next Hint
                                    </Button>
                                  )}
                                </AccordionDetails>
                              </Accordion>
                            ))}
                          </Box>
                        )}
                      </Box>
                    </Box>
                  </TabPanel>

                  <TabPanel value={activeTab} index={1}>
                    <Box sx={{ mb: 2 }}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={googleInterviewMode}
                            onChange={(e) => setGoogleInterviewMode(e.target.checked)}
                            color="primary"
                          />
                        }
                        label="Google Interview Simulation Mode"
                      />
                    </Box>
                    
                    {googleInterviewMode ? (
                      <GoogleStyleCodeEditor
                        problemId={selectedProblem.id}
                        onCodeChange={setUserCode}
                        onSubmit={handleSubmission}
                        interviewMode={true}
                      />
                    ) : (
                      <CodeEditor
                        problemId={selectedProblem.id}
                        onCodeChange={setUserCode}
                        onSubmit={handleSubmission}
                      />
                    )}
                  </TabPanel>

                  <TabPanel value={activeTab} index={2}>
                    <Box sx={{ p: 3 }}>
                      <Typography variant="h6" gutterBottom>Your Submissions</Typography>
                      {submissions.length > 0 ? (
                        <Box>
                          {submissions.map((submission) => (
                            <Paper key={submission.id} variant="outlined" sx={{ p: 2, mb: 2 }}>
                              <Grid container spacing={2} alignItems="center">
                                <Grid item xs={12} sm={2}>
                                  <Box display="flex" alignItems="center" gap={1}>
                                    {submission.status === 'accepted' ? (
                                      <CheckCircle color="success" />
                                    ) : (
                                      <Cancel color="error" />
                                    )}
                                    <Typography 
                                      variant="body2" 
                                      color={submission.status === 'accepted' ? 'success.main' : 'error.main'}
                                      fontWeight="bold"
                                    >
                                      {submission.status.replace('_', ' ').toUpperCase()}
                                    </Typography>
                                  </Box>
                                </Grid>
                                <Grid item xs={12} sm={2}>
                                  <Typography variant="body2">
                                    Runtime: {submission.runtime}ms
                                  </Typography>
                                </Grid>
                                <Grid item xs={12} sm={2}>
                                  <Typography variant="body2">
                                    Memory: {submission.memory}MB
                                  </Typography>
                                </Grid>
                                <Grid item xs={12} sm={2}>
                                  <Typography variant="body2">
                                    Tests: {submission.test_cases_passed}/{submission.total_test_cases}
                                  </Typography>
                                </Grid>
                                <Grid item xs={12} sm={2}>
                                  <Typography variant="body2">
                                    Time: {formatTime(submission.solve_time)}
                                  </Typography>
                                </Grid>
                                <Grid item xs={12} sm={2}>
                                  <Typography variant="body2" color="textSecondary">
                                    {submission.timestamp.toLocaleTimeString()}
                                  </Typography>
                                </Grid>
                              </Grid>
                            </Paper>
                          ))}
                        </Box>
                      ) : (
                        <Typography color="textSecondary">
                          No submissions yet. Submit your solution to see results here.
                        </Typography>
                      )}
                    </Box>
                  </TabPanel>

                  <TabPanel value={activeTab} index={3}>
                    <Box sx={{ p: 3 }}>
                      <Typography variant="h6" gutterBottom>Reference Solutions</Typography>
                      {problemDetails?.solutions && problemDetails.solutions.length > 0 ? (
                        <Alert severity="info" sx={{ mb: 2 }}>
                          💡 Try solving the problem yourself first before looking at these solutions!
                        </Alert>
                      ) : (
                        <Typography color="textSecondary">
                          No reference solutions available for this problem.
                        </Typography>
                      )}
                      
                      {problemDetails?.solutions?.map((solution: any, index: number) => (
                        <Accordion key={index}>
                          <AccordionSummary expandIcon={<ExpandMore />}>
                            <Typography variant="subtitle1">
                              Solution {index + 1} - {solution.approach_type} 
                              (Quality: {solution.overall_quality_score?.toFixed(1) || 'N/A'}/100)
                            </Typography>
                          </AccordionSummary>
                          <AccordionDetails>
                            <CodeEditor
                              initialCode={solution.code}
                              language={solution.language}
                              readOnly
                            />
                            {solution.explanation && (
                              <Box mt={2}>
                                <Typography variant="body2" color="textSecondary">
                                  <strong>Explanation:</strong> {solution.explanation}
                                </Typography>
                              </Box>
                            )}
                          </AccordionDetails>
                        </Accordion>
                      ))}
                    </Box>
                  </TabPanel>
                </CardContent>
              </Card>
            </Box>
          ) : (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 6 }}>
                <Code sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  Select a problem to start practicing
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Choose from the problems on the left to begin your coding practice session.
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default CodePractice;
