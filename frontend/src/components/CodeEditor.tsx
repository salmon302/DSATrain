import React, { useState, useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  Alert,
  Chip,
  Grid,
  Paper,
  LinearProgress,
  CircularProgress,
  TextField,
} from '@mui/material';
import { PlayArrow, Stop, Fullscreen, FullscreenExit, Code, BugReport, Speed, CheckCircle, Cancel, Assessment, Memory, Timer } from '@mui/icons-material';

// Import the real execution API
import { 
  codeExecutionAPI, 
  ExecutionResult, 
  TestResult, 
  CodeAnalysisResult,
  TestCase,
  executionUtils 
} from '../services/codeExecutionAPI';

interface CodeEditorProps {
  problemId?: string;
  initialCode?: string;
  language?: string;
  onCodeChange?: (code: string) => void;
  onSubmit?: (code: string, language: string, analysis?: CodeAnalysisResult) => void;
  readOnly?: boolean;
}

// Remove the old TestCase interface since we're importing it from the API

const CodeEditor: React.FC<CodeEditorProps> = ({
  problemId,
  initialCode = '',
  language: initialLanguage = 'python',
  onCodeChange,
  onSubmit,
  readOnly = false,
}) => {
  const [code, setCode] = useState(initialCode);
  const [language, setLanguage] = useState(initialLanguage);
  const [isRunning, setIsRunning] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [output, setOutput] = useState('');
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [analysisResult, setAnalysisResult] = useState<CodeAnalysisResult | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [theme, setTheme] = useState<'vs-dark' | 'light'>('vs-dark');
  const [fontSize, setFontSize] = useState(14);
  // const [showSettings, setShowSettings] = useState(false);
  const [customInput, setCustomInput] = useState('');
  const [customTests, setCustomTests] = useState<TestCase[]>([]);
  const [newTestName, setNewTestName] = useState('Custom Case');
  const [newTestInput, setNewTestInput] = useState('');
  const [newTestExpected, setNewTestExpected] = useState<string | undefined>(undefined);
  
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);

  // Monaco editor options
  const editorOptions = {
    fontSize,
    minimap: { enabled: false },
    automaticLayout: true,
    scrollBeyondLastLine: false,
    wordWrap: 'on' as const,
    lineNumbers: 'on' as const,
    glyphMargin: true,
    folding: true,
    lineDecorationsWidth: 0,
    lineNumbersMinChars: 3,
    renderLineHighlight: 'all' as const,
    selectOnLineNumbers: true,
    roundedSelection: false,
    readOnly,
    cursorStyle: 'line' as const,
    tabSize: 4,
    insertSpaces: true,
  };

  // Language templates
  const languageTemplates = {
    python: `def solution():
    """
    Write your solution here
    """
    pass

# Test your solution
if __name__ == "__main__":
    result = solution()
    print(result)`,
    javascript: `function solution() {
    // Write your solution here
    return null;
}

// Test your solution
console.log(solution());`,
    java: `public class Solution {
    public static void main(String[] args) {
        Solution sol = new Solution();
        // Test your solution
        System.out.println(sol.solution());
    }
    
    public Object solution() {
        // Write your solution here
        return null;
    }
}`,
    cpp: `#include <iostream>
#include <vector>
#include <string>
using namespace std;

class Solution {
public:
    // Write your solution here
    void solution() {
        
    }
};

int main() {
    Solution sol;
    sol.solution();
    return 0;
}`
  };

  // Handle editor mount
  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
    
    // Configure themes
    monaco.editor.defineTheme('custom-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [],
      colors: {
        'editor.background': '#1e1e1e',
        'editor.foreground': '#d4d4d4',
        'editor.lineHighlightBackground': '#2d2d30',
        'editorLineNumber.foreground': '#858585',
        'editor.selectionBackground': '#264f78',
        'editor.inactiveSelectionBackground': '#3a3d41',
      }
    });
    
    // Set up auto-completion and IntelliSense
    if (language === 'python') {
    monaco.languages.registerCompletionItemProvider('python', {
        provideCompletionItems: (model: any, position: any) => {
      /* eslint-disable no-template-curly-in-string */
          const suggestions = [
            {
              label: 'def',
              kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: 'def ${1:function_name}(${2:parameters}):\n    ${3:pass}',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Function definition'
            },
            {
              label: 'for',
              kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: 'for ${1:item} in ${2:items}:\n    ${3:pass}',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'For loop'
            },
            {
              label: 'while',
              kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: 'while ${1:condition}:\n    ${2:pass}',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'While loop'
            },
            {
              label: 'if',
              kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: 'if ${1:condition}:\n    ${2:pass}',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'If statement'
            }
          ];
      /* eslint-enable no-template-curly-in-string */
      return { suggestions };
        }
      });
    }
  };

  // Handle code change
  const handleCodeChange = (newCode: string | undefined) => {
    const updatedCode = newCode || '';
    setCode(updatedCode);
    onCodeChange?.(updatedCode);
  };

  // Handle language change
  const handleLanguageChange = (newLanguage: string) => {
    setLanguage(newLanguage);
    if (!code.trim() || code === languageTemplates[language as keyof typeof languageTemplates]) {
      setCode(languageTemplates[newLanguage as keyof typeof languageTemplates] || '');
    }
  };

  // Run code with real execution
  const runCode = async () => {
    if (!code.trim()) {
      setOutput('Please enter some code to run.');
      return;
    }

    setIsRunning(true);
    setActiveTab(1); // Switch to output tab
    setOutput('Running code...\n');
    
    try {
      // Execute code with real API
      const result = await codeExecutionAPI.runCode(code, language, customInput);
      setExecutionResult(result);
      
      // Format output
      let outputText = '';
      if (result.success) {
        outputText = `✅ Execution successful!\n\n`;
        outputText += `Output:\n${result.stdout}\n`;
        outputText += `\n📊 Performance:\n`;
        outputText += `⏱️ Time: ${codeExecutionAPI.formatExecutionTime(result.execution_time_ms)}\n`;
        outputText += `💾 Memory: ${codeExecutionAPI.formatMemoryUsage(result.memory_usage_mb)}\n`;
      } else {
        outputText = `❌ Execution failed!\n\n`;
        if (result.timeout) {
          outputText += `⏰ Timeout: Code execution timed out\n`;
        } else {
          outputText += `Error:\n${result.stderr}\n`;
        }
        if (result.stdout) {
          outputText += `\nOutput before error:\n${result.stdout}\n`;
        }
        outputText += `\n📊 Performance:\n`;
        outputText += `⏱️ Time: ${codeExecutionAPI.formatExecutionTime(result.execution_time_ms)}\n`;
        outputText += `💾 Memory: ${codeExecutionAPI.formatMemoryUsage(result.memory_usage_mb)}\n`;
      }
      
      setOutput(outputText);
      
    } catch (error) {
      setOutput(`❌ Execution error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setExecutionResult(null);
    } finally {
      setIsRunning(false);
    }
  };

  // Run comprehensive analysis
  const runAnalysis = async () => {
    if (!code.trim()) {
      setOutput('Please enter some code to analyze.');
      return;
    }

    setIsAnalyzing(true);
    setActiveTab(2); // Switch to test results tab
    
    try {
      // Generate and run comprehensive analysis
      const analysis = await codeExecutionAPI.analyzeCode(code, language, undefined, customTests.length ? customTests : undefined);
      setAnalysisResult(analysis);
      setTestResults(analysis.test_results);
      
      // Update output with analysis summary
      const summary = executionUtils.calculatePerformanceScore(analysis.performance_metrics);
      let analysisOutput = `🔍 Code Analysis Complete!\n\n`;
      analysisOutput += `📊 Overall Performance Score: ${summary}/100\n`;
      analysisOutput += `🏆 Performance Grade: ${analysis.performance_metrics.performance_grade}\n`;
      analysisOutput += `✅ Test Success Rate: ${analysis.performance_metrics.success_rate * 100}%\n`;
      analysisOutput += `📝 Code Quality: ${analysis.code_quality.total_lines} lines, ${analysis.code_quality.comment_lines} comments\n`;
      
      if (analysis.suggestions.length > 0) {
        analysisOutput += `\n💡 Suggestions:\n`;
        analysis.suggestions.forEach(suggestion => {
          analysisOutput += `• ${suggestion}\n`;
        });
      }
      
      setOutput(analysisOutput);
      
    } catch (error) {
      setOutput(`❌ Analysis error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setAnalysisResult(null);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Submit code with analysis
  const submitCode = () => {
    onSubmit?.(code, language, analysisResult || undefined);
  };

  // Toggle fullscreen
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  // Reset code
  const resetCode = () => {
    setCode(languageTemplates[language as keyof typeof languageTemplates] || '');
  };

  useEffect(() => {
    if (initialCode && initialCode !== code) {
      setCode(initialCode);
    }
  }, [initialCode, code]);

  const editorContainer = (
    <Box sx={{ height: isFullscreen ? '100vh' : '60vh', position: 'relative' }}>
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          p: 1, 
          borderBottom: 1, 
          borderColor: 'divider',
          backgroundColor: 'background.paper'
        }}
      >
        <Box display="flex" gap={1} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Language</InputLabel>
            <Select
              value={language}
              onChange={(e) => handleLanguageChange(e.target.value as string)}
              disabled={readOnly}
            >
              <MenuItem value="python">Python</MenuItem>
              <MenuItem value="javascript">JavaScript</MenuItem>
              <MenuItem value="java">Java</MenuItem>
              <MenuItem value="cpp">C++</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 100 }}>
            <InputLabel>Theme</InputLabel>
            <Select
              value={theme}
              onChange={(e) => setTheme(e.target.value as 'vs-dark' | 'light')}
            >
              <MenuItem value="vs-dark">Dark</MenuItem>
              <MenuItem value="light">Light</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 80 }}>
            <InputLabel>Font Size</InputLabel>
            <Select
              value={fontSize}
              onChange={(e) => setFontSize(e.target.value as number)}
            >
              <MenuItem value={12}>12px</MenuItem>
              <MenuItem value={14}>14px</MenuItem>
              <MenuItem value={16}>16px</MenuItem>
              <MenuItem value={18}>18px</MenuItem>
            </Select>
          </FormControl>
        </Box>
        
        <Box display="flex" gap={1}>
          {!readOnly && (
            <>
              <Tooltip title="Run Code">
                <Button
                  variant="contained"
                  color="success"
                  startIcon={isRunning ? <Stop /> : <PlayArrow />}
                  onClick={runCode}
                  disabled={isRunning || isAnalyzing}
                  size="small"
                >
                  {isRunning ? 'Running...' : 'Run'}
                </Button>
              </Tooltip>
              
              <Tooltip title="Analyze Code">
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={isAnalyzing ? <Stop /> : <Assessment />}
                  onClick={runAnalysis}
                  disabled={isRunning || isAnalyzing}
                  size="small"
                >
                  {isAnalyzing ? 'Analyzing...' : 'Analyze'}
                </Button>
              </Tooltip>
              
              <Tooltip title="Reset Code">
                <Button
                  variant="outlined"
                  onClick={resetCode}
                  size="small"
                >
                  Reset
                </Button>
              </Tooltip>
              
              <Tooltip title="Submit Solution">
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<CheckCircle />}
                  onClick={submitCode}
                  size="small"
                  disabled={isRunning || isAnalyzing}
                >
                  Submit
                </Button>
              </Tooltip>
              
              {/* Loading indicator */}
              {(isRunning || isAnalyzing) && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={16} />
                  <Typography variant="body2">
                    {isRunning ? 'Executing...' : 'Analyzing...'}
                  </Typography>
                </Box>
              )}
            </>
          )}
          
          <Tooltip title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}>
            <IconButton onClick={toggleFullscreen} size="small">
              {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      
      <Editor
        height="calc(100% - 50px)"
        language={language}
        value={code}
        onChange={handleCodeChange}
        onMount={handleEditorDidMount}
        theme={theme === 'vs-dark' ? 'custom-dark' : 'light'}
        options={editorOptions}
      />
    </Box>
  );

  if (isFullscreen) {
    return (
      <Box sx={{ 
        position: 'fixed', 
        top: 0, 
        left: 0, 
        right: 0, 
        bottom: 0, 
        zIndex: 9999, 
        backgroundColor: 'background.default'
      }}>
        {editorContainer}
      </Box>
    );
  }

  return (
    <Card sx={{ mt: 2 }}>
      <CardContent sx={{ p: 0 }}>
        <Grid container>
          <Grid item xs={12} lg={8}>
            {editorContainer}
          </Grid>
          
          <Grid item xs={12} lg={4}>
            <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
              <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
                <Tab label="Console" icon={<Code />} />
                <Tab label="Test Results" icon={<Assessment />} />
                <Tab label="Performance" icon={<Speed />} />
                <Tab label="Tests" icon={<BugReport />} />
              </Tabs>
              
              <Box sx={{ flexGrow: 1, p: 2, overflow: 'auto' }}>
                {activeTab === 0 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Console Output
                    </Typography>
                    
                    {/* Custom Input Section */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Custom Input (optional):
                      </Typography>
                      <Paper variant="outlined" sx={{ p: 1 }}>
                        <textarea
                          value={customInput}
                          onChange={(e) => setCustomInput(e.target.value)}
                          placeholder="Enter input for your program..."
                          style={{
                            width: '100%',
                            minHeight: '60px',
                            border: 'none',
                            outline: 'none',
                            fontFamily: 'monospace',
                            fontSize: '13px',
                            resize: 'vertical'
                          }}
                        />
                      </Paper>
                    </Box>
                    
                    <Paper 
                      variant="outlined" 
                      sx={{ 
                        p: 2, 
                        backgroundColor: theme === 'vs-dark' ? '#1e1e1e' : '#f5f5f5',
                        color: theme === 'vs-dark' ? '#d4d4d4' : '#000',
                        fontFamily: 'monospace',
                        fontSize: '13px',
                        minHeight: '200px',
                        maxHeight: '400px',
                        overflow: 'auto'
                      }}
                    >
                      <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                        {output || 'Click "Run" to execute your code...'}
                      </pre>
                    </Paper>
                    
                    {/* Execution Result Summary */}
                    {executionResult && (
                      <Box sx={{ mt: 2 }}>
                        <Grid container spacing={2}>
                          <Grid item xs={6} md={3}>
                            <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
                              <Typography 
                                variant="h6" 
                                color={executionUtils.getExecutionStatusColor(executionResult)}
                              >
                                {executionResult.success ? '✅' : '❌'}
                              </Typography>
                              <Typography variant="caption">Status</Typography>
                            </Paper>
                          </Grid>
                          <Grid item xs={6} md={3}>
                            <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
                              <Typography variant="h6" color="primary">
                                <Timer sx={{ fontSize: 'inherit', mr: 0.5 }} />
                                {codeExecutionAPI.formatExecutionTime(executionResult.execution_time_ms)}
                              </Typography>
                              <Typography variant="caption">Time</Typography>
                            </Paper>
                          </Grid>
                          <Grid item xs={6} md={3}>
                            <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
                              <Typography variant="h6" color="secondary">
                                <Memory sx={{ fontSize: 'inherit', mr: 0.5 }} />
                                {codeExecutionAPI.formatMemoryUsage(executionResult.memory_usage_mb)}
                              </Typography>
                              <Typography variant="caption">Memory</Typography>
                            </Paper>
                          </Grid>
                          <Grid item xs={6} md={3}>
                            <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
                              <Typography variant="h6" color="warning.main">
                                {executionResult.return_code}
                              </Typography>
                              <Typography variant="caption">Exit Code</Typography>
                            </Paper>
                          </Grid>
                        </Grid>
                      </Box>
                    )}
                  </Box>
                )}
                
                {activeTab === 1 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Test Results
                    </Typography>
                    {testResults.length > 0 ? (
                      <Box>
                        {testResults.map((testResult, index) => (
                          <Paper 
                            key={index} 
                            variant="outlined" 
                            sx={{ 
                              p: 2, 
                              mb: 1,
                              backgroundColor: testResult.passed ? 'success.light' : 'error.light',
                              color: testResult.passed ? 'success.contrastText' : 'error.contrastText'
                            }}
                          >
                            <Box display="flex" alignItems="center" gap={1} mb={1}>
                              {testResult.passed ? <CheckCircle /> : <Cancel />}
                              <Typography variant="subtitle2">
                                {testResult.test_case.name} - Test Case {index + 1}
                              </Typography>
                              <Chip 
                                label={testResult.passed ? 'PASSED' : 'FAILED'} 
                                color={testResult.passed ? 'success' : 'error'}
                                size="small"
                              />
                              <Chip 
                                label={codeExecutionAPI.formatExecutionTime(testResult.result.execution_time_ms)}
                                color="default"
                                size="small"
                                icon={<Timer />}
                              />
                            </Box>
                            
                            {testResult.test_case.description && (
                              <Typography variant="body2" sx={{ mb: 1, fontStyle: 'italic' }}>
                                {testResult.test_case.description}
                              </Typography>
                            )}
                            
                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                              <strong>Input:</strong> {testResult.test_case.input}<br />
                              {testResult.test_case.expected_output && (
                                <>
                                  <strong>Expected:</strong> {testResult.test_case.expected_output}<br />
                                </>
                              )}
                              <strong>Actual Output:</strong> {testResult.result.stdout || '(no output)'}
                              {testResult.result.stderr && (
                                <>
                                  <br /><strong>Error:</strong> {testResult.result.stderr}
                                </>
                              )}
                            </Typography>
                          </Paper>
                        ))}
                        
                        <Box mt={2}>
                          <Typography variant="body1">
                            <strong>
                              {executionUtils.getTestSummary(testResults).passed} / {testResults.length} tests passed
                              {' '}({executionUtils.getTestSummary(testResults).successRate.toFixed(1)}% success rate)
                            </strong>
                          </Typography>
                        </Box>
                      </Box>
                    ) : (
                      <Typography color="text.secondary">
                        Click "Analyze" to run comprehensive tests...
                      </Typography>
                    )}
                  </Box>
                )}
                
                {activeTab === 2 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Performance Analysis
                    </Typography>
                    {analysisResult ? (
                      <Box>
                        {/* Performance Grade */}
                        <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
                          <Typography variant="subtitle1" gutterBottom>
                            Overall Performance Grade
                          </Typography>
                          <Box display="flex" alignItems="center" gap={2}>
                            <Typography 
                              variant="h2" 
                              color={codeExecutionAPI.getPerformanceGradeColor(analysisResult.performance_metrics.performance_grade)}
                            >
                              {analysisResult.performance_metrics.performance_grade}
                            </Typography>
                            <Box>
                              <Typography variant="body1">
                                Performance Score: {executionUtils.calculatePerformanceScore(analysisResult.performance_metrics)}/100
                              </Typography>
                              <LinearProgress 
                                variant="determinate" 
                                value={executionUtils.calculatePerformanceScore(analysisResult.performance_metrics)}
                                sx={{ width: 200, mt: 1 }}
                                color={codeExecutionAPI.getPerformanceGradeColor(analysisResult.performance_metrics.performance_grade)}
                              />
                            </Box>
                          </Box>
                        </Paper>
                        
                        {/* Performance Metrics */}
                        <Grid container spacing={2} sx={{ mb: 2 }}>
                          <Grid item xs={12} md={6}>
                            <Paper variant="outlined" sx={{ p: 2 }}>
                              <Typography variant="subtitle2" color="primary" gutterBottom>
                                Execution Performance
                              </Typography>
                              <Typography variant="body2">
                                Average Time: {codeExecutionAPI.formatExecutionTime(analysisResult.performance_metrics.average_execution_time_ms)}<br />
                                Max Time: {codeExecutionAPI.formatExecutionTime(analysisResult.performance_metrics.max_execution_time_ms)}<br />
                                Average Memory: {codeExecutionAPI.formatMemoryUsage(analysisResult.performance_metrics.average_memory_usage_mb)}<br />
                                Success Rate: {(analysisResult.performance_metrics.success_rate * 100).toFixed(1)}%
                              </Typography>
                            </Paper>
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <Paper variant="outlined" sx={{ p: 2 }}>
                              <Typography variant="subtitle2" color="primary" gutterBottom>
                                Code Quality
                              </Typography>
                              <Typography variant="body2">
                                Total Lines: {analysisResult.code_quality.total_lines}<br />
                                Code Lines: {analysisResult.code_quality.code_lines}<br />
                                Comments: {analysisResult.code_quality.comment_lines}<br />
                                Avg Line Length: {analysisResult.code_quality.average_line_length.toFixed(1)}
                              </Typography>
                            </Paper>
                          </Grid>
                        </Grid>
                        
                        {/* Suggestions */}
                        {analysisResult.suggestions.length > 0 && (
                          <Paper variant="outlined" sx={{ p: 2 }}>
                            <Typography variant="subtitle2" color="primary" gutterBottom>
                              💡 Improvement Suggestions
                            </Typography>
                            {analysisResult.suggestions.map((suggestion, index) => (
                              <Alert key={index} severity="info" sx={{ mb: 1 }}>
                                {suggestion}
                              </Alert>
                            ))}
                          </Paper>
                        )}
                      </Box>
                    ) : (
                      <Typography color="text.secondary">
                        Click "Analyze" to see detailed performance analysis...
                      </Typography>
                    )}
                  </Box>
                )}

                {activeTab === 3 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Test Case Composer
                    </Typography>
                    <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={4}>
                          <TextField
                            fullWidth
                            size="small"
                            label="Name"
                            value={newTestName}
                            onChange={(e) => setNewTestName(e.target.value)}
                          />
                        </Grid>
                        <Grid item xs={12} sm={8}>
                          <TextField
                            fullWidth
                            size="small"
                            label="Input"
                            placeholder="Raw stdin for your program"
                            value={newTestInput}
                            onChange={(e) => setNewTestInput(e.target.value)}
                          />
                        </Grid>
                        <Grid item xs={12}>
                          <TextField
                            fullWidth
                            size="small"
                            label="Expected Output (optional)"
                            placeholder="What should be printed"
                            value={newTestExpected ?? ''}
                            onChange={(e) => setNewTestExpected(e.target.value || undefined)}
                          />
                        </Grid>
                        <Grid item xs={12}>
                          <Button
                            variant="contained"
                            size="small"
                            startIcon={<BugReport />}
                            onClick={() => {
                              const newCase: TestCase = {
                                name: newTestName || `Case ${customTests.length + 1}`,
                                input: newTestInput,
                                expected_output: newTestExpected,
                              } as TestCase;
                              setCustomTests([...customTests, newCase]);
                              setNewTestInput('');
                            }}
                            disabled={!newTestInput.trim()}
                          >
                            Add Test
                          </Button>
                        </Grid>
                      </Grid>
                    </Paper>

                    {customTests.length === 0 ? (
                      <Typography color="text.secondary">No custom tests added yet.</Typography>
                    ) : (
                      <Box>
                        {customTests.map((tc, idx) => (
                          <Paper key={idx} variant="outlined" sx={{ p: 1, mb: 1 }}>
                            <Box display="flex" justifyContent="space-between" alignItems="center">
                              <Typography variant="subtitle2">{tc.name}</Typography>
                              <Button size="small" onClick={() => setCustomTests(customTests.filter((_, i) => i !== idx))}>Remove</Button>
                            </Box>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                              <strong>Input:</strong> {tc.input}
                              {tc.expected_output && (<><br/><strong>Expected:</strong> {tc.expected_output}</>)}
                            </Typography>
                          </Paper>
                        ))}
                        <Box mt={1}>
                          <Button variant="contained" size="small" onClick={runAnalysis} startIcon={<Assessment />}>Analyze with Custom Tests</Button>
                        </Box>
                      </Box>
                    )}
                  </Box>
                )}
              </Box>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default CodeEditor;
