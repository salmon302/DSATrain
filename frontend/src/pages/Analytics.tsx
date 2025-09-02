import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Box,
  Typography,
  Alert,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  TrendingUp,
  Speed,
  Star,
  Timeline,
  Assessment,
  Psychology,
  Refresh,
  Quiz,
  CheckCircle,
  AccessTime,
  EmojiEvents,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

import { 
  trackingAPI, 
  statsAPI, 
  getCurrentUserId,
  UserAnalytics 
} from '../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
  </div>
);

const Analytics: React.FC = () => {
  const [userAnalytics, setUserAnalytics] = useState<UserAnalytics | null>(null);
  const [platformStats, setPlatformStats] = useState<any>(null);
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [timeRange, setTimeRange] = useState(30); // days

  const userId = getCurrentUserId();

  // Load analytics data
  const loadAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [userData, platformData, trendsData] = await Promise.all([
        trackingAPI.getUserAnalytics(userId, timeRange),
        statsAPI.getPlatformAnalytics(),
        trackingAPI.getTrends(7) // Last 7 days for trends
      ]);

      setUserAnalytics(userData.user_analytics);
      setPlatformStats(platformData.platform_analytics);
      setTrends(trendsData.trends);

    } catch (err: any) {
      console.error('Error loading analytics:', err);
      setError('Failed to load analytics data. Please check if the API server is running.');
    } finally {
      setLoading(false);
    }
  }, [userId, timeRange]);

  // Handle time range change
  const handleTimeRangeChange = (newRange: number) => {
    setTimeRange(newRange);
  };

  // Chart colors
  const COLORS = useMemo(() => ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1'], []);

  // Format numbers
  const formatNumber = useCallback((num: number) => {
    return new Intl.NumberFormat().format(num);
  }, []);

  // Format percentage
  const formatPercentage = useCallback((num: number) => {
    return `${(num * 100).toFixed(1)}%`;
  }, []);

  // Format time duration
  const formatDuration = useCallback((seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  }, []);

  useEffect(() => {
    void loadAnalytics();
  }, [loadAnalytics]);

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            📊 Analytics Dashboard
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Comprehensive insights into your learning journey and platform performance
          </Typography>
        </Box>
        
        <Box display="flex" gap={2} alignItems="center">
          <FormControl variant="outlined" size="small">
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => handleTimeRangeChange(e.target.value as number)}
              label="Time Range"
            >
              <MenuItem value={7}>Last 7 days</MenuItem>
              <MenuItem value={30}>Last 30 days</MenuItem>
              <MenuItem value={90}>Last 90 days</MenuItem>
              <MenuItem value={365}>Last year</MenuItem>
            </Select>
          </FormControl>
          <Tooltip title="Refresh Data">
            <IconButton onClick={() => void loadAnalytics()}>
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

      {/* Tabs */}
      <Tabs value={selectedTab} onChange={(_, newValue) => setSelectedTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Personal Analytics" icon={<Timeline />} />
        <Tab label="Platform Insights" icon={<AnalyticsIcon />} />
        <Tab label="Learning Trends" icon={<TrendingUp />} />
        <Tab label="Performance Metrics" icon={<Assessment />} />
      </Tabs>

      {/* Personal Analytics Tab */}
      <TabPanel value={selectedTab} index={0}>
        {userAnalytics ? (
          <Grid container spacing={3}>
            {/* Key Metrics Cards */}
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Avatar sx={{ bgcolor: 'primary.main' }}>
                      <Quiz />
                    </Avatar>
                    <Box>
                      <Typography variant="h4" fontWeight="bold">
                        {formatNumber(userAnalytics.activity_summary?.unique_problems || 0)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Problems Engaged
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Avatar sx={{ bgcolor: 'success.main' }}>
                      <CheckCircle />
                    </Avatar>
                    <Box>
                      <Typography variant="h4" fontWeight="bold">
                        {formatNumber(userAnalytics.problem_solving_stats?.solved || 0)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Problems Solved
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Avatar sx={{ bgcolor: 'warning.main' }}>
                      <Speed />
                    </Avatar>
                    <Box>
                      <Typography variant="h4" fontWeight="bold">
                        {formatPercentage(userAnalytics.problem_solving_stats?.success_rate || 0)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Success Rate
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Avatar sx={{ bgcolor: 'info.main' }}>
                      <AccessTime />
                    </Avatar>
                    <Box>
                      <Typography variant="h4" fontWeight="bold">
                        {formatDuration(userAnalytics.problem_solving_stats?.average_solve_time || 0)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Avg Solve Time
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Learning Patterns */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Learning Consistency
                  </Typography>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <LinearProgress
                      variant="determinate"
                      value={userAnalytics.learning_patterns?.consistency_score * 100 || 0}
                      sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="body2" fontWeight="bold">
                      {formatPercentage(userAnalytics.learning_patterns?.consistency_score || 0)}
                    </Typography>
                  </Box>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Active Days
                      </Typography>
                      <Typography variant="h6">
                        {userAnalytics.learning_patterns?.active_days || 0} / {userAnalytics.learning_patterns?.total_days_period || 0}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Daily Avg Interactions
                      </Typography>
                      <Typography variant="h6">
                        {formatNumber(userAnalytics.learning_patterns?.average_daily_interactions || 0)}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Activity Breakdown */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Activity Breakdown
                  </Typography>
                  {userAnalytics.activity_summary?.actions && (
                    <ResponsiveContainer width="100%" height={200}>
                      <PieChart>
                        <Pie
                          data={Object.entries(userAnalytics.activity_summary.actions).map(([action, count]) => ({
                            name: action,
                            value: count
                          }))}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                          label
                        >
                          {Object.entries(userAnalytics.activity_summary.actions).map((_, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <RechartsTooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Most Common Actions */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Activity Summary
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          <EmojiEvents />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary="Most Common Action"
                        secondary={userAnalytics.activity_summary?.most_common_action || 'N/A'}
                      />
                      <ListItemSecondaryAction>
                        <Chip 
                          label={`${userAnalytics.total_interactions || 0} total`}
                          color="primary"
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                    <Divider variant="inset" component="li" />
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: 'secondary.main' }}>
                          <Quiz />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary="Unique Problems Engaged"
                        secondary={`${userAnalytics.activity_summary?.unique_problems || 0} different problems`}
                      />
                      <ListItemSecondaryAction>
                        <Chip 
                          label={`${userAnalytics.activity_summary?.unique_sessions || 0} sessions`}
                          color="secondary"
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        ) : (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 6 }}>
              <Psychology sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No personal analytics available yet
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Start solving problems to see your learning analytics and progress.
              </Typography>
            </CardContent>
          </Card>
        )}
      </TabPanel>

      {/* Platform Insights Tab */}
      <TabPanel value={selectedTab} index={1}>
        {platformStats ? (
          <Grid container spacing={3}>
            {/* Platform Distribution Chart */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Problems by Platform
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={platformStats}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="platform" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="problem_count" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Quality Metrics Chart */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Quality Metrics by Platform
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={platformStats}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="platform" />
                      <YAxis />
                      <RechartsTooltip />
                      <Line 
                        type="monotone" 
                        dataKey="average_quality_score" 
                        stroke="#8884d8" 
                        name="Quality Score"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="average_google_relevance" 
                        stroke="#82ca9d" 
                        name="Google Relevance"
                      />
                      <Legend />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Platform Statistics Table */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Platform Statistics
                  </Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Platform</TableCell>
                          <TableCell align="right">Problems</TableCell>
                          <TableCell align="right">Avg Quality</TableCell>
                          <TableCell align="right">Google Relevance</TableCell>
                          <TableCell align="right">Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {platformStats.map((platform: any) => (
                          <TableRow key={platform.platform}>
                            <TableCell component="th" scope="row">
                              <Box display="flex" alignItems="center" gap={1}>
                                <Avatar sx={{ width: 24, height: 24, fontSize: 12 }}>
                                  {platform.platform[0].toUpperCase()}
                                </Avatar>
                                {platform.platform}
                              </Box>
                            </TableCell>
                            <TableCell align="right">
                              {formatNumber(platform.problem_count)}
                            </TableCell>
                            <TableCell align="right">
                              <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                                <Star sx={{ fontSize: 16, color: 'gold' }} />
                                {platform.average_quality_score.toFixed(1)}
                              </Box>
                            </TableCell>
                            <TableCell align="right">
                              {platform.average_google_relevance.toFixed(1)}%
                            </TableCell>
                            <TableCell align="right">
                              <Chip 
                                label={platform.problem_count > 0 ? 'Active' : 'Inactive'}
                                color={platform.problem_count > 0 ? 'success' : 'default'}
                                size="small"
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        ) : (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 6 }}>
              <AnalyticsIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No platform statistics available
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Platform analytics will appear once data is loaded.
              </Typography>
            </CardContent>
          </Card>
        )}
      </TabPanel>

      {/* Learning Trends Tab */}
      <TabPanel value={selectedTab} index={2}>
        {trends ? (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Platform Trends (Last 7 Days)
                  </Typography>
                  {/* Example chart using aggregated trends */}
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={Array.isArray(trends) ? trends : []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Area type="monotone" dataKey="interactions" stroke="#8884d8" fill="#8884d8" name="Interactions" />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        ) : (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 6 }}>
              <TrendingUp sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No trending data available
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Trend analysis will appear as users engage with the platform.
              </Typography>
            </CardContent>
          </Card>
        )}
      </TabPanel>

      {/* Performance Metrics Tab */}
      <TabPanel value={selectedTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Insights
                </Typography>
                <Alert severity="info">
                  Advanced performance metrics including solve time analysis, difficulty progression,
                  and skill development tracking will be available in the next update.
                </Alert>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
};

export default Analytics;
