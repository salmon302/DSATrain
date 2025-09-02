import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Tabs,
  Tab,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  Chip,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  ExpandMore,
  School,
  Code,
  Psychology,
  CheckCircle,
  LightbulbOutlined,
  TipsAndUpdates,
  SpeakerNotes,
  Assessment,
  BookmarkBorder,
} from '@mui/icons-material';

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

const GeneralInfoPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [showExample, setShowExample] = useState(false);
  const [currentExample, setCurrentExample] = useState('');

  const thinkingOutLoudStructure = [
    {
      phase: "Problem Understanding",
      duration: "2-3 minutes",
      actions: [
        "Read the problem statement carefully",
        "Identify input/output format",
        "Ask clarifying questions",
        "Restate the problem in your own words"
      ],
      example: `"Let me read through this problem... So I need to find two numbers in an array that add up to a target value. The input is an array of integers and a target integer. The output should be the indices of those two numbers. Can I assume there's always exactly one solution? Are there any constraints on the array size or values?"`
    },
    {
      phase: "Approach Planning",
      duration: "3-5 minutes", 
      actions: [
        "Discuss multiple approaches",
        "Explain trade-offs",
        "Choose the best approach",
        "Outline the algorithm steps"
      ],
      example: `"I can think of a few approaches: 1) Brute force with nested loops - O(n²) time but O(1) space, 2) Sort then use two pointers - O(n log n) time, or 3) Hash map approach - O(n) time and O(n) space. The hash map seems optimal for this problem because..."`
    },
    {
      phase: "Implementation",
      duration: "15-20 minutes",
      actions: [
        "Explain each line as you write",
        "Mention variable purposes",
        "Discuss edge cases while coding",
        "Keep the interviewer engaged"
      ],
      example: `"I'll start by creating a hash map to store the numbers I've seen... This 'complement' variable represents what number I need to find to reach the target... Now I'm checking if this complement already exists in my hash map..."`
    },
    {
      phase: "Testing & Validation", 
      duration: "5-8 minutes",
      actions: [
        "Walk through with the given example",
        "Test edge cases",
        "Verify the logic",
        "Discuss potential improvements"
      ],
      example: `"Let me trace through this with the example [2,7,11,15], target=9... When i=0, num=2, complement=7, 7 not in seen yet, so I add 2... When i=1, num=7, complement=2, and 2 is in seen at index 0, so I return [0,1]..."`
    },
    {
      phase: "Optimization Discussion",
      duration: "3-5 minutes",
      actions: [
        "Analyze time/space complexity",
        "Discuss alternative solutions", 
        "Consider follow-up scenarios",
        "Mention scalability concerns"
      ],
      example: `"The time complexity is O(n) since we iterate through the array once, and space complexity is O(n) for the hash map. If memory was a concern, we could sort first and use two pointers, trading time for space. For very large datasets, we might consider..."`
    }
  ];

  const googlePrinciples = [
    {
      title: "Think Out Loud Constantly",
      description: "Never code in silence. Explain every decision.",
      tips: [
        "Verbalize your thought process before writing code",
        "Explain why you chose specific data structures",
        "Mention trade-offs as you consider them",
        "Keep talking even during brief pauses"
      ]
    },
    {
      title: "Start with Clarification",
      description: "Understand the problem completely before coding.",
      tips: [
        "Ask about input constraints and edge cases",
        "Confirm expected output format",
        "Discuss assumptions you're making",
        "Restate the problem to ensure understanding"
      ]
    },
    {
      title: "Multiple Approaches",
      description: "Always discuss multiple solutions before implementing.",
      tips: [
        "Present brute force solution first",
        "Explain more optimal approaches",
        "Compare time/space complexity trade-offs",
        "Choose best approach with reasoning"
      ]
    },
    {
      title: "Clean, Readable Code",
      description: "Write code as if others will maintain it.",
      tips: [
        "Use meaningful variable and function names",
        "Add comments for complex logic",
        "Keep functions small and focused",
        "Follow consistent formatting"
      ]
    },
    {
      title: "Test and Validate",
      description: "Always test your solution thoroughly.",
      tips: [
        "Walk through with given examples",
        "Consider edge cases and test them",
        "Trace through your algorithm step by step",
        "Fix bugs by explaining your debugging process"
      ]
    }
  ];

  const pythonQuickReference = {
    dataStructures: [
      {
        type: "Lists (Arrays)",
        syntax: "arr = [1, 2, 3]",
        operations: [
          "arr.append(4)  # Add to end",
          "arr.insert(0, 0)  # Insert at index",
          "arr.pop()  # Remove last",
          "arr.remove(2)  # Remove value",
          "len(arr)  # Length",
          "arr[0]  # Access by index",
          "arr[-1]  # Last element"
        ]
      },
      {
        type: "Dictionaries (Hash Maps)",
        syntax: "d = {'key': 'value'}",
        operations: [
          "d['new_key'] = 'new_value'  # Add/update",
          "value = d.get('key', default)  # Safe access",
          "'key' in d  # Check existence",
          "d.pop('key')  # Remove and return",
          "d.keys()  # Get all keys",
          "d.values()  # Get all values",
          "d.items()  # Get key-value pairs"
        ]
      },
      {
        type: "Sets",
        syntax: "s = {1, 2, 3} or set()",
        operations: [
          "s.add(4)  # Add element",
          "s.remove(2)  # Remove element",
          "s.discard(5)  # Remove if exists",
          "4 in s  # Check membership",
          "s1.union(s2)  # Union",
          "s1.intersection(s2)  # Intersection"
        ]
      }
    ],
    commonPatterns: [
      {
        pattern: "Two Pointers",
        code: `def two_pointers(arr, target):
    left, right = 0, len(arr) - 1
    while left < right:
        current_sum = arr[left] + arr[right]
        if current_sum == target:
            return [left, right]
        elif current_sum < target:
            left += 1
        else:
            right -= 1
    return []`,
        when: "Sorted arrays, palindromes, pair problems, target sum",
        complexity: "Time: O(n), Space: O(1)"
      },
      {
        pattern: "Sliding Window (Fixed Size)",
        code: `def sliding_window_fixed(arr, k):
    if len(arr) < k:
        return []
    
    window_sum = sum(arr[:k])
    max_sum = window_sum
    
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i-k]
        max_sum = max(max_sum, window_sum)
    
    return max_sum`,
        when: "Fixed-size subarray/substring problems",
        complexity: "Time: O(n), Space: O(1)"
      },
      {
        pattern: "Sliding Window (Variable Size)",
        code: `def sliding_window_variable(arr, target):
    left = 0
    current_sum = 0
    min_length = float('inf')
    
    for right in range(len(arr)):
        current_sum += arr[right]
        
        while current_sum >= target:
            min_length = min(min_length, right - left + 1)
            current_sum -= arr[left]
            left += 1
    
    return min_length if min_length != float('inf') else 0`,
        when: "Variable size subarray/substring problems",
        complexity: "Time: O(n), Space: O(1)"
      },
      {
        pattern: "Binary Search",
        code: `def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2  # Avoid overflow
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1  # Not found`,
        when: "Sorted data, search problems, optimization",
        complexity: "Time: O(log n), Space: O(1)"
      },
      {
        pattern: "DFS (Recursive)",
        code: `def dfs(node, visited, graph, result):
    if node in visited:
        return
    
    visited.add(node)
    result.append(node)  # Process current node
    
    for neighbor in graph.get(node, []):
        dfs(neighbor, visited, graph, result)

# Usage example
visited = set()
result = []
dfs(start_node, visited, graph, result)`,
        when: "Trees, graphs, backtracking, path finding",
        complexity: "Time: O(V + E), Space: O(V) for recursion stack"
      },
      {
        pattern: "BFS (Iterative)",
        code: `from collections import deque

def bfs(start, graph):
    queue = deque([start])
    visited = {start}
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)  # Process current node
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return result`,
        when: "Shortest path, level-order traversal, minimum steps",
        complexity: "Time: O(V + E), Space: O(V) for queue"
      },
      {
        pattern: "Dynamic Programming (1D)",
        code: `def dp_1d(n):
    # Base cases
    if n <= 1:
        return n
    
    # DP array
    dp = [0] * (n + 1)
    dp[0], dp[1] = 0, 1
    
    # Fill DP table
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]  # Recurrence relation
    
    return dp[n]`,
        when: "Optimization problems, counting problems, Fibonacci-like",
        complexity: "Time: O(n), Space: O(n) - can optimize to O(1)"
      },
      {
        pattern: "Dynamic Programming (2D)",
        code: `def dp_2d(m, n):
    # Create DP table
    dp = [[0] * n for _ in range(m)]
    
    # Initialize base cases
    for i in range(m):
        dp[i][0] = 1
    for j in range(n):
        dp[0][j] = 1
    
    # Fill DP table
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]
    
    return dp[m-1][n-1]`,
        when: "Grid problems, path counting, string matching",
        complexity: "Time: O(m*n), Space: O(m*n)"
      },
      {
        pattern: "Backtracking",
        code: `def backtrack(current_path, remaining_choices, result):
    # Base case - found valid solution
    if is_valid_solution(current_path):
        result.append(current_path[:])  # Make a copy
        return
    
    # Try each possible choice
    for choice in remaining_choices:
        # Make choice
        current_path.append(choice)
        new_choices = get_next_choices(remaining_choices, choice)
        
        # Recurse
        backtrack(current_path, new_choices, result)
        
        # Backtrack (undo choice)
        current_path.pop()`,
        when: "Permutations, combinations, sudoku, N-Queens",
        complexity: "Time: O(b^d) where b=branching factor, d=depth"
      }
    ],
    builtInFunctions: [
      "max(arr), min(arr)  # Find maximum/minimum",
      "sum(arr)  # Sum all elements", 
      "sorted(arr)  # Return sorted copy",
      "arr.sort()  # Sort in place",
      "enumerate(arr)  # Get (index, value) pairs",
      "zip(arr1, arr2)  # Combine arrays",
      "range(start, stop, step)  # Generate numbers",
      "map(func, arr)  # Apply function to all",
      "filter(func, arr)  # Filter by condition",
      "any(arr), all(arr)  # Boolean operations",
      "reversed(arr)  # Reverse iterator",
      "len(obj)  # Length of object",
      "abs(x)  # Absolute value",
      "divmod(a, b)  # Division and remainder",
      "pow(x, y)  # x to the power of y"
    ],
    commonImports: [
      "from collections import deque, defaultdict, Counter",
      "import heapq  # For priority queues",
      "import bisect  # For binary search in sorted lists",
      "import itertools  # For permutations, combinations",
      "import math  # For mathematical functions",
      "import sys  # For sys.maxsize (infinity)",
      "from functools import lru_cache  # For memoization"
    ],
    complexityReference: {
      "O(1)": "Constant - dictionary lookup, array access",
      "O(log n)": "Logarithmic - binary search, balanced tree operations",
      "O(n)": "Linear - single loop, linear search",
      "O(n log n)": "Linearithmic - merge sort, heap sort",
      "O(n²)": "Quadratic - nested loops, bubble sort",
      "O(n³)": "Cubic - triple nested loops",
      "O(2^n)": "Exponential - recursive Fibonacci, subset generation",
      "O(n!)": "Factorial - permutation generation"
    }
  };

  const communicationExamples = [
    {
      situation: "Starting the Problem",
      poor: "Let me think... *silence for 30 seconds*",
      good: "Let me read through this problem carefully. I need to find two numbers that sum to a target. Let me think about different approaches - I could use a brute force nested loop, or maybe a hash map for O(n) time..."
    },
    {
      situation: "Choosing Data Structure",
      poor: "*writes code* I'll use a dictionary.",
      good: "I'm choosing a dictionary here because I need O(1) lookups to check if the complement exists. This will give me O(n) time complexity instead of O(n²) with nested loops."
    },
    {
      situation: "Writing a Loop",
      poor: "*silently writes for loop*",
      good: "I'm iterating through the array with enumerate to get both the index and value. For each number, I'll calculate what its complement should be..."
    },
    {
      situation: "Handling Edge Cases",
      poor: "This should work for most cases.",
      good: "Let me consider edge cases: what if the array is empty? What if no solution exists? The problem states there's always exactly one solution, so I don't need to handle the no-solution case."
    },
    {
      situation: "Testing Solution",
      poor: "Looks right to me.",
      good: "Let me trace through the example [2,7,11,15] with target 9. When i=0, num=2, complement=7. 7 isn't in seen yet, so I add 2→0. When i=1, num=7, complement=2. 2 is in seen at index 0, so I return [0,1]. Perfect!"
    }
  ];

  const showExampleDialog = (example: string) => {
    setCurrentExample(example);
    setShowExample(true);
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" gutterBottom>
          📚 Interview Preparation Guide
        </Typography>
  <Typography variant="h6" color="text.secondary" gutterBottom>
          Master the art of thinking out loud and Google-style problem solving
        </Typography>
        <Alert severity="info" sx={{ mt: 2 }}>
          <strong>💡 Pro Tip:</strong> Practice these techniques regularly with the Google Interview Mode in our code editor!
        </Alert>
      </Box>

      {/* Main Tabs */}
      <Card>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} variant="fullWidth">
          <Tab label="Thinking Out Loud" icon={<Psychology />} />
          <Tab label="Google Principles" icon={<School />} />
          <Tab label="Python Quick Reference" icon={<Code />} />
          <Tab label="Communication Examples" icon={<SpeakerNotes />} />
        </Tabs>

        <CardContent>
          {/* Tab 1: Thinking Out Loud Structure */}
          <TabPanel value={activeTab} index={0}>
            <Typography variant="h5" gutterBottom>
              🗣️ Structured Thinking Out Loud Framework
            </Typography>
            <Typography variant="body1" paragraph>
              Google interviews are as much about communication as problem-solving. Here's a proven framework 
              for thinking out loud that demonstrates your analytical process:
            </Typography>

            {thinkingOutLoudStructure.map((phase, index) => (
              <Accordion key={index} sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Chip 
                      label={`${index + 1}`} 
                      color="primary" 
                      size="small" 
                    />
                    <Typography variant="h6">
                      {phase.phase}
                    </Typography>
                    <Chip 
                      label={phase.duration} 
                      color="secondary" 
                      variant="outlined" 
                      size="small" 
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        Key Actions:
                      </Typography>
                      <List dense>
                        {phase.actions.map((action, idx) => (
                          <ListItem key={idx}>
                            <ListItemIcon>
                              <CheckCircle color="success" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText primary={action} />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        Example Communication:
                      </Typography>
                      <Paper 
                        variant="outlined" 
                        sx={{ p: 2, backgroundColor: 'grey.50', fontStyle: 'italic' }}
                      >
                        <Typography variant="body2">
                          "{phase.example}"
                        </Typography>
                      </Paper>
                      <Button 
                        size="small" 
                        onClick={() => showExampleDialog(phase.example)}
                        sx={{ mt: 1 }}
                      >
                        View Full Example
                      </Button>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}

            <Alert severity="success" sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                🎯 Remember: The goal is to make your thought process transparent!
              </Typography>
              <Typography variant="body2">
                Interviewers want to understand how you think, not just see the final solution. 
                Even if you get stuck, clear communication can demonstrate your problem-solving approach.
              </Typography>
            </Alert>
          </TabPanel>

          {/* Tab 2: Google Principles */}
          <TabPanel value={activeTab} index={1}>
            <Typography variant="h5" gutterBottom>
              🎯 Google Interview Principles
            </Typography>
            <Typography variant="body1" paragraph>
              These principles reflect Google's evaluation criteria and what they value in candidates:
            </Typography>

            <Grid container spacing={3}>
              {googlePrinciples.map((principle, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card variant="outlined" sx={{ height: '100%' }}>
                    <CardContent>
                      <Box display="flex" alignItems="center" gap={1} mb={2}>
                        <LightbulbOutlined color="primary" />
                        <Typography variant="h6">
                          {principle.title}
                        </Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {principle.description}
                      </Typography>
                      <Typography variant="subtitle2" gutterBottom>
                        Implementation Tips:
                      </Typography>
                      <List dense>
                        {principle.tips.map((tip, idx) => (
                          <ListItem key={idx} sx={{ pl: 0 }}>
                            <ListItemIcon sx={{ minWidth: 30 }}>
                              <TipsAndUpdates fontSize="small" color="action" />
                            </ListItemIcon>
                            <ListItemText 
                              primary={tip}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>

            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                📊 Google's Four Evaluation Criteria:
              </Typography>
              <Typography variant="body2">
                <strong>GCA (General Cognitive Ability):</strong> Problem-solving and analytical thinking<br />
                <strong>RRK (Role-Related Knowledge):</strong> Technical competency and coding skills<br />
                <strong>Communication:</strong> Ability to explain ideas clearly and collaborate<br />
                <strong>Googleyness:</strong> Cultural fit, growth mindset, and engineering excellence
              </Typography>
            </Alert>
          </TabPanel>

          {/* Tab 3: Python Quick Reference */}
          <TabPanel value={activeTab} index={2}>
            <Typography variant="h5" gutterBottom>
              🐍 Python Quick Reference for Interviews
            </Typography>

            {/* Data Structures */}
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Data Structures
            </Typography>
            <Grid container spacing={2}>
              {pythonQuickReference.dataStructures.map((ds, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom color="primary">
                        {ds.type}
                      </Typography>
                      <Paper sx={{ p: 1, backgroundColor: 'grey.100', mb: 2 }}>
                        <Typography variant="body2" fontFamily="monospace">
                          {ds.syntax}
                        </Typography>
                      </Paper>
                      <Typography variant="subtitle2" gutterBottom>
                        Common Operations:
                      </Typography>
                      {ds.operations.map((op, idx) => (
                        <Typography 
                          key={idx} 
                          variant="body2" 
                          fontFamily="monospace" 
                          fontSize="0.8rem"
                          sx={{ mb: 0.5 }}
                        >
                          {op}
                        </Typography>
                      ))}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>

            {/* Common Patterns */}
            <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
              Common Algorithm Patterns
            </Typography>
            {pythonQuickReference.commonPatterns.map((pattern, index) => (
              <Accordion key={index} sx={{ mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
                    <Typography variant="subtitle1" fontWeight="bold">
                      {pattern.pattern}
                    </Typography>
                    <Chip label={pattern.when} size="small" variant="outlined" />
                    {pattern.complexity && (
                      <Chip 
                        label={pattern.complexity} 
                        size="small" 
                        color="secondary" 
                        variant="filled" 
                      />
                    )}
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Paper 
                    variant="outlined" 
                    sx={{ p: 2, backgroundColor: 'grey.50' }}
                  >
                    <Typography 
                      variant="body2" 
                      fontFamily="monospace" 
                      whiteSpace="pre-wrap"
                    >
                      {pattern.code}
                    </Typography>
                  </Paper>
                </AccordionDetails>
              </Accordion>
            ))}

            {/* Built-in Functions */}
            <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
              Essential Built-in Functions
            </Typography>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Grid container spacing={2}>
                {pythonQuickReference.builtInFunctions.map((func, index) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <Typography 
                      variant="body2" 
                      fontFamily="monospace"
                      sx={{ mb: 1 }}
                    >
                      {func}
                    </Typography>
                  </Grid>
                ))}
              </Grid>
            </Paper>

            {/* Common Imports */}
            <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
              Essential Imports for Interviews
            </Typography>
            <Paper variant="outlined" sx={{ p: 2 }}>
              {pythonQuickReference.commonImports.map((imp, index) => (
                <Typography 
                  key={index}
                  variant="body2" 
                  fontFamily="monospace"
                  sx={{ mb: 1 }}
                >
                  {imp}
                </Typography>
              ))}
            </Paper>

            {/* Complexity Reference */}
            <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
              Time Complexity Reference
            </Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Complexity</strong></TableCell>
                    <TableCell><strong>Description & Examples</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(pythonQuickReference.complexityReference).map(([complexity, description]) => (
                    <TableRow key={complexity}>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace" fontWeight="bold">
                          {complexity}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {description}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="body2">
                <strong>💡 Pro Tip:</strong> Always analyze and state your solution's time and space complexity 
                at the end of your implementation. It's a great way to demonstrate your understanding!
              </Typography>
            </Alert>
          </TabPanel>

          {/* Tab 4: Communication Examples */}
          <TabPanel value={activeTab} index={3}>
            <Typography variant="h5" gutterBottom>
              💬 Communication Examples: Good vs Poor
            </Typography>
            <Typography variant="body1" paragraph>
              Learn from these examples of how to communicate effectively during coding interviews:
            </Typography>

            {communicationExamples.map((example, index) => (
              <Card key={index} variant="outlined" sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="primary">
                    {example.situation}
                  </Typography>
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Box sx={{ p: 2, backgroundColor: 'error.light', borderRadius: 1 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          ❌ Poor Communication:
                        </Typography>
                        <Typography 
                          variant="body2" 
                          fontStyle="italic"
                          color="error.dark"
                        >
                          "{example.poor}"
                        </Typography>
                      </Box>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <Box sx={{ p: 2, backgroundColor: 'success.light', borderRadius: 1 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          ✅ Good Communication:
                        </Typography>
                        <Typography 
                          variant="body2" 
                          fontStyle="italic"
                          color="success.dark"
                        >
                          "{example.good}"
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            ))}

            <Alert severity="warning" sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                ⚠️ Common Communication Mistakes to Avoid:
              </Typography>
              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                <li>Long periods of silence while thinking</li>
                <li>Writing code without explaining the approach first</li>
                <li>Not asking clarifying questions</li>
                <li>Giving up too quickly when stuck</li>
                <li>Not testing the solution with examples</li>
                <li>Ignoring the interviewer's hints or questions</li>
              </ul>
            </Alert>
          </TabPanel>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Grid container spacing={2} justifyContent="center">
          <Grid item>
            <Button
              variant="contained"
              size="large"
              startIcon={<Code />}
              href="/practice"
            >
              Practice with Google Interview Mode
            </Button>
          </Grid>
          <Grid item>
            <Button
              variant="outlined"
              size="large"
              startIcon={<Assessment />}
              href="/analytics"
            >
              View Your Progress
            </Button>
          </Grid>
          <Grid item>
            <Button
              variant="outlined"
              size="large"
              startIcon={<BookmarkBorder />}
              onClick={() => {
                const content = document.documentElement.outerHTML;
                const blob = new Blob([content], { type: 'text/html' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'interview-guide.html';
                a.click();
              }}
            >
              Save Guide Offline
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Example Dialog */}
      <Dialog 
        open={showExample} 
        onClose={() => setShowExample(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          💬 Communication Example
        </DialogTitle>
        <DialogContent>
          <Paper variant="outlined" sx={{ p: 3, backgroundColor: 'grey.50' }}>
            <Typography variant="body1" fontStyle="italic">
              "{currentExample}"
            </Typography>
          </Paper>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowExample(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default GeneralInfoPage;
