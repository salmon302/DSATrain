import React, { useState, useEffect, useRef, lazy, Suspense, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
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
  ListItemButton,
  Skeleton,
  Stepper,
  Step,
  StepLabel,
  TextField,
} from '@mui/material';
import {
  Code,
  PlayArrow,
  CheckCircle,
  Cancel,
  Star,
  Timer,
  School,
  Lightbulb,
  ExpandMore,
  Assessment,
  BookmarkBorder,
  Bookmark,
  Refresh,
  Stop,
} from '@mui/icons-material';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import AutoSizer from 'react-virtualized-auto-sizer';
import { FixedSizeList as VList, ListChildComponentProps } from 'react-window';

import AIStatusWidget from '../components/AIStatusWidget';
import { apiService, problemsAPI, Problem, trackingAPI, practiceAPI, getCurrentUserId, generateSessionId, favoritesAPI, aiAPI } from '../services/api';

// Lazy components declared after all imports
const LazyCodeEditor = lazy(() => import('../components/CodeEditor'));
const LazyGoogleStyleCodeEditor = lazy(() => import('../components/GoogleStyleCodeEditor'));

// Practice Gates component
const PracticeGates: React.FC<{
  sessionId: string;
  problemId: string;
  gates: { read: boolean; plan: string; pseudocode: string; codeReady: boolean };
  onUpdate: (g: { read: boolean; plan: string; pseudocode: string; codeReady: boolean }) => void;
}> = ({ sessionId, problemId, gates, onUpdate }) => {

  // Persist drafts locally per session+problem
  const draftKey = (k: 'plan' | 'pseudocode') => `practice_gates:${sessionId}:${problemId}:${k}`;

  React.useEffect(() => {
    try {
      const planDraft = localStorage.getItem(draftKey('plan'));
      const pseudoDraft = localStorage.getItem(draftKey('pseudocode'));
      if (planDraft !== null || pseudoDraft !== null) {
        onUpdate({
          ...gates,
          plan: planDraft !== null ? planDraft : gates.plan,
          pseudocode: pseudoDraft !== null ? pseudoDraft : gates.pseudocode,
          // do not flip booleans here
        });
      }
    } catch (_) {
      // ignore localStorage errors
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, problemId]);

  const saveProgress = async (key: string, value: any) => {
  try {
      const gateMap: Record<string, 'dry_run' | 'pseudocode' | 'code'> = {
        read: 'dry_run',
        plan: 'dry_run', // treat planning as the first gate
        pseudocode: 'pseudocode',
        codeReady: 'code',
      } as const;
      const gate = gateMap[key] || 'dry_run';
      await practiceAPI.gates.progress({ session_id: sessionId, gate, value: Boolean(value) });
    } catch (e) {
      // ignore
    } finally {
      // no-op
    }
  };

  const steps = ['Read', 'Plan', 'Pseudocode', 'Code'];
  const activeStep = gates.codeReady ? 4 : gates.pseudocode ? 3 : gates.plan ? 2 : gates.read ? 1 : 0;

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="subtitle1" gutterBottom>Think Twice, Code Once</Typography>
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 2 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box display="flex" flexDirection="column" gap={2}>
          <FormControlLabel
            control={<Switch checked={gates.read} onChange={async (e) => {
              onUpdate({ ...gates, read: e.target.checked });
              await saveProgress('read', e.target.checked);
            }} />}
            label="I carefully read and understood the problem statement"
          />

          <TextField
            label="High-level plan"
            placeholder="Outline your approach in a few bullets"
            value={gates.plan}
            onChange={(e) => {
              onUpdate({ ...gates, plan: e.target.value });
              try { localStorage.setItem(draftKey('plan'), e.target.value); } catch {}
            }}
            onBlur={async () => { await saveProgress('plan', gates.plan); }}
            multiline
            minRows={2}
            disabled={!gates.read}
          />

          <TextField
            label="Pseudocode"
            placeholder="Write concise pseudocode for your solution"
            value={gates.pseudocode}
            onChange={(e) => {
              onUpdate({ ...gates, pseudocode: e.target.value });
              try { localStorage.setItem(draftKey('pseudocode'), e.target.value); } catch {}
            }}
            onBlur={async () => { await saveProgress('pseudocode', gates.pseudocode); }}
            multiline
            minRows={3}
            disabled={!gates.plan}
          />

          <FormControlLabel
            control={<Switch checked={gates.codeReady} onChange={async (e) => {
              const next = e.target.checked;
              onUpdate({ ...gates, codeReady: next });
              await saveProgress('codeReady', next); // corrected key
            }} />}
            label="I’m ready to start coding"
            disabled={!gates.pseudocode}
          />
      </Box>
      </CardContent>
    </Card>
  );
};

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
  const navigate = useNavigate();
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
  const [gatesSessionId, setGatesSessionId] = useState<string | null>(null);
  const [gates, setGates] = useState<any>({ read: false, plan: '', pseudocode: '', codeReady: false });
  const gatesEnabled = process.env.REACT_APP_FEATURE_PRACTICE_GATES !== 'off';

  // AI integration state
  const [aiHintQuery, setAiHintQuery] = useState<string>('');
  const [aiHints, setAiHints] = useState<{ hints: { level: string; text: string }[]; provider?: string; model?: string; problem_id?: string; meta?: any } | null>(null);
  const [aiHintIndex, setAiHintIndex] = useState<number>(0);
  const [aiLoading, setAiLoading] = useState<{ [key: string]: boolean }>({});
  // Split errors per feature to avoid clobbering
  const [aiHintError, setAiHintError] = useState<string | null>(null);
  const [aiElaborateError, setAiElaborateError] = useState<string | null>(null); // displayed in AI section when saving elaborative responses fails
  const [aiReviewError, setAiReviewError] = useState<string | null>(null);
  const [elaboration, setElaboration] = useState<{ why_questions: string[]; how_questions: string[] } | null>(null);
  const [aiReview, setAiReview] = useState<{ strengths?: string[]; suggestions?: string[]; rubric?: any; provider?: string; model?: string } | null>(null);
  const [reviewNotes, setReviewNotes] = useState<string>('');
  const [elabResponses, setElabResponses] = useState<Record<string, string>>({});
  const [streaming, setStreaming] = useState<boolean>(false);
  const [readingMaterials, setReadingMaterials] = useState<any[]>([]);
  const [readingLoading, setReadingLoading] = useState<boolean>(false);
  const [aiRefreshSignal, setAiRefreshSignal] = useState<number>(0);
  const [favorites, setFavorites] = useState<Set<string>>(new Set());

  const userId = getCurrentUserId();
  const sessionRef = useRef<string>(generateSessionId());
  const sessionId = sessionRef.current;

  // Timer ref to avoid leaking globals
  const timerRef = useRef<number | null>(null);

  // Prevent async races when switching problems
  const selectReqRef = useRef<number>(0);

  // ---- UI formatting helpers ----
  const titleCase = (s: string) => s.replace(/[_-]+/g, ' ').replace(/\s+/g, ' ').trim()
    .replace(/\b\w/g, (c) => c.toUpperCase());

  const normalizeTag = (tag: string) => {
    const t = tag.toLowerCase().replace(/[- ]/g, '_');
    const map: Record<string, string> = {
      two_pointers: 'Two Pointers',
      binary_search: 'Binary Search',
      sliding_window: 'Sliding Window',
      data_structures: 'Data Structures',
      constructive_algorithms: 'Constructive Algorithms',
      dfs_and_similar: 'DFS and Similar',
      number_theory: 'Number Theory',
      fast_fourier_transform: 'FFT',
    };
    return map[t] || titleCase(tag);
  };

  const formatPlatform = (p?: string) => (p ? titleCase(p) : '');
  const formatDifficulty = (d?: string) => (d ? titleCase(d) : '');

  // Build a best-effort source URL when metadata is missing (helps for Codeforces)
  const buildSourceUrl = (problem?: Problem | null): string | null => {
    if (!problem) return null;
    // Prefer any existing metadata if present
    const metaUrl = (problemDetails as any)?.metadata?.source_url;
    if (typeof metaUrl === 'string' && metaUrl.length > 0) return metaUrl;

    const platform = (problem.platform || '').toLowerCase();
    const pid = (problem.platform_id || problem.id || '').toString();

    // Codeforces IDs look like cf_<contestId>_<index>, e.g., cf_2109_A
    if (platform === 'codeforces') {
      const m = pid.match(/cf_(\d+)_([A-Za-z0-9]+)/i);
      if (m) {
        const contestId = m[1];
        const index = m[2];
        return `https://codeforces.com/contest/${contestId}/problem/${index}`;
      }
    }

    // LeetCode fallback (platform_id often numeric). We cannot map reliably without slug
    // so we avoid constructing incorrect links.
    return null;
  };

  // Get problem ID from navigation state if passed from ProblemBrowser (unused)
  // const targetProblemId = (location.state as { problemId?: string })?.problemId;
  // Select a problem for practice (memoized for stable references)
  const selectProblem = useCallback(async (problem: Problem) => {
    setSelectedProblem(problem);
    setLoading(true);
    const reqId = Date.now();
    selectReqRef.current = reqId;

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
        apiService.get(`/problems/${problem.id}/solutions`).then(r => r.data)
          .catch(() => ({ solutions: [] }))
      ]);

      // Ignore if a newer selection happened
      if (selectReqRef.current !== reqId) return;

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

      // Reset AI-related state when switching problems
      setAiHintQuery('');
      setAiHints(null);
      setAiHintIndex(0);
      setAiHintError(null);
      setAiElaborateError(null);
      setAiReviewError(null);
      setElaboration(null);
      setReadingMaterials([]);

      // Initialize practice gates if enabled
      if (gatesEnabled) {
        try {
          const start = await practiceAPI.gates.start({ problem_id: problem.id, session_id: sessionId });
          if (selectReqRef.current !== reqId) return; // guard
          setGatesSessionId(start.session_id || sessionId);
          setGates({ read: false, plan: '', pseudocode: '', codeReady: false });
        } catch (e) {
          // Non-blocking
          console.error('Failed to start practice gates session:', e);
        }
      }
      
    } catch (error) {
      console.error('Error loading problem details:', error);
      if (selectReqRef.current !== reqId) return; // guard
      setProblemDetails(problem);
    } finally {
      if (selectReqRef.current === reqId) setLoading(false);
    }
  }, [userId, sessionId, gatesEnabled]);

  // Load random practice problems
  const loadPracticeProblems = useCallback(async () => {
    try {
      setLoading(true);
      const response = await problemsAPI.getProblems({ 
        limit: 20,
        // min_quality: 80, // Remove this line as it's not supported by the API type
        // order_by: 'random' // Remove this line as it's not supported by the API type
      });
      setProblems(response.problems || []);
    } catch (err: any) {
      console.error('Error loading practice problems:', err);
      setError('Failed to load practice problems. Please check if the API server is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Start practice timer
  const startPractice = () => {
    setIsTimerActive(true);

    // do not reset here to support resume; caller can zero if needed
    if (timerRef.current != null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
    const id = window.setInterval(() => {
      setSolveTime(prev => prev + 1);
    }, 1000);
    timerRef.current = id;
  };

  // Stop practice timer
  const stopPractice = () => {
    setIsTimerActive(false);
    if (timerRef.current != null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  // Cleanup timer on unmount
  React.useEffect(() => {
    return () => {
      if (timerRef.current != null) {
        window.clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, []);

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

      // Persist attempt to backend
      try {
        await practiceAPI.logAttempt({
          user_id: userId,
          problem_id: selectedProblem.id,
          status: submission.status === 'accepted' ? 'solved' : 'attempted',
          time_spent_seconds: solveTime,
          code,
          language,
          session_id: sessionId,
          metadata: {
            runtime_ms: submission.runtime,
            memory_mb: submission.memory,
            tests_passed: submission.test_cases_passed,
            tests_total: submission.total_test_cases,
          }
        } as any);
      } catch (e) {
        // Non-blocking
        console.error('Failed to log attempt:', e);
      }
      
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
  const getDifficultyColor = (difficulty: string): 'default' | 'success' | 'warning' | 'error' => {
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

  // AI: Request hint (layered)
  const requestAIHint = async () => {
    if (!selectedProblem) return;
    try {
      setAiLoading(prev => ({ ...prev, hint: true }));
      setAiHintError(null);
      if (streaming) {
        setAiHints({ hints: [] });
        setAiHintIndex(0);
        const acc: { level?: string; text?: string }[] = [] as any;
        const sub = aiAPI.streamHint(selectedProblem.id, {
          query: aiHintQuery || undefined,
          sessionId,
          onMeta: (meta) => {
            setAiHints((prev) => ({ ...(prev || { hints: [] }), provider: meta.provider, model: meta.model, problem_id: meta.problem_id, meta }));
          },
          onHint: (hint) => {
            acc.push(hint);
            setAiHints((prev) => ({ ...(prev || { hints: [] }), hints: [...(prev?.hints || []), hint] }));
          },
          onDone: () => {
            setAiLoading(prev => ({ ...prev, hint: false }));
          },
          onError: (err) => {
            setAiHintError(typeof err === 'string' ? err : (err?.detail || 'Streaming error'));
            setAiLoading(prev => ({ ...prev, hint: false }));
          }
        });
        // Auto-close after 30s safety
        setTimeout(() => { try { sub.close(); } catch {} }, 30000);
      } else {
        const result = await aiAPI.getHint(selectedProblem.id, aiHintQuery || undefined, sessionId);
        const hints = Array.isArray(result?.hints) ? result.hints : [];
        setAiHints({
          hints,
          provider: result?.provider,
          model: result?.model,
          problem_id: result?.problem_id,
          meta: result?.meta,
        });
        setAiHintIndex(0);
      }
      // Track interaction (non-blocking)
      trackingAPI.trackInteraction({
        user_id: userId,
        problem_id: selectedProblem.id,
        action: 'ai_hint_requested',
        session_id: sessionId,
        metadata: JSON.stringify({ query: aiHintQuery || null })
      }).catch(() => {});
      setAiRefreshSignal((s) => s + 1);
    } catch (error: any) {
      const detail = error?.response?.data?.detail || error?.message || 'Failed to get AI hint';
      setAiHintError(detail);
    } finally {
      if (!streaming) setAiLoading(prev => ({ ...prev, hint: false }));
    }
  };

  // AI: Elaborate why/how questions
  const requestElaboration = async () => {
    if (!selectedProblem) return;
    try {
      setAiLoading(prev => ({ ...prev, elaborate: true }));
      setAiElaborateError(null);
      const result = await aiAPI.elaborate(selectedProblem.id);
      const why = Array.isArray(result?.why_questions) ? result.why_questions : [];
      const how = Array.isArray(result?.how_questions) ? result.how_questions : [];
      setElaboration({ why_questions: why, how_questions: how });
      const blanks: Record<string, string> = {};
      [...why, ...how].forEach((q) => { blanks[q] = ''; });
      setElabResponses(blanks);
      trackingAPI.trackInteraction({
        user_id: userId,
        problem_id: selectedProblem.id,
        action: 'ai_elaborate_requested',
        session_id: sessionId,
      }).catch(() => {});
    } catch (error: any) {
      const detail = error?.response?.data?.detail || error?.message || 'Failed to elaborate problem';
      setAiElaborateError(detail);
    } finally {
      setAiLoading(prev => ({ ...prev, elaborate: false }));
    }
  };

  const requestCodeReview = async () => {
    if (!selectedProblem || !userCode?.trim()) return;
    try {
      setAiLoading(prev => ({ ...prev, review: true }));
      setAiReviewError(null);
      setAiReview(null);
      const rubric = {
        session_id: sessionId,
        notes: reviewNotes || undefined,
        criteria: ['correctness', 'readability', 'efficiency', 'tests']
      };
      if (streaming) {
        const strengths: string[] = [];
        const suggestions: string[] = [];
        aiAPI.streamReview({ code: userCode, rubric, problem_id: selectedProblem.id }, {
          onMeta: (meta) => {
            setAiReview((prev) => ({ ...(prev || {}), provider: meta.provider, model: meta.model, rubric }));
          },
          onStrength: (text) => {
            strengths.push(text);
            setAiReview((prev) => ({ ...(prev || {}), strengths: [...(prev?.strengths || []), text] }));
          },
          onSuggestion: (text) => {
            suggestions.push(text);
            setAiReview((prev) => ({ ...(prev || {}), suggestions: [...(prev?.suggestions || []), text] }));
          },
          onDone: () => {
            setAiLoading(prev => ({ ...prev, review: false }));
          },
          onError: (err) => {
            setAiReviewError(typeof err === 'string' ? err : (err?.detail || 'Streaming error'));
            setAiLoading(prev => ({ ...prev, review: false }));
          }
        });
      } else {
        const result = await aiAPI.reviewCode(userCode, rubric as any, selectedProblem.id);
        setAiReview({
          strengths: Array.isArray(result?.strengths) ? result.strengths : [],
          suggestions: Array.isArray(result?.suggestions) ? result.suggestions : [],
          rubric: result?.rubric,
          provider: result?.provider,
          model: result?.model,
        });
      }
      trackingAPI.trackInteraction({
        user_id: userId,
        problem_id: selectedProblem.id,
        action: 'ai_review_requested',
        session_id: sessionId,
        metadata: JSON.stringify({ code_length: userCode.length })
      }).catch(() => {});
      setAiRefreshSignal((s) => s + 1);
    } catch (error: any) {
      const detail = error?.response?.data?.detail || error?.message || 'Failed to review code';
      setAiReviewError(detail);
    } finally {
      if (!streaming) setAiLoading(prev => ({ ...prev, review: false }));
    }
  };

  // Save elaborative responses (why/how answers)
  const saveElaborativeResponses = async () => {
    if (!selectedProblem || !elaboration) return;
    try {
      setAiLoading(prev => ({ ...prev, saveElaborative: true }));
      setAiElaborateError(null);
      // Optional lightweight tracking hook
      await practiceAPI.elaborative({
        problem_id: selectedProblem.id,
        question: 'batch',
        context: 'practice_ai_elaboration',
      } as any).catch(() => {});

      await apiService.post('/practice/elaborative', {
        problem_id: selectedProblem.id,
        why_questions: elaboration.why_questions,
        how_questions: elaboration.how_questions,
        responses: elabResponses,
      });
    } catch (error: any) {
      const detail = error?.response?.data?.detail || error?.message || 'Failed to save elaborative responses';
      setAiElaborateError(detail);
    } finally {
      setAiLoading(prev => ({ ...prev, saveElaborative: false }));
    }
  };

  // Contextual readings: fetch when problem changes
  useEffect(() => {
    const fetchReadings = async () => {
      if (!selectedProblem) return;
      try {
        setReadingLoading(true);
        setAiHintError(null);
        const query = selectedProblem.title || (selectedProblem.algorithm_tags || []).slice(0, 3).join(' ');
        const params: any = { query };
        const res = await apiService.get('/reading-materials/search', { params });
        setReadingMaterials(res?.data?.materials || []);
      } catch (error: any) {
        // Silent fail; keep UI minimal
        setReadingMaterials([]);
      } finally {
        setReadingLoading(false);
      }
    };
    fetchReadings();
  }, [selectedProblem]);

  useEffect(() => {
    loadPracticeProblems();
    
    // Cleanup timer on unmount
    return () => {
      if (timerRef.current != null) {
        window.clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [loadPracticeProblems]);

  // Sync bookmark state and cache favorites once
  useEffect(() => {
    const fetchFavorites = async () => {
      try {
        const res = await favoritesAPI.list(userId, false);
        const ids: string[] = res.problem_ids || [];
        setFavorites(new Set(ids));
      } catch (_) {
        // ignore
      }
    };
    fetchFavorites();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  // Derive bookmarked from favorites when selectedProblem changes
  useEffect(() => {
    if (!selectedProblem) return;
    setBookmarked(favorites.has(selectedProblem.id));
  }, [favorites, selectedProblem]);

  // Add a small reset helper
  const resetPracticeTime = () => {
    setSolveTime(0);
  };

  // Selected index for keyboard nav
  const [selectedIndex, setSelectedIndex] = useState<number>(0);

  // Update URL when selection changes
  useEffect(() => {
    if (!selectedProblem) return;
    // Build next URL using current router location to avoid direct window references in tests
    const search = new URLSearchParams(location.search);
    search.set('pid', selectedProblem.id);
    navigate({ pathname: location.pathname, search: `?${search.toString()}`, hash: location.hash }, { replace: true });
    // Only react to id changes to keep URL stable
  }, [selectedProblem, navigate, location.pathname, location.search, location.hash]);

  // Attempt initial selection by pid or title in navigation state/query (once)
  const attemptedInitialSelectRef = useRef<boolean>(false);
  useEffect(() => {
    if (attemptedInitialSelectRef.current) return; // already attempted initial selection
    const state: any = location.state || {};
    const statePid = state?.problemId as string | undefined;
    const urlPid = new URLSearchParams(location.search).get('pid') || undefined;
    const stateTitle = (state?.problemTitle as string | undefined)?.trim();
    const pid = statePid || urlPid;

    // If neither pid nor title provided, do nothing here (fallback handled separately)
    if (!pid && !stateTitle) return;
    attemptedInitialSelectRef.current = true; // prevent fallback while we attempt selection

    // Helper to select by a resolved Problem
    const selectResolved = async (prob: Problem | null) => {
      if (prob) {
        // If it's not already in list, prepend for visibility
        setProblems(prev => (prev.some(p => p.id === prob.id) ? prev : ([prob, ...prev] as unknown) as Problem[]));
        await selectProblem(prob);
      }
    };

    // Prefer selection by pid when available
    if (pid) {
      const inList = problems.find(p => p.id === pid);
      if (inList) {
        void selectResolved(inList);
        return;
      }
      (async () => {
        try {
          setLoading(true);
          const prob = await problemsAPI.getProblem(pid);
          await selectResolved(prob as Problem);
        } catch (e) {
          console.error('Failed to load target problem by id for practice:', e);
        } finally {
          setLoading(false);
        }
      })();
      return;
    }

    // Fallback: select by title (best-effort) when provided in state
    if (stateTitle) {
      // Try to find in the preloaded list first (case-insensitive)
      const inListByTitle = problems.find(p => (p.title || '').toLowerCase() === stateTitle.toLowerCase());
      if (inListByTitle) {
        void selectResolved(inListByTitle);
        return;
      }
      (async () => {
        try {
          setLoading(true);
          // Best-effort search; pick the top exact title match, else first result
          const res = await problemsAPI.searchProblems(stateTitle);
          const items: Problem[] = (res?.problems || res?.results || []) as Problem[];
          const exact = items.find(p => (p.title || '').toLowerCase() === stateTitle.toLowerCase());
          await selectResolved((exact || items[0] || null) as Problem | null);
        } catch (e) {
          console.error('Failed to resolve target problem by title for practice:', e);
        } finally {
          setLoading(false);
        }
      })();
    }
  }, [problems, selectProblem, location.state, location.search]);

  // Fallback: when problems are loaded and no pid/state provided, select the first problem once
  const fallbackSelectedRef = useRef<boolean>(false);
  useEffect(() => {
    if (fallbackSelectedRef.current) return; // already fallback-selected
    if (selectedProblem) return; // nothing to do
    // If we attempted an initial selection (by id or title), don't fallback-select
    if (attemptedInitialSelectRef.current) return;
    const statePid = (location.state as any)?.problemId as string | undefined;
    const urlPid = new URLSearchParams(location.search).get('pid') || undefined;
    const stateTitle = (location.state as any)?.problemTitle as string | undefined;
    if (statePid || urlPid || stateTitle) return; // initial flow handled in the effect above
    if (problems.length > 0) {
      fallbackSelectedRef.current = true;
      selectProblem(problems[0]);
    }
  }, [problems, selectedProblem, location.state, location.search, selectProblem]);

  // Keep selectedIndex aligned to selectedProblem
  useEffect(() => {
    if (!selectedProblem) return;
    const idx = problems.findIndex(p => p.id === selectedProblem.id);
    if (idx >= 0) setSelectedIndex(idx);
  }, [selectedProblem, problems]);

  // Keyboard navigation
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      // avoid when typing in inputs or textarea
      const t = e.target as HTMLElement;
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
      if (e.key === 'j' || e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((i) => Math.min(i + 1, Math.max(0, problems.length - 1)));
      } else if (e.key === 'k' || e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((i) => Math.max(i - 1, 0));
      } else if (e.key === 'Enter') {
        const pb = problems[selectedIndex];
        if (pb) selectProblem(pb);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [problems, selectedIndex, selectProblem]);

  // ---- Render ----
  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            🚀 Code Practice Arena
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Sharpen your coding skills with interactive problem solving
          </Typography>
        </Box>
        
        <Box display="flex" gap={1} alignItems="center">
          {/* Compact AI status with session awareness */}
          <AIStatusWidget sessionId={sessionId} compact refreshSignal={aiRefreshSignal} />
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
            <IconButton onClick={loadPracticeProblems} aria-label="Refresh problems">
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
              {/* Virtualized list */}
              <Box sx={{ height: '70vh' }}>
                <AutoSizer>
                  {({ height, width }: { height: number; width: number }) => (
                    <VList
                      height={height}
                      width={width}
                      itemCount={problems.length}
                      itemSize={88}
                    >
                      {({ index, style }: ListChildComponentProps) => {
                        const problem = problems[index];
                        const selected = selectedProblem?.id === problem.id;
                        const highlighted = index === selectedIndex;
                        return (
                          <Box key={problem.id} style={style} px={0.5}>
                            <ListItemButton
                              selected={selected}
                              onClick={() => selectProblem(problem)}
                              sx={{
                                mb: 1,
                                borderRadius: 1,
                                border: selected ? 2 : 1,
                                borderColor: selected ? 'primary.main' : 'divider',
                                outline: highlighted ? '2px solid' : 'none',
                                outlineColor: highlighted ? 'primary.main' : 'transparent',
                              }}
                            >
                              <ListItemIcon sx={{ minWidth: 36, mr: 1 }}>
                                <Box display="flex" alignItems="center" gap={0.5}>
                                  <Chip
                                    label={formatDifficulty(problem.difficulty)}
                                    size="small"
                                    color={getDifficultyColor(problem.difficulty) as any}
                                  />
                                </Box>
                              </ListItemIcon>
                              <ListItemText
                                primary={
                                  <Typography 
                                    variant="subtitle2" 
                                    sx={{ 
                                      fontWeight: selected ? 'bold' : 'normal',
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
                                  <Box display="flex" alignItems="center" justifyContent="space-between" mt={0.5}>
                                    <Box display="flex" gap={0.5} flexWrap="wrap" sx={{ pr: 1 }}>
                                      {problem.algorithm_tags?.slice(0, 2).map((tag: string, idx: number) => (
                                        <Tooltip key={idx} title={normalizeTag(tag)}>
                                          <Chip label={normalizeTag(tag)} size="small" variant="outlined" />
                                        </Tooltip>
                                      ))}
                                    </Box>
                                    <Box display="flex" alignItems="center" gap={0.5} sx={{ flexShrink: 0 }}>
                                      <Star sx={{ fontSize: 14, color: 'gold' }} />
                                      <Typography variant="caption">
                                        {problem.quality_score?.toFixed(1) || 'N/A'}
                                      </Typography>
                                    </Box>
                                  </Box>
                                }
                              />
                            </ListItemButton>
                          </Box>
                        );
                      }}
                    </VList>
                  )}
                </AutoSizer>
              </Box>
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
                  {loading ? (
                    <Box>
                      <Skeleton variant="text" width={280} height={36} />
                      <Skeleton variant="rectangular" height={64} sx={{ mt: 2 }} />
                    </Box>
                  ) : (
                    <>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Typography variant="h5" fontWeight="bold">
                          {selectedProblem.title}
                        </Typography>
                        <Box display="flex" gap={1} alignItems="center">
                          {(() => { const platformLabel = formatPlatform(selectedProblem.platform); return platformLabel ? (
                            <Chip 
                              label={platformLabel}
                              variant="outlined"
                            />) : null; })()}
                          <Chip 
                            label={formatDifficulty((problemDetails?.difficulty || selectedProblem.difficulty) as string)}
                            color={getDifficultyColor((problemDetails?.difficulty || selectedProblem.difficulty) as string) as any}
                          />
                          <IconButton 
                            onClick={async () => {
                              const next = !bookmarked;
                              setBookmarked(next);
                              // Optimistically update favorites cache
                              setFavorites((prev) => {
                                const nextSet = new Set(prev);
                                if (next) nextSet.add(selectedProblem.id); else nextSet.delete(selectedProblem.id);
                                return nextSet;
                              });
                              try {
                                await favoritesAPI.toggle({ user_id: userId, problem_id: selectedProblem.id, favorite: next });
                                // Track interaction
                                await trackingAPI.trackInteraction({
                                  user_id: userId,
                                  problem_id: selectedProblem.id,
                                  action: 'bookmarked',
                                  session_id: sessionId,
                                  metadata: JSON.stringify({ source: 'practice_header', state: next ? 'bookmarked' : 'unbookmarked' })
                                });
                              } catch (e) {
                                // revert on error
                                setBookmarked(!next);
                                setFavorites((prev) => {
                                  const nextSet = new Set(prev);
                                  if (!next) nextSet.add(selectedProblem.id); else nextSet.delete(selectedProblem.id);
                                  return nextSet;
                                });
                              }
                            }}
                            color={bookmarked ? 'primary' : 'default'}
                            aria-label={bookmarked ? 'Remove bookmark' : 'Bookmark problem'}
                          >
                            {bookmarked ? <Bookmark /> : <BookmarkBorder />}
                          </IconButton>
                        </Box>
                      </Box>
                      
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6} md={3}>
                          <Box textAlign="center">
                            <Tooltip title="Composite quality estimate (0-100) based on completeness, tagging, and consistency.">
                              <Typography variant="h6" color="primary" fontWeight="bold">
                                {selectedProblem.quality_score?.toFixed(1) || 'N/A'}
                              </Typography>
                            </Tooltip>
                            <Typography variant="caption" color="text.secondary">
                              Quality Score
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                          <Box textAlign="center">
                            <Tooltip title="Heuristic relevance to Google-style interviews (0-100%).">
                              <Typography variant="h6" color="warning.main" fontWeight="bold">
                                {selectedProblem.google_interview_relevance?.toFixed(0) || 'N/A'}%
                              </Typography>
                            </Tooltip>
                            <Typography variant="caption" color="text.secondary">
                              Google Relevance
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                          <Box textAlign="center">
                            <Typography variant="h6" color="success.main" fontWeight="bold">
                              {problemDetails?.solutions?.length || 0}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Solutions Available
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                          <Box textAlign="center">
                            <Box display="flex" justifyContent="center" gap={1}>
                              <Button
                                variant={isTimerActive ? "outlined" : "contained"}
                                color="primary"
                                onClick={isTimerActive ? stopPractice : startPractice}
                                startIcon={isTimerActive ? <Stop /> : <PlayArrow />}
                                size="small"
                                aria-label={isTimerActive ? 'Stop timer' : 'Start timer'}
                              >
                                {isTimerActive ? 'Stop' : 'Start'}
                              </Button>
                              <Button
                                variant="text"
                                size="small"
                                onClick={resetPracticeTime}
                                aria-label="Reset timer"
                              >
                                Reset
                              </Button>
                            </Box>
                          </Box>
                        </Grid>
                      </Grid>
                    </>
                  )}
                </CardContent>
              </Card>

              {/* Practice Tabs */}
              <Card>
                <CardContent sx={{ p: 0 }}>
                  <Tabs
                    value={activeTab}
                    onChange={(_, newValue) => setActiveTab(newValue)}
                    sx={{ '& .MuiTab-root': { textTransform: 'none' } }}
                  >
                    <Tab label="Problem" icon={<School />} />
                    <Tab label="Code Editor" icon={<Code />} />
                    <Tab label="Submissions" icon={<Assessment />} />
                    <Tab
                      label={`Solutions (${problemDetails?.solutions?.length || 0})`}
                      icon={<Lightbulb />}
                      disabled={(problemDetails?.solutions?.length || 0) === 0}
                    />
                  </Tabs>

                  <TabPanel value={activeTab} index={0}>
                    <Box sx={{ p: 3 }}>
                      {/* Problem Description */}
                      <Box mb={3}>
                        <Typography variant="h6" gutterBottom>Problem Description</Typography>
                        <Paper variant="outlined" sx={{ p: 2 }}>
                          {loading ? (
                            <>
                              <Skeleton variant="text" height={20} />
                              <Skeleton variant="text" height={20} />
                              <Skeleton variant="text" height={20} />
                            </>
                          ) : problemDetails?.description || selectedProblem.description ? (
                            <Typography style={{ whiteSpace: 'pre-wrap' }}>
                              {problemDetails?.description || (selectedProblem as any).description}
                            </Typography>
                          ) : (
                            <Box>
                              <Typography color="text.secondary">
                                No description available. Many external contest problems (e.g., Codeforces) don't expose statements via API.
                              </Typography>
                              {(() => {
                                const url = buildSourceUrl(selectedProblem);
                                if (!url) return null;
                                return (
                                  <Button
                                    href={url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    size="small"
                                    startIcon={<OpenInNewIcon />}
                                    sx={{ mt: 1 }}
                                  >
                                    Open on {formatPlatform(selectedProblem.platform)}
                                  </Button>
                                );
                              })()}
                            </Box>
                          )}
                        </Paper>
                      </Box>

                      {/* Algorithm Tags */}
                      <Box mb={3}>
                        <Typography variant="h6" gutterBottom>Algorithm Tags</Typography>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          {selectedProblem.algorithm_tags?.map((tag, index) => (
                            <Chip key={index} label={normalizeTag(tag)} color="primary" variant="outlined" />
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

                      {/* AI Assistant: Layered hints and elaboration */}
                      <Divider sx={{ my: 3 }} />
                      <Box>
                        <Typography variant="h6" gutterBottom>AI Assistant</Typography>
                        {aiHintError && (
                          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setAiHintError(null)}>
                            {aiHintError}
                          </Alert>
                        )}
                        <Grid container spacing={2}>
                          <Grid item xs={12} md={8}>
                            <TextField
                              fullWidth
                              size="small"
                              label="Ask for a specific hint (optional)"
                              placeholder="e.g., I'm stuck on choosing the right data structure"
                              value={aiHintQuery}
                              onChange={(e) => setAiHintQuery(e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={4}>
                            <Button
                              variant="contained"
                              fullWidth
                              onClick={requestAIHint}
                              disabled={!!aiLoading.hint || !selectedProblem}
                            >
                              {aiLoading.hint ? 'Getting Hint...' : 'Get AI Hint'}
                            </Button>
                          </Grid>
                        </Grid>

                        {aiHints && (
                          <Box mt={2}>
                            {aiHints.hints.slice(0, aiHintIndex + 1).map((h, i) => (
                              <Paper key={i} variant="outlined" sx={{ p: 2, mb: 1 }}>
                                <Typography variant="overline" color="text.secondary">{h.level}</Typography>
                                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{h.text}</Typography>
                              </Paper>
                            ))}
                            <Box display="flex" gap={1}>
                              <Button
                                variant="outlined"
                                onClick={() => setAiHintIndex(prev => Math.min(prev + 1, (aiHints.hints?.length || 1) - 1))}
                                disabled={(aiHints.hints?.length || 0) === 0 || aiHintIndex >= (aiHints.hints.length - 1)}
                              >
                                Next AI Hint
                              </Button>
                              <Button
                                variant="text"
                                onClick={() => setAiHintIndex(0)}
                                disabled={!aiHints || aiHintIndex === 0}
                              >
                                Reset
                              </Button>
                            </Box>
                          </Box>
                        )}

                        <Box mt={3}>
                          <Button
                            variant="outlined"
                            onClick={requestElaboration}
                            disabled={!!aiLoading.elaborate || !selectedProblem}
                            startIcon={<Lightbulb />}
                          >
                            {aiLoading.elaborate ? 'Generating...' : 'Generate Why/How Questions'}
                          </Button>
                          {aiElaborateError && (
                            <Alert severity="error" sx={{ mt: 2 }} onClose={() => setAiElaborateError(null)}>
                              {aiElaborateError}
                            </Alert>
                          )}
                          {elaboration && (
                            <Grid container spacing={2} sx={{ mt: 1 }}>
                              <Grid item xs={12} md={6}>
                                <Typography variant="subtitle2">Why Questions</Typography>
                                <List>
                                  {elaboration.why_questions.map((q, idx) => (
                                    <ListItem key={idx} alignItems="flex-start">
                                      <ListItemText primary={q} />
                                    </ListItem>
                                  ))}
                                </List>
                              </Grid>
                              <Grid item xs={12} md={6}>
                                <Typography variant="subtitle2">How Questions</Typography>
                                <List>
                                  {elaboration.how_questions.map((q, idx) => (
                                    <ListItem key={idx} alignItems="flex-start">
                                      <ListItemText primary={q} />
                                    </ListItem>
                                  ))}
                                </List>
                              </Grid>
                              <Grid item xs={12}>
                                <Typography variant="subtitle2" sx={{ mt: 1 }}>Your Responses</Typography>
                                <Grid container spacing={2}>
                                  {[...elaboration.why_questions, ...elaboration.how_questions].map((q, i) => (
                                    <Grid item xs={12} key={i}>
                                      <TextField
                                        fullWidth
                                        label={q}
                                        multiline
                                        minRows={2}
                                        value={elabResponses[q] ?? ''}
                                        onChange={(e) => setElabResponses(prev => ({ ...prev, [q]: e.target.value }))}
                                      />
                                    </Grid>
                                  ))}
                                </Grid>
                                <Box display="flex" justifyContent="flex-end" mt={2}>
                                  <Button
                                    variant="contained"
                                    onClick={saveElaborativeResponses}
                                    disabled={!!aiLoading.saveElaborative}
                                  >
                                    {aiLoading.saveElaborative ? 'Saving…' : 'Save Responses'}
                                  </Button>
                                </Box>
                              </Grid>
                            </Grid>
                          )}
                        </Box>
                      </Box>

                      {/* Contextual Reading Materials */}
                      <Divider sx={{ my: 3 }} />
                      <Box>
                        <Typography variant="h6" gutterBottom>Contextual Reading</Typography>
                        {readingLoading && <LinearProgress sx={{ mb: 2 }} />}
                        {!readingLoading && readingMaterials.length === 0 && (
                          <Typography color="text.secondary">No related readings found.</Typography>
                        )}
                        <List>
                          {readingMaterials.slice(0, 5).map((m: any) => (
                            <ListItem key={m.id} alignItems="flex-start">
                              <ListItemText
                                primary={m.title}
                                secondary={
                                  <>
                                    <Typography component="span" variant="caption" color="text.secondary">
                                      {m.content_type} • ~{m.estimated_read_time_minutes || m.estimated_read_time || '—'} min • Score {m.effectiveness_score?.toFixed?.(1) ?? m.effectiveness_score ?? '—'}
                                    </Typography>
                                    <Typography variant="body2" sx={{ mt: 0.5 }} color="text.secondary">
                                      {m.summary || ''}
                                    </Typography>
                                  </>
                                }
                              />
                            </ListItem>
                          ))}
                        </List>
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
                    {gatesEnabled && (
                      <PracticeGates
                        sessionId={gatesSessionId || sessionId}
                        problemId={selectedProblem.id}
                        gates={gates}
                        onUpdate={setGates}
                      />
                    )}
                    <Suspense fallback={<Box sx={{ p: 3 }}><LinearProgress /></Box>}>
                      {googleInterviewMode ? (
                        <LazyGoogleStyleCodeEditor
                          problemId={selectedProblem.id}
                          onCodeChange={setUserCode}
                          onSubmit={handleSubmission}
                          interviewMode={true}
                        />
                      ) : (
                        <LazyCodeEditor
                          problemId={selectedProblem.id}
                          onCodeChange={setUserCode}
                          onSubmit={handleSubmission}
                          readOnly={gatesEnabled && !gates.codeReady}
                        />
                      )}
                    </Suspense>

                    <Box sx={{ p: 3, pt: 0 }}>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="h6" gutterBottom>AI Code Review</Typography>
                      {aiReviewError && (
                        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setAiReviewError(null)}>
                          {aiReviewError}
                        </Alert>
                      )}
                      <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} md={8}>
                          <TextField
                            fullWidth
                            size="small"
                            label="Optional notes for reviewer (context, goals)"
                            value={reviewNotes}
                            onChange={(e) => setReviewNotes(e.target.value)}
                          />
                        </Grid>
                        <Grid item xs={12} md={4}>
                          <Button
                            variant="contained"
                            fullWidth
                            onClick={requestCodeReview}
                            disabled={!!aiLoading.review || !userCode.trim()}
                          >
                            {aiLoading.review ? 'Reviewing…' : 'Review My Code'}
                          </Button>
                        </Grid>
                        <Grid item xs={12}>
                          <FormControlLabel
                            control={<Switch checked={streaming} onChange={(e) => setStreaming(e.target.checked)} />}
                            label="Stream responses"
                          />
                        </Grid>
                      </Grid>
                      {aiReview && (
                        <Grid container spacing={2} sx={{ mt: 1 }}>
                          <Grid item xs={12} md={6}>
                            <Typography variant="subtitle2">Strengths</Typography>
                            {aiReview.strengths && aiReview.strengths.length > 0 ? (
                              <List>
                                {aiReview.strengths.map((s, i) => (
                                  <ListItem key={i}><ListItemText primary={s} /></ListItem>
                                ))}
                              </List>
                            ) : (
                              <Typography variant="body2" color="text.secondary">No strengths identified.</Typography>
                            )}
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <Typography variant="subtitle2">Suggestions</Typography>
                            {aiReview.suggestions && aiReview.suggestions.length > 0 ? (
                              <List>
                                {aiReview.suggestions.map((s, i) => (
                                  <ListItem key={i}><ListItemText primary={s} /></ListItem>
                                ))}
                              </List>
                            ) : (
                              <Typography variant="body2" color="text.secondary">No suggestions provided.</Typography>
                            )}
                          </Grid>
                          <Grid item xs={12}>
                            {(aiReview?.provider || aiReview?.model) && (
                              <Typography variant="caption" color="text.secondary">
                                Provider: {aiReview?.provider || '—'} • Model: {aiReview?.model || '—'}
                              </Typography>
                            )}
                          </Grid>
                        </Grid>
                      )}
                    </Box>
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
                                  <Typography variant="body2" color="text.secondary">
                                    {submission.timestamp.toLocaleTimeString()}
                                  </Typography>
                                </Grid>
                              </Grid>
                            </Paper>
                          ))}
                        </Box>
                      ) : (
                        <Typography color="text.secondary">
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
                        <Typography color="text.secondary">
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
                            <Suspense fallback={<Box sx={{ p: 2 }}><LinearProgress /></Box>}>
                              <LazyCodeEditor
                                initialCode={solution.code}
                                language={solution.language}
                                readOnly
                              />
                            </Suspense>
                            {solution.explanation && (
                              <Box mt={2}>
                                <Typography variant="body2" color="text.secondary">
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
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Select a problem to start practicing
                </Typography>
                <Typography variant="body2" color="text.secondary">
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
