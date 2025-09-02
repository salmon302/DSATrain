import React, { useState, useEffect, useCallback } from 'react';
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
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  Tab,
  Tabs,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Edit,
  Save,
  Cancel,
  Settings,
  EmojiEvents,
  TrendingUp,
  Code,
  Assessment,
  ExpandMore,
  GitHub,
  LinkedIn,
  Email,
  LocationOn,
} from '@mui/icons-material';

import { 
  trackingAPI, 
  getCurrentUserId,
  cognitiveAPI,
  skillTreeAPI,
  SkillTreePreferences,
} from '../services/api';

interface UserProfileData {
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
  const [profile, setProfile] = useState<UserProfileData | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [editedProfile, setEditedProfile] = useState<UserProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [cognitive, setCognitive] = useState<any | null>(null);
  const [treePrefs, setTreePrefs] = useState<SkillTreePreferences | null>(null);
  const [savingPrefs, setSavingPrefs] = useState(false);
  const [prefsSaved, setPrefsSaved] = useState(false);
  const [prefsError, setPrefsError] = useState<string | null>(null);

  const userId = getCurrentUserId();

  // Load user profile and analytics
  const loadUserData = useCallback(async () => {
    try {
      setLoading(true);

      // Load base analytics
      const analyticsResponse = await trackingAPI.getUserAnalytics(userId, 30);

      // Load cognitive profile (auto-creates default_user on backend)
      try {
        const prof = await cognitiveAPI.getProfile(userId);
        setCognitive(prof);
      } catch {}

      // Load skill tree preferences
      try {
        const prefs = await skillTreeAPI.getPreferences(userId);
        setTreePrefs(prefs);
      } catch {}

      // Create mock profile (until real user service exists)
    const mockProfile: UserProfileData = {
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
          learning_style: (cognitive?.learning_style_preference as string) || 'visual',
          target_companies: ['Google', 'Meta', 'Amazon']
        },
        achievements: generateMockAchievements(),
        statistics: {
      problems_solved: analyticsResponse.user_analytics?.problem_solving_stats?.solved || 0,
          current_streak: 5,
          longest_streak: 12,
          total_study_time: 150,
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
  }, [userId, cognitive?.learning_style_preference]);

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

  // Save both profile (mock) and skill tree preferences
  const handleSaveProfile = async () => {
    if (!editedProfile) return;
    setEditMode(false);
    setProfile(editedProfile);

    // Save Skill Tree Preferences if present
    if (treePrefs) {
      try {
        setSavingPrefs(true);
        setPrefsError(null);
        await skillTreeAPI.updatePreferences(userId, treePrefs);
        setPrefsSaved(true);
        // hide success after a bit
        setTimeout(() => setPrefsSaved(false), 2000);
      } catch (e: any) {
        console.error('Error saving preferences', e);
        setPrefsError('Failed to save preferences');
      } finally {
        setSavingPrefs(false);
      }
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
    void loadUserData();
  }, [loadUserData]);

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
                <Typography variant="body2" color="text.secondary" paragraph>
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
                                <Typography variant="body2" color="text.secondary">
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
                          {/* Cognitive snapshot */}
                          {cognitive && (
                            <Box mt={2}>
                              <Typography variant="subtitle2" gutterBottom>
                                Cognitive Profile (default_user)
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                WMC: {cognitive.working_memory_capacity ?? '—'} | Style: {cognitive.learning_style_preference ?? '—'} | V↔V: {typeof cognitive.visual_vs_verbal === 'number' ? cognitive.visual_vs_verbal.toFixed(2) : '—'} | Speed: {cognitive.processing_speed ?? '—'}
                              </Typography>
                            </Box>
                          )}
                        </AccordionDetails>
                      </Accordion>
                    </Grid>

                    {/* Skill Tree Preferences */}
                    <Grid item xs={12}>
                      <Accordion>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography variant="h6">Skill Tree Preferences</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          {treePrefs ? (
                            <Box display="flex" flexDirection="column" gap={2} width="100%">
                              {/* Preferred View Mode */}
                              <FormControl fullWidth>
                                <InputLabel id="pref-view-mode-label">Preferred View</InputLabel>
                                <Select
                                  labelId="pref-view-mode-label"
                                  label="Preferred View"
                                  value={treePrefs.preferred_view_mode}
                                  onChange={(e) => editMode && setTreePrefs(prev => prev ? { ...prev, preferred_view_mode: e.target.value as any } : prev)}
                                  disabled={!editMode}
                                >
                                  <MenuItem value="columns">Columns</MenuItem>
                                  <MenuItem value="grid">Grid</MenuItem>
                                  <MenuItem value="tree">Tree</MenuItem>
                                </Select>
                              </FormControl>

                              {/* Switches */}
                              <FormControlLabel
                                control={
                                  <Switch
                                    checked={!!treePrefs.show_confidence_overlay}
                                    onChange={(e) => editMode && setTreePrefs(prev => prev ? { ...prev, show_confidence_overlay: e.target.checked } : prev)}
                                    disabled={!editMode}
                                  />
                                }
                                label="Show confidence overlay"
                              />
                              <FormControlLabel
                                control={
                                  <Switch
                                    checked={!!treePrefs.auto_expand_clusters}
                                    onChange={(e) => editMode && setTreePrefs(prev => prev ? { ...prev, auto_expand_clusters: e.target.checked } : prev)}
                                    disabled={!editMode}
                                  />
                                }
                                label="Auto-expand clusters"
                              />
                              <FormControlLabel
                                control={
                                  <Switch
                                    checked={!!treePrefs.highlight_prerequisites}
                                    onChange={(e) => editMode && setTreePrefs(prev => prev ? { ...prev, highlight_prerequisites: e.target.checked } : prev)}
                                    disabled={!editMode}
                                  />
                                }
                                label="Highlight prerequisites"
                              />

                              {/* Visible Skill Areas (simple CSV input to avoid overbuilding UI) */}
                              <TextField
                                label="Visible Skill Areas (CSV)"
                                value={(treePrefs.visible_skill_areas || []).join(', ')}
                                onChange={(e) => editMode && setTreePrefs(prev => prev ? { ...prev, visible_skill_areas: e.target.value.split(',').map(s => s.trim()).filter(Boolean) } : prev)}
                                disabled={!editMode}
                                helperText="Comma-separated list. Leave empty to show all."
                              />

                              {/* Local save button for convenience while in edit mode */}
                              {editMode && (
                                <Box>
                                  <Button
                                    variant="contained"
                                    onClick={handleSaveProfile}
                                    disabled={savingPrefs}
                                  >
                                    {savingPrefs ? 'Saving…' : 'Save Preferences'}
                                  </Button>
                                  {prefsSaved && (
                                    <Typography variant="body2" color="success.main" sx={{ ml: 2, display: 'inline' }}>
                                      Preferences saved
                                    </Typography>
                                  )}
                                  {prefsError && (
                                    <Typography variant="body2" color="error.main" sx={{ ml: 2, display: 'inline' }}>
                                      {prefsError}
                                    </Typography>
                                  )}
                                </Box>
                              )}
                            </Box>
                          ) : (
                            <Typography variant="body2" color="text.secondary">No preferences found for user.</Typography>
                          )}
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
