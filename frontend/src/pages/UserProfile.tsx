import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Alert,
  Card,
  CardContent,
  Grid,
  Avatar,
  Chip,
  Button,
  LinearProgress,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tab,
  Tabs,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Person,
  Edit,
  Save,
  Cancel,
  Settings,
  EmojiEvents,
  TrendingUp,
  Star,
  Psychology,
  School,
  Code,
  Timer,
  Assessment,
  Insights,
  NotificationsActive,
  Security,
  Palette,
  Language,
  ExpandMore,
  GitHub,
  LinkedIn,
  Email,
  Phone,
  LocationOn,
} from '@mui/icons-material';

import { 
  trackingAPI, 
  getCurrentUserId,
  UserAnalytics
} from '../services/api';

interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  location?: string;
  bio?: string;
  githubUsername?: string;
  linkedinProfile?: string;
  preferences: {
    difficulty_preference: string;
    focus_areas: string[];
    study_hours_per_week: number;
    notification_preferences: {
      email_notifications: boolean;
      push_notifications: boolean;
      weekly_summary: boolean;
      recommendation_updates: boolean;
    };
    learning_style: string;
    target_companies: string[];
  };
  achievements: Achievement[];
  statistics: {
    problems_solved: number;
    current_streak: number;
    longest_streak: number;
    total_study_time: number;
    favorite_topics: string[];
    skill_levels: { [topic: string]: number };
  };
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  earned_date: string;
  category: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

const UserProfile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [userAnalytics, setUserAnalytics] = useState<UserAnalytics | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [editedProfile, setEditedProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [showAchievements, setShowAchievements] = useState(false);

  const userId = getCurrentUserId();

  // Load user profile and analytics
  const loadUserData = async () => {
    try {
      setLoading(true);

      // Load user analytics
      const analyticsResponse = await trackingAPI.getUserAnalytics(userId, 30);
      setUserAnalytics(analyticsResponse.user_analytics);

      // Create mock profile (in real app, this would come from a user service)
      const mockProfile: UserProfile = {
        id: userId,
        name: 'DSA Learner',
        email: 'learner@dsatrain.com',
        location: 'San Francisco, CA',
        bio: 'Passionate software engineer preparing for tech interviews and competitive programming.',
        githubUsername: 'dsalearner',
        linkedinProfile: 'dsalearner',
        preferences: {
          difficulty_preference: 'medium',
          focus_areas: ['Dynamic Programming', 'Trees', 'Graphs'],
          study_hours_per_week: 10,
          notification_preferences: {
            email_notifications: true,
            push_notifications: true,
            weekly_summary: true,
            recommendation_updates: true
          },
          learning_style: 'visual',
          target_companies: ['Google', 'Meta', 'Amazon']
        },
        achievements: generateMockAchievements(),
        statistics: {
          problems_solved: analyticsResponse.user_analytics?.problem_solving_stats?.solved || 0,
          current_streak: 5,
          longest_streak: 12,
          total_study_time: 150, // hours
          favorite_topics: ['Arrays', 'Hash Maps', 'Binary Trees'],
          skill_levels: {
            'Arrays': 85,
            'Strings': 78,
            'Trees': 72,
            'Graphs': 65,
            'Dynamic Programming': 58,
            'Backtracking': 45
          }
        }
      };

      setProfile(mockProfile);
      setEditedProfile(mockProfile);

    } catch (error) {
      console.error('Error loading user data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Generate mock achievements
  const generateMockAchievements = (): Achievement[] => [
    {
      id: '1',
      title: 'First Steps',
      description: 'Solved your first problem',
      icon: '🎯',
      earned_date: '2024-01-15',
      category: 'milestone',
      rarity: 'common'
    },
    {
      id: '2',
      title: 'Problem Solver',
      description: 'Solved 10 problems',
      icon: '🧩',
      earned_date: '2024-01-20',
      category: 'milestone',
      rarity: 'common'
    },
    {
      id: '3',
      title: 'Streak Master',
      description: 'Maintained a 7-day streak',
      icon: '🔥',
      earned_date: '2024-01-25',
      category: 'consistency',
      rarity: 'rare'
    },
    {
      id: '4',
      title: 'Algorithm Expert',
      description: 'Mastered Dynamic Programming',
      icon: '🎓',
      earned_date: '2024-02-01',
      category: 'skill',
      rarity: 'epic'
    }
  ];

  // Handle profile save
  const handleSaveProfile = () => {
    if (editedProfile) {
      setProfile(editedProfile);
      setEditMode(false);
      // In real app, would save to backend
    }
  };

  // Handle cancel edit
  const handleCancelEdit = () => {
    setEditedProfile(profile);
    setEditMode(false);
  };

  // Get achievement rarity color
  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return '#9E9E9E';
      case 'rare': return '#2196F3';
      case 'epic': return '#9C27B0';
      case 'legendary': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  // Get skill level color
  const getSkillLevelColor = (level: number) => {
    if (level >= 80) return 'success';
    if (level >= 60) return 'warning';
    return 'error';
  };

  useEffect(() => {
    loadUserData();
  }, []);

  if (loading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>Loading Profile...</Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (!profile) {
    return (
      <Alert severity="error">
        Failed to load user profile. Please try again.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          👤 User Profile
        </Typography>
        <Button
          variant={editMode ? "outlined" : "contained"}
          startIcon={editMode ? <Cancel /> : <Edit />}
          onClick={editMode ? handleCancelEdit : () => setEditMode(true)}
        >
          {editMode ? 'Cancel' : 'Edit Profile'}
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Profile Overview */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar
                sx={{ 
                  width: 120, 
                  height: 120, 
                  mx: 'auto', 
                  mb: 2,
                  bgcolor: 'primary.main',
                  fontSize: '3rem'
                }}
              >
                {profile.avatar ? (
                  <img src={profile.avatar} alt={profile.name} />
                ) : (
                  profile.name.charAt(0).toUpperCase()
                )}
              </Avatar>

              {editMode ? (
                <TextField
                  fullWidth
                  value={editedProfile?.name || ''}
                  onChange={(e) => setEditedProfile(prev => prev ? { ...prev, name: e.target.value } : null)}
                  sx={{ mb: 2 }}
                />
              ) : (
                <Typography variant="h5" fontWeight="bold" gutterBottom>
                  {profile.name}
                </Typography>
              )}

              {editMode ? (
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  value={editedProfile?.bio || ''}
                  onChange={(e) => setEditedProfile(prev => prev ? { ...prev, bio: e.target.value } : null)}
                  placeholder="Tell us about yourself..."
                  sx={{ mb: 2 }}
                />
              ) : (
                <Typography variant="body2" color="textSecondary" paragraph>
                  {profile.bio}
                </Typography>
              )}

              <Box display="flex" justifyContent="center" gap={1} mb={2}>
                <Chip 
                  label={`${profile.statistics.problems_solved} Problems Solved`}
                  color="primary"
                  icon={<Code />}
                />
                <Chip 
                  label={`${profile.statistics.current_streak} Day Streak`}
                  color="secondary"
                  icon={<TrendingUp />}
                />
              </Box>

              {editMode && (
                <Button
                  variant="contained"
                  startIcon={<Save />}
                  onClick={handleSaveProfile}
                  fullWidth
                >
                  Save Changes
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Contact Info */}
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Contact Information
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'transparent', color: 'text.primary' }}>
                      <Email />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText 
                    primary="Email"
                    secondary={profile.email}
                  />
                </ListItem>
                <ListItem>
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'transparent', color: 'text.primary' }}>
                      <LocationOn />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText 
                    primary="Location"
                    secondary={profile.location || 'Not specified'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'transparent', color: 'text.primary' }}>
                      <GitHub />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText 
                    primary="GitHub"
                    secondary={profile.githubUsername || 'Not connected'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'transparent', color: 'text.primary' }}>
                      <LinkedIn />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText 
                    primary="LinkedIn"
                    secondary={profile.linkedinProfile || 'Not connected'}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Main Content */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
                <Tab label="Statistics" icon={<Assessment />} />
                <Tab label="Achievements" icon={<EmojiEvents />} />
                <Tab label="Preferences" icon={<Settings />} />
              </Tabs>

              {/* Statistics Tab */}
              {activeTab === 0 && (
                <Box sx={{ pt: 3 }}>
                  <Grid container spacing={3}>
                    {/* Skill Levels */}
                    <Grid item xs={12}>
                      <Typography variant="h6" gutterBottom>
                        Skill Levels
                      </Typography>
                      {Object.entries(profile.statistics.skill_levels).map(([skill, level]) => (
                        <Box key={skill} mb={2}>
                          <Box display="flex" justifyContent="space-between" mb={1}>
                            <Typography variant="body2">{skill}</Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {level}%
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={level}
                            color={getSkillLevelColor(level) as any}
                            sx={{ height: 8, borderRadius: 4 }}
                          />
                        </Box>
                      ))}
                    </Grid>

                    {/* Study Statistics */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" gutterBottom>
                        Study Statistics
                      </Typography>
                      <List>
                        <ListItem>
                          <ListItemText
                            primary="Total Study Time"
                            secondary={`${profile.statistics.total_study_time} hours`}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="Longest Streak"
                            secondary={`${profile.statistics.longest_streak} days`}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="Weekly Goal"
                            secondary={`${profile.preferences.study_hours_per_week} hours/week`}
                          />
                        </ListItem>
                      </List>
                    </Grid>

                    {/* Favorite Topics */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" gutterBottom>
                        Favorite Topics
                      </Typography>
                      <Box display="flex" gap={1} flexWrap="wrap">
                        {profile.statistics.favorite_topics.map((topic, index) => (
                          <Chip
                            key={index}
                            label={topic}
                            color="primary"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              )}

              {/* Achievements Tab */}
              {activeTab === 1 && (
                <Box sx={{ pt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Achievements ({profile.achievements.length})
                  </Typography>
                  <Grid container spacing={2}>
                    {profile.achievements.map((achievement) => (
                      <Grid item xs={12} sm={6} key={achievement.id}>
                        <Card 
                          variant="outlined"
                          sx={{ 
                            border: `2px solid ${getRarityColor(achievement.rarity)}`,
                            '&:hover': { boxShadow: 4 }
                          }}
                        >
                          <CardContent>
                            <Box display="flex" alignItems="center" gap={2}>
                              <Typography variant="h4">
                                {achievement.icon}
                              </Typography>
                              <Box>
                                <Typography variant="subtitle1" fontWeight="bold">
                                  {achievement.title}
                                </Typography>
                                <Typography variant="body2" color="textSecondary">
                                  {achievement.description}
                                </Typography>
                                <Chip
                                  label={achievement.rarity}
                                  size="small"
                                  sx={{ 
                                    mt: 1,
                                    backgroundColor: getRarityColor(achievement.rarity),
                                    color: 'white'
                                  }}
                                />
                              </Box>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}

              {/* Preferences Tab */}
              {activeTab === 2 && (
                <Box sx={{ pt: 3 }}>
                  <Grid container spacing={3}>
                    {/* Learning Preferences */}
                    <Grid item xs={12}>
                      <Accordion>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography variant="h6">Learning Preferences</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Grid container spacing={2}>
                            <Grid item xs={12} md={6}>
                              <FormControl fullWidth>
                                <InputLabel>Preferred Difficulty</InputLabel>
                                <Select
                                  value={profile.preferences.difficulty_preference}
                                  disabled={!editMode}
                                >
                                  <MenuItem value="easy">Easy</MenuItem>
                                  <MenuItem value="medium">Medium</MenuItem>
                                  <MenuItem value="hard">Hard</MenuItem>
                                  <MenuItem value="mixed">Mixed</MenuItem>
                                </Select>
                              </FormControl>
                            </Grid>
                            <Grid item xs={12} md={6}>
                              <FormControl fullWidth>
                                <InputLabel>Learning Style</InputLabel>
                                <Select
                                  value={profile.preferences.learning_style}
                                  disabled={!editMode}
                                >
                                  <MenuItem value="visual">Visual</MenuItem>
                                  <MenuItem value="analytical">Analytical</MenuItem>
                                  <MenuItem value="practical">Practical</MenuItem>
                                </Select>
                              </FormControl>
                            </Grid>
                          </Grid>
                        </AccordionDetails>
                      </Accordion>
                    </Grid>

                    {/* Notification Preferences */}
                    <Grid item xs={12}>
                      <Accordion>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography variant="h6">Notification Preferences</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <List>
                            <ListItem>
                              <ListItemText
                                primary="Email Notifications"
                                secondary="Receive updates via email"
                              />
                              <ListItemSecondaryAction>
                                <Switch
                                  checked={profile.preferences.notification_preferences.email_notifications}
                                  disabled={!editMode}
                                />
                              </ListItemSecondaryAction>
                            </ListItem>
                            <ListItem>
                              <ListItemText
                                primary="Push Notifications"
                                secondary="Browser notifications for real-time updates"
                              />
                              <ListItemSecondaryAction>
                                <Switch
                                  checked={profile.preferences.notification_preferences.push_notifications}
                                  disabled={!editMode}
                                />
                              </ListItemSecondaryAction>
                            </ListItem>
                            <ListItem>
                              <ListItemText
                                primary="Weekly Summary"
                                secondary="Weekly progress reports"
                              />
                              <ListItemSecondaryAction>
                                <Switch
                                  checked={profile.preferences.notification_preferences.weekly_summary}
                                  disabled={!editMode}
                                />
                              </ListItemSecondaryAction>
                            </ListItem>
                          </List>
                        </AccordionDetails>
                      </Accordion>
                    </Grid>

                    {/* Target Companies */}
                    <Grid item xs={12}>
                      <Accordion>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography variant="h6">Target Companies</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Box display="flex" gap={1} flexWrap="wrap">
                            {profile.preferences.target_companies.map((company, index) => (
                              <Chip
                                key={index}
                                label={company}
                                color="primary"
                                variant="outlined"
                              />
                            ))}
                          </Box>
                        </AccordionDetails>
                      </Accordion>
                    </Grid>
                  </Grid>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default UserProfile;
