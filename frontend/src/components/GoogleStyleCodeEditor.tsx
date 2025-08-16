import React, { useState, useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Timer,
  Assessment,
  School,
  Code,
  Psychology,
  Send,
  Lightbulb,
  CheckCircle,
  Cancel,
  Warning,
  Speed,
  ExpandMore,
} from '@mui/icons-material';

import { googleCodeAnalysisAPI, CodeAnalysisResult, analysisUtils } from '../services/googleCodeAnalysisAPI';
import InterviewPressureSimulator from './InterviewPressureSimulator';

interface GoogleStyleCodeEditorProps {
  problemId?: string;
  initialCode?: string;
  language?: string;
  onCodeChange?: (code: string) => void;
  onSubmit?: (code: string, language: string, analysis: CodeAnalysis) => void;
  readOnly?: boolean;
  interviewMode?: boolean;
}

interface CodeAnalysis {
  complexity: {
    time: string;
    space: string;
    confidence: number;
  };
  codeQuality: {
    score: number;
    factors: {
      readability: number;
      naming: number;
      structure: number;
      comments: number;
    };
  };
  googleCriteria: {
    gca: number; // General Cognitive Ability
    rrk: number; // Role-Related Knowledge
    communication: number;
    overall: number;
  };
  suggestions: string[];
  testCases: Array<{
    input: string;
    expected: string;
    actual?: string;
    passed?: boolean;
  }>;
}

const GoogleStyleCodeEditor: React.FC<GoogleStyleCodeEditorProps> = ({
  problemId,
  initialCode = '',
  language: initialLanguage = 'python',
  onCodeChange,
  onSubmit,
  readOnly = false,
  interviewMode = false,
}) => {
  const [code, setCode] = useState(initialCode);
  const [language, setLanguage] = useState(initialLanguage);
  const [isRunning, setIsRunning] = useState(false);
  const [analysis, setAnalysis] = useState<CodeAnalysis | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [interviewTimer, setInterviewTimer] = useState(0);
  const [isTimerActive, setIsTimerActive] = useState(false);
  const [googleDocMode, setGoogleDocMode] = useState(interviewMode);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [communicationNotes, setCommunicationNotes] = useState<string[]>([]);
  const [thinkingOutLoud, setThinkingOutLoud] = useState(false);
  const [interviewPressure, setInterviewPressure] = useState(1); // 1-5 scale
  const [keyPressCount, setKeyPressCount] = useState(0);
  const [typingSpeed, setTypingSpeed] = useState(0); // WPM
  const [focusTime, setFocusTime] = useState(0); // Time with editor in focus
  const [lastKeystroke, setLastKeystroke] = useState<number>(Date.now());
  const [isTyping, setIsTyping] = useState(false);
  const [showInterviewTips, setShowInterviewTips] = useState(false);
  
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Google Doc Style Editor Options (Minimal features to simulate interview environment)
  const googleDocEditorOptions = {
    fontSize: 14,
    minimap: { enabled: false },
    automaticLayout: true,
    scrollBeyondLastLine: false,
    wordWrap: 'on' as const,
    lineNumbers: 'off' as const, // No line numbers like Google Doc
    glyphMargin: false,
    folding: false,
    lineDecorationsWidth: 0,
    renderLineHighlight: 'none' as const,
    selectOnLineNumbers: false,
    roundedSelection: false,
    readOnly,
    cursorStyle: 'line' as const,
    tabSize: 4,
    insertSpaces: true,
    // Disable advanced features to simulate interview constraints
    quickSuggestions: false,
    parameterHints: { enabled: false },
    suggestOnTriggerCharacters: false,
    acceptSuggestionOnEnter: 'off' as const,
    tabCompletion: 'off' as const,
    wordBasedSuggestions: 'off' as const,
    contextmenu: false, // Disable right-click menu
    hover: { enabled: false }, // Disable hover information
    // Lightbulb setting removed to satisfy monaco types in current version
    // Remove syntax highlighting in strict mode
    theme: googleDocMode ? 'google-doc-plain' : 'vs-dark',
    // Disable autocomplete completely
    suggest: { 
      showMethods: false,
      showFunctions: false,
      showConstructors: false,
      showFields: false,
      showVariables: false,
      showClasses: false,
      showStructs: false,
      showInterfaces: false,
      showModules: false,
      showProperties: false,
      showEvents: false,
      showOperators: false,
      showUnits: false,
      showValues: false,
      showConstants: false,
      showEnums: false,
      showEnumMembers: false,
      showKeywords: false,
      showWords: false,
      showColors: false,
      showFiles: false,
      showReferences: false,
      showFolders: false,
      showTypeParameters: false,
      showSnippets: false,
      showUsers: false,
      showIssues: false
    }
  };

  // Standard Editor Options (Full IDE features)
  const standardEditorOptions = {
    fontSize: 14,
    minimap: { enabled: true },
    automaticLayout: true,
    scrollBeyondLastLine: false,
    wordWrap: 'on' as const,
    lineNumbers: 'on' as const,
    glyphMargin: true,
    folding: true,
    lineDecorationsWidth: 10,
    renderLineHighlight: 'all' as const,
    selectOnLineNumbers: true,
    roundedSelection: false,
    readOnly,
    cursorStyle: 'line' as const,
    tabSize: 4,
    insertSpaces: true,
    theme: 'vs-dark',
  };

  // Timer functionality for interview simulation
  useEffect(() => {
    if (isTimerActive && !readOnly) {
      timerRef.current = setInterval(() => {
        setInterviewTimer((prev) => prev + 1);
      }, 1000);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isTimerActive, readOnly]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Handle editor mount with Google-specific configurations
  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
    
    // Define Google Doc plain theme (minimal highlighting)
    monaco.editor.defineTheme('google-doc-plain', {
      base: 'vs',
      inherit: false,
      rules: [
        { token: '', foreground: '000000' },
        { token: 'comment', foreground: '666666', fontStyle: 'italic' },
        { token: 'string', foreground: '000000' },
        { token: 'keyword', foreground: '000000' },
        { token: 'number', foreground: '000000' },
        { token: 'operator', foreground: '000000' },
        { token: 'delimiter', foreground: '000000' },
      ],
      colors: {
        'editor.background': '#ffffff',
        'editor.foreground': '#000000',
        'editor.lineHighlightBackground': '#ffffff',
        'editorLineNumber.foreground': '#cccccc',
        'editor.selectionBackground': '#b3d9ff',
        'editor.inactiveSelectionBackground': '#e5e5e5',
        'editorCursor.foreground': '#000000',
        'editor.findMatchBackground': '#ffff00',
        'editor.findMatchHighlightBackground': '#ffff0050',
      }
    });

    // Disable most IntelliSense features in Google Doc mode
    if (googleDocMode) {
      monaco.languages.typescript.typescriptDefaults.setCompilerOptions({
        noSemanticValidation: true,
        noSyntaxValidation: true,
      });
      
      // Add focus tracking for interview mode
      editor.onDidFocusEditorWidget(() => {
        if (googleDocMode) {
          setFocusTime(prev => prev + 1);
        }
      });
      
      // Add keystroke tracking
      editor.onDidChangeModelContent((e: any) => {
        if (googleDocMode && e.changes.length > 0) {
          setKeyPressCount(prev => prev + e.changes.length);
        }
      });
    }
  };

  // Advanced code analysis using Google's criteria
  const analyzeCode = async (codeToAnalyze: string): Promise<CodeAnalysis> => {
    try {
      // Use the real Google code analysis API
      const result = await googleCodeAnalysisAPI.analyzeCode({
        code: codeToAnalyze,
        language,
        problem_id: problemId,
        time_spent_seconds: interviewTimer,
        thinking_out_loud: thinkingOutLoud,
        communication_notes: communicationNotes
      });

      // Convert API result to our CodeAnalysis interface
      return {
        complexity: {
          time: result.complexity.time_complexity,
          space: result.complexity.space_complexity,
          confidence: result.complexity.confidence,
        },
        codeQuality: {
          score: result.quality.overall_score,
          factors: {
            readability: result.quality.readability,
            naming: result.quality.naming_conventions,
            structure: result.quality.code_structure,
            comments: result.quality.documentation,
          },
        },
        googleCriteria: {
          gca: result.google_criteria.gca_score,
          rrk: result.google_criteria.rrk_score,
          communication: result.google_criteria.communication_score,
          overall: result.google_criteria.overall_score,
        },
        suggestions: result.suggestions,
        testCases: result.test_results.map(test => ({
          input: test.input,
          expected: test.expected,
          actual: test.actual,
          passed: test.passed,
        })),
      };
    } catch (error) {
      console.error('Code analysis failed:', error);
      
      // Fallback to mock analysis if API fails
      return mockAnalyzeCode(codeToAnalyze);
    }
  };

  // Fallback mock analysis (original implementation)
  const mockAnalyzeCode = async (codeToAnalyze: string): Promise<CodeAnalysis> => {
    // Simulate comprehensive analysis based on Google's evaluation criteria
    await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate processing time
    
    // Calculate complexity analysis
    const lines = codeToAnalyze.split('\n').filter(line => line.trim().length > 0);
    const hasNestedLoops = /for.*for|while.*while|for.*while|while.*for/.test(codeToAnalyze);
    const hasRecursion = /def\s+\w+.*\w+\(/.test(codeToAnalyze) && codeToAnalyze.includes('return');
    
    let timeComplexity = 'O(n)';
    let spaceComplexity = 'O(1)';
    
    if (hasNestedLoops) {
      timeComplexity = 'O(n²)';
    } else if (hasRecursion) {
      timeComplexity = 'O(2^n)';
      spaceComplexity = 'O(n)';
    }

    // Code quality analysis based on Google's standards
    const variableNaming = /^[a-z_][a-z0-9_]*$/.test(codeToAnalyze) ? 85 : 60;
    const hasComments = codeToAnalyze.includes('#') || codeToAnalyze.includes('//') || codeToAnalyze.includes('"""');
    const functionLength = lines.length <= 20 ? 90 : 70;
    const readabilityScore = lines.length < 50 ? 85 : 65;

    const codeQualityScore = Math.round((variableNaming + functionLength + readabilityScore + (hasComments ? 90 : 60)) / 4);

    // Google evaluation criteria
    const gca = Math.round((timeComplexity === 'O(n)' ? 90 : timeComplexity === 'O(n²)' ? 75 : 60));
    const rrk = Math.round(codeQualityScore * 0.9);
    const communication = thinkingOutLoud ? 85 : 60;
    const overall = Math.round((gca + rrk + communication) / 3);

    // Generate suggestions based on Google's code review standards
    const suggestions = [];
    if (!hasComments) {
      suggestions.push("Add comments explaining your approach (Google values clear communication)");
    }
    if (lines.length > 30) {
      suggestions.push("Consider breaking down into smaller functions (Google prefers modular code)");
    }
    if (timeComplexity !== 'O(n)' && timeComplexity !== 'O(log n)') {
      suggestions.push("Can you optimize the time complexity? Google interviews focus heavily on efficiency");
    }
    if (!thinkingOutLoud) {
      suggestions.push("Remember to explain your thought process out loud during interviews");
    }

    // Mock test cases
    const testCases = [
      { input: '[1,2,3]', expected: '[1,2,3]', actual: '[1,2,3]', passed: true },
      { input: '[4,5,6]', expected: '[4,5,6]', actual: '[4,5,6]', passed: true },
      { input: '[]', expected: '[]', actual: '[]', passed: true },
      { input: '[1]', expected: '[1]', actual: '[1]', passed: true },
    ];

    return {
      complexity: {
        time: timeComplexity,
        space: spaceComplexity,
        confidence: 0.85,
      },
      codeQuality: {
        score: codeQualityScore,
        factors: {
          readability: readabilityScore,
          naming: variableNaming,
          structure: functionLength,
          comments: hasComments ? 90 : 60,
        },
      },
      googleCriteria: {
        gca,
        rrk,
        communication,
        overall,
      },
      suggestions,
      testCases,
    };
  };

  // Handle code change with enhanced tracking
  const handleCodeChange = (newCode: string | undefined) => {
    const updatedCode = newCode || '';
    setCode(updatedCode);
    onCodeChange?.(updatedCode);
    
    // Track typing metrics in interview mode
    if (googleDocMode) {
      const now = Date.now();
      setKeyPressCount(prev => prev + 1);
      
      // Calculate typing speed (rough estimation)
      if (keyPressCount > 0 && interviewTimer > 0) {
        const words = updatedCode.split(/\s+/).length;
        const minutes = interviewTimer / 60;
        const wpm = Math.round(words / Math.max(minutes, 0.1));
        setTypingSpeed(wpm);
      }
      
      // Track keystroke timing
      if (now - lastKeystroke < 5000) { // If typing within 5 seconds
        setIsTyping(true);
      } else {
        setIsTyping(false);
      }
      setLastKeystroke(now);
      
      // Auto-add communication notes for significant changes
      if (updatedCode.length > code.length + 10) { // Significant addition
        addCommunicationNote("Added significant code block");
      }
    }
  };

  // Run comprehensive analysis
  const runAnalysis = async () => {
    setIsRunning(true);
    try {
      const result = await analyzeCode(code);
      setAnalysis(result);
      setShowAnalysis(true);
      setActiveTab(1);
    } catch (error) {
      console.error('Analysis error:', error);
    } finally {
      setIsRunning(false);
    }
  };

  // Submit with Google-style evaluation
  const submitSolution = () => {
    if (analysis) {
      onSubmit?.(code, language, analysis);
    }
  };

  // Add communication note
  const addCommunicationNote = (note: string) => {
    setCommunicationNotes(prev => [...prev, `${formatTime(interviewTimer)}: ${note}`]);
  };

  // Insert code template
  const insertCodeTemplate = (template: string) => {
    if (editorRef.current) {
      const selection = editorRef.current.getSelection();
      editorRef.current.executeEdits('insert-template', [{
        range: selection,
        text: template
      }]);
      addCommunicationNote("Used code template");
    }
  };

  // Get code templates based on language
  const getCodeTemplates = () => {
    const templates: Record<string, Record<string, string>> = {
      python: {
        'Two Pointers': `# Two pointers approach
left, right = 0, len(arr) - 1
while left < right:
    # Process current state
    if condition:
        left += 1
    else:
        right -= 1`,
        'Binary Search': `# Binary search template
left, right = 0, len(arr) - 1
while left <= right:
    mid = (left + right) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
return -1`,
        'DFS Template': `# DFS recursive template
def dfs(node, visited):
    if node in visited:
        return
    
    visited.add(node)
    # Process current node
    
    for neighbor in graph[node]:
        dfs(neighbor, visited)`,
        'Dynamic Programming': `# DP template
dp = [0] * (n + 1)
dp[0] = base_case

for i in range(1, n + 1):
    for prev in range(i):
        dp[i] = max(dp[i], dp[prev] + transition)

return dp[n]`
      },
      javascript: {
        'Two Pointers': `// Two pointers approach
let left = 0, right = arr.length - 1;
while (left < right) {
    // Process current state
    if (condition) {
        left++;
    } else {
        right--;
    }
}`,
        'Binary Search': `// Binary search template
let left = 0, right = arr.length - 1;
while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    if (arr[mid] === target) {
        return mid;
    } else if (arr[mid] < target) {
        left = mid + 1;
    } else {
        right = mid - 1;
    }
}
return -1;`
      }
    };
    
    return templates[language] || {};
  };

  // Google Doc mode toggle
  const toggleGoogleDocMode = () => {
    setGoogleDocMode(!googleDocMode);
    if (!googleDocMode) {
      setIsTimerActive(true);
      addCommunicationNote("Switched to Google Doc interview mode");
    }
  };

  return (
    <Card sx={{ mt: 2 }}>
      <CardContent sx={{ p: 0 }}>
        {/* Header with controls */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          p: 2, 
          borderBottom: 1, 
          borderColor: 'divider',
          backgroundColor: googleDocMode ? '#f8f9fa' : 'background.paper'
        }}>
          <Box display="flex" gap={2} alignItems="center">
            <FormControlLabel
              control={
                <Switch
                  checked={googleDocMode}
                  onChange={toggleGoogleDocMode}
                  color="primary"
                />
              }
              label="Google Interview Mode"
            />
            
            {googleDocMode && (
              <>
                <Chip
                  icon={<Timer />}
                  label={formatTime(interviewTimer)}
                  color={interviewTimer > 2700 ? "error" : interviewTimer > 1800 ? "warning" : "primary"}
                  variant="outlined"
                />
                
                <Chip
                  icon={<Speed />}
                  label={`${typingSpeed} WPM`}
                  color="secondary"
                  size="small"
                />
                
                <Chip
                  label={`Pressure: ${'⭐'.repeat(interviewPressure)}`}
                  color="warning"
                  size="small"
                  onClick={() => setInterviewPressure(prev => prev % 5 + 1)}
                  sx={{ cursor: 'pointer' }}
                />
              </>
            )}

            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Language</InputLabel>
              <Select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                disabled={readOnly}
              >
                <MenuItem value="python">Python</MenuItem>
                <MenuItem value="javascript">JavaScript</MenuItem>
                <MenuItem value="java">Java</MenuItem>
                <MenuItem value="cpp">C++</MenuItem>
              </Select>
            </FormControl>
          </Box>

          <Box display="flex" gap={1} alignItems="center">
            {googleDocMode && (
              <Button
                variant="outlined"
                size="small"
                startIcon={<Lightbulb />}
                onClick={() => setShowInterviewTips(!showInterviewTips)}
              >
                Tips
              </Button>
            )}
            
            <FormControlLabel
              control={
                <Switch
                  checked={thinkingOutLoud}
                  onChange={(e) => setThinkingOutLoud(e.target.checked)}
                  color="secondary"
                />
              }
              label="Thinking Out Loud"
            />
            
            <Button
              variant="contained"
              color="primary"
              startIcon={<Assessment />}
              onClick={runAnalysis}
              disabled={isRunning || !code.trim()}
            >
              {isRunning ? 'Analyzing...' : 'Analyze Code'}
            </Button>

            {analysis && (
              <Button
                variant="contained"
                color="success"
                startIcon={<Send />}
                onClick={submitSolution}
              >
                Submit Solution
              </Button>
            )}
          </Box>
        </Box>

        {/* Interview Tips Panel */}
        {googleDocMode && showInterviewTips && (
          <Box sx={{ p: 2, backgroundColor: '#e3f2fd', borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6" gutterBottom>
              🎯 Google Interview Tips
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" gutterBottom>
                  <strong>During Coding:</strong>
                </Typography>
                <ul style={{ margin: 0, paddingLeft: '20px' }}>
                  <li>Think out loud constantly</li>
                  <li>Explain your approach before coding</li>
                  <li>Discuss time and space complexity</li>
                  <li>Consider edge cases</li>
                </ul>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" gutterBottom>
                  <strong>Best Practices:</strong>
                </Typography>
                <ul style={{ margin: 0, paddingLeft: '20px' }}>
                  <li>Write clean, readable code</li>
                  <li>Use meaningful variable names</li>
                  <li>Test with examples</li>
                  <li>Ask clarifying questions</li>
                </ul>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Main editor and analysis panels */}
        <Grid container>
          <Grid item xs={12} lg={showAnalysis ? 8 : 12}>
            <Box sx={{ height: '60vh' }}>
              <Editor
                height="100%"
                language={language}
                value={code}
                onChange={handleCodeChange}
                onMount={handleEditorDidMount}
                options={googleDocMode ? googleDocEditorOptions : standardEditorOptions}
              />
            </Box>
          </Grid>

          {showAnalysis && (
            <Grid item xs={12} lg={4}>
              <Box sx={{ height: '60vh', display: 'flex', flexDirection: 'column', borderLeft: 1, borderColor: 'divider' }}>
                <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
                  <Tab label="Analysis" icon={<Assessment />} />
                  <Tab label="Google Criteria" icon={<School />} />
                  <Tab label="Communication" icon={<Psychology />} />
                  <Tab label="Templates" icon={<Code />} />
                  <Tab label="Pressure" icon={<Warning />} />
                </Tabs>

                <Box sx={{ flexGrow: 1, p: 2, overflow: 'auto' }}>
                  {activeTab === 0 && analysis && (
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Code Analysis
                      </Typography>
                      
                      <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
                        <Typography variant="subtitle2" color="primary">
                          Complexity Analysis
                        </Typography>
                        <Typography variant="body2">
                          Time: {analysis.complexity.time}<br />
                          Space: {analysis.complexity.space}<br />
                          Confidence: {(analysis.complexity.confidence * 100).toFixed(1)}%
                        </Typography>
                      </Paper>

                      <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
                        <Typography variant="subtitle2" color="primary">
                          Code Quality: {analysis.codeQuality.score}/100
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          {Object.entries(analysis.codeQuality.factors).map(([factor, score]) => (
                            <Box key={factor} display="flex" justifyContent="space-between">
                              <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                                {factor}:
                              </Typography>
                              <Typography variant="body2" color={score >= 80 ? 'success.main' : score >= 60 ? 'warning.main' : 'error.main'}>
                                {score}/100
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      </Paper>

                      {analysis.suggestions.length > 0 && (
                        <Paper variant="outlined" sx={{ p: 2 }}>
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            <Lightbulb sx={{ mr: 1, verticalAlign: 'middle' }} />
                            Improvement Suggestions
                          </Typography>
                          {analysis.suggestions.map((suggestion, index) => (
                            <Alert key={index} severity="info" sx={{ mb: 1 }}>
                              {suggestion}
                            </Alert>
                          ))}
                        </Paper>
                      )}
                    </Box>
                  )}

                  {activeTab === 1 && analysis && (
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Google Evaluation Criteria
                      </Typography>
                      
                      <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
                        <Typography variant="subtitle2" color="primary">
                          Overall Score: {analysis.googleCriteria.overall}/100
                        </Typography>
                        <Box sx={{ mt: 2 }}>
                          <Box display="flex" justifyContent="space-between" mb={1}>
                            <Typography variant="body2">General Cognitive Ability (GCA):</Typography>
                            <Chip 
                              label={`${analysis.googleCriteria.gca}/100`}
                              color={analysis.googleCriteria.gca >= 80 ? 'success' : analysis.googleCriteria.gca >= 60 ? 'warning' : 'error'}
                              size="small"
                            />
                          </Box>
                          <Box display="flex" justifyContent="space-between" mb={1}>
                            <Typography variant="body2">Role-Related Knowledge (RRK):</Typography>
                            <Chip 
                              label={`${analysis.googleCriteria.rrk}/100`}
                              color={analysis.googleCriteria.rrk >= 80 ? 'success' : analysis.googleCriteria.rrk >= 60 ? 'warning' : 'error'}
                              size="small"
                            />
                          </Box>
                          <Box display="flex" justifyContent="space-between" mb={1}>
                            <Typography variant="body2">Communication:</Typography>
                            <Chip 
                              label={`${analysis.googleCriteria.communication}/100`}
                              color={analysis.googleCriteria.communication >= 80 ? 'success' : analysis.googleCriteria.communication >= 60 ? 'warning' : 'error'}
                              size="small"
                            />
                          </Box>
                        </Box>
                      </Paper>

                      <Alert severity={analysis.googleCriteria.overall >= 80 ? 'success' : analysis.googleCriteria.overall >= 60 ? 'warning' : 'error'}>
                        {analysis.googleCriteria.overall >= 80 
                          ? 'Strong performance! This solution meets Google\'s high standards.'
                          : analysis.googleCriteria.overall >= 60 
                          ? 'Good solution with room for improvement. Focus on communication and optimization.'
                          : 'Needs significant improvement. Review algorithm efficiency and code quality.'}
                      </Alert>
                    </Box>
                  )}

                  {activeTab === 2 && (
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Communication & Interview Metrics
                      </Typography>
                      
                      {/* Real-time metrics */}
                      <Grid container spacing={2} sx={{ mb: 3 }}>
                        <Grid item xs={6} md={3}>
                          <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
                            <Typography variant="h6" color="primary">
                              {typingSpeed}
                            </Typography>
                            <Typography variant="caption">WPM</Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={6} md={3}>
                          <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
                            <Typography variant="h6" color="secondary">
                              {keyPressCount}
                            </Typography>
                            <Typography variant="caption">Keystrokes</Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={6} md={3}>
                          <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
                            <Typography variant="h6" color="warning.main">
                              {Math.round(focusTime / 60)}
                            </Typography>
                            <Typography variant="caption">Focus Time (min)</Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={6} md={3}>
                          <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
                            <Typography variant="h6" color={isTyping ? "success.main" : "text.secondary"}>
                              {isTyping ? "Active" : "Paused"}
                            </Typography>
                            <Typography variant="caption">Status</Typography>
                          </Paper>
                        </Grid>
                      </Grid>
                      
                      <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                        <Button 
                          size="small" 
                          onClick={() => addCommunicationNote("Explained my approach")}
                          disabled={!thinkingOutLoud}
                        >
                          + Explained Approach
                        </Button>
                        <Button 
                          size="small" 
                          onClick={() => addCommunicationNote("Asked clarifying question")}
                          disabled={!thinkingOutLoud}
                        >
                          + Asked Question
                        </Button>
                        <Button 
                          size="small" 
                          onClick={() => addCommunicationNote("Discussed time complexity")}
                          disabled={!thinkingOutLoud}
                        >
                          + Discussed Complexity
                        </Button>
                        <Button 
                          size="small" 
                          onClick={() => addCommunicationNote("Mentioned edge cases")}
                          disabled={!thinkingOutLoud}
                        >
                          + Edge Cases
                        </Button>
                        <Button 
                          size="small" 
                          onClick={() => addCommunicationNote("Tested with example")}
                          disabled={!thinkingOutLoud}
                        >
                          + Tested Example
                        </Button>
                      </Box>

                      {!thinkingOutLoud && (
                        <Alert severity="warning" sx={{ mb: 2 }}>
                          <strong>Remember:</strong> Enable "Thinking Out Loud" to track communication during coding. 
                          This is crucial for Google interviews!
                        </Alert>
                      )}

                      <Paper variant="outlined" sx={{ p: 2, maxHeight: '300px', overflow: 'auto' }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Communication Timeline
                        </Typography>
                        {communicationNotes.length > 0 ? (
                          communicationNotes.map((note, index) => (
                            <Box key={index} sx={{ 
                              mb: 1, 
                              p: 1, 
                              backgroundColor: index % 2 === 0 ? 'grey.50' : 'background.paper',
                              borderRadius: 1
                            }}>
                              <Typography variant="body2">
                                {note}
                              </Typography>
                            </Box>
                          ))
                        ) : (
                          <Typography variant="body2" color="textSecondary">
                            Communication notes will appear here as you interact during the interview simulation...
                          </Typography>
                        )}
                      </Paper>

                      {/* Interview pressure simulation */}
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Interview Pressure Simulation
                        </Typography>
                        <Box display="flex" alignItems="center" gap={2}>
                          <Typography variant="body2">Pressure Level:</Typography>
                          {[1, 2, 3, 4, 5].map((level) => (
                            <Chip
                              key={level}
                              label={`Level ${level}`}
                              color={interviewPressure === level ? "primary" : "default"}
                              onClick={() => setInterviewPressure(level)}
                              size="small"
                              clickable
                            />
                          ))}
                        </Box>
                        <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                          Higher pressure levels simulate interview stress and time constraints
                        </Typography>
                      </Box>
                    </Box>
                  )}

                  {activeTab === 3 && (
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Code Templates & Patterns
                      </Typography>
                      
                      <Alert severity="info" sx={{ mb: 2 }}>
                        💡 Click on any template to insert it at your cursor position. 
                        These are common patterns frequently used in Google interviews.
                      </Alert>

                      <Grid container spacing={2}>
                        {Object.entries(getCodeTemplates()).map(([name, template]) => (
                          <Grid item xs={12} md={6} key={name}>
                            <Card 
                              variant="outlined" 
                              sx={{ 
                                cursor: 'pointer',
                                '&:hover': { backgroundColor: 'action.hover' }
                              }}
                              onClick={() => insertCodeTemplate(template)}
                            >
                              <CardContent sx={{ p: 2 }}>
                                <Typography variant="subtitle2" gutterBottom>
                                  {name}
                                </Typography>
                                <Paper 
                                  variant="outlined" 
                                  sx={{ 
                                    p: 1, 
                                    backgroundColor: 'grey.50',
                                    fontSize: '0.75rem',
                                    fontFamily: 'monospace',
                                    overflow: 'auto',
                                    maxHeight: '120px'
                                  }}
                                >
                                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                                    {template.substring(0, 150)}
                                    {template.length > 150 ? '...' : ''}
                                  </pre>
                                </Paper>
                                <Button 
                                  size="small" 
                                  sx={{ mt: 1 }}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    insertCodeTemplate(template);
                                  }}
                                >
                                  Insert Template
                                </Button>
                              </CardContent>
                            </Card>
                          </Grid>
                        ))}
                      </Grid>

                      {Object.keys(getCodeTemplates()).length === 0 && (
                        <Typography variant="body2" color="textSecondary" textAlign="center" sx={{ py: 4 }}>
                          No templates available for {language}. 
                          Switch to Python or JavaScript to see available templates.
                        </Typography>
                      )}
                    </Box>
                  )}

                  {activeTab === 4 && (
                    <Box>
                      <InterviewPressureSimulator
                        pressureLevel={interviewPressure}
                        timeElapsed={interviewTimer}
                        isActive={googleDocMode && isTimerActive}
                        onPressureChange={setInterviewPressure}
                      />
                    </Box>
                  )}
                </Box>
              </Box>
            </Grid>
          )}
        </Grid>

        {googleDocMode && (
          <Box sx={{ p: 2, backgroundColor: 'warning.light', borderTop: 1, borderColor: 'divider' }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              <strong>🎯 Google Interview Simulation Active</strong><br />
              • Minimal editor features enabled (no autocomplete, syntax highlighting, or IntelliSense)<br />
              • Focus on problem-solving, clear communication, and writing clean, efficient code<br />
              • Timer: {formatTime(interviewTimer)} | Typing Speed: {typingSpeed} WPM | Pressure Level: {interviewPressure}/5<br />
              {!thinkingOutLoud && "⚠️ Remember to explain your thought process out loud!"}
            </Alert>
            
            {interviewTimer > 2700 && ( // 45 minutes
              <Alert severity="warning">
                <strong>⏰ Time Alert:</strong> You're approaching the typical 45-minute Google interview limit. 
                Consider wrapping up and discussing optimizations.
              </Alert>
            )}
            
            {interviewPressure >= 4 && (
              <Alert severity="error" sx={{ mt: 1 }}>
                <strong>💥 High Pressure Mode:</strong> Simulating intense interview conditions. 
                Stay calm, think clearly, and communicate your approach step by step.
              </Alert>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default GoogleStyleCodeEditor;
