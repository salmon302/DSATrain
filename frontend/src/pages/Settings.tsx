import React, { useState, useEffect, useCallback } from 'react';
import { Box, Typography, Card, CardContent, Grid, FormControl, InputLabel, Select, MenuItem, TextField, Button, Switch, FormControlLabel, Alert, CircularProgress, Chip, Accordion, AccordionSummary, AccordionDetails, Tooltip } from '@mui/material';
import {
  Save,
  Refresh,
  ExpandMore,
  Key,
  Check,
  Error as ErrorIcon,
  Warning,
} from '@mui/icons-material';

import { settingsAPI } from '../services/api';

interface SettingsData {
  enable_ai: boolean;
  ai_provider: string;
  model: string;
  api_keys: { [key: string]: string };
  rate_limit_per_minute: number;
  rate_limit_window_seconds: number;
  monthly_cost_cap_usd: number;
  hint_budget_per_session: number;
  review_budget_per_session: number;
  elaborate_budget_per_session: number;
  cognitive_profile: {
    working_memory_capacity: number;
    learning_style_preference: string;
    visual_vs_verbal: number;
    processing_speed: string;
  };
}

interface EffectiveSettings {
  api_keys_present: { [key: string]: boolean };
  provider_requires_key: boolean;
  provider_has_key: boolean;
  ai_provider_ready: boolean;
  effective_model: string;
}

interface ValidationResult {
  valid: boolean;
  errors: string[];
  provider_has_key: boolean;
  ai_provider_ready: boolean;
}

interface ProviderInfo {
  allowed: string[];
  notes: { [key: string]: string };
}

interface ModelsData {
  models: { [provider: string]: string[] };
}

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [effective, setEffective] = useState<EffectiveSettings | null>(null);
  const [providers, setProviders] = useState<ProviderInfo | null>(null);
  const [models, setModels] = useState<ModelsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  // Local-only inputs for API keys to avoid re-posting masked values from GET /settings
  const [apiKeyInputs, setApiKeyInputs] = useState<{ [key: string]: string }>({});
  // UI toggle for restricting to free models (primarily for OpenRouter)
  const [onlyFreeModels, setOnlyFreeModels] = useState<boolean>(false);

  // Load settings data
  const loadSettings = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Load all data in parallel
      const [settingsResponse, providersResponse, modelsResponse] = await Promise.all([
        settingsAPI.getSettings(true, true),
        settingsAPI.getProviders(),
        settingsAPI.getModels(),
      ]);

      setSettings(settingsResponse);
      setEffective({
        api_keys_present: settingsResponse.api_keys_present || {},
        provider_requires_key: settingsResponse.provider_requires_key || false,
        provider_has_key: settingsResponse.provider_has_key || false,
        ai_provider_ready: settingsResponse.ai_provider_ready || false,
        effective_model: settingsResponse.effective_model || '',
      });
      setProviders(settingsResponse.providers || providersResponse);
      setModels(modelsResponse);

    } catch (error: any) {
      console.error('Error loading settings:', error);
      setError(error.response?.data?.detail || 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  }, []);

  // Validate settings without saving
  const validateSettings = async (settingsToValidate: Partial<SettingsData>) => {
    try {
      setValidating(true);
      setValidationResult(null);

      const response = await settingsAPI.validateSettings(settingsToValidate);
      setValidationResult(response);
      // Live-update readiness flags and effective model without reload
      setEffective((prev) => ({
        api_keys_present: response.api_keys_present || prev?.api_keys_present || {},
        provider_requires_key: response.provider_requires_key ?? prev?.provider_requires_key ?? false,
        provider_has_key: response.provider_has_key ?? prev?.provider_has_key ?? false,
        ai_provider_ready: response.ai_provider_ready ?? prev?.ai_provider_ready ?? false,
        effective_model: (settingsToValidate.model as string) || prev?.effective_model || '',
      }));
      return response;

    } catch (error: any) {
      if (error.response?.status === 400) {
        setValidationResult({
          valid: false,
          errors: error.response.data.detail?.errors || [error.response.data.detail?.message || 'Validation failed'],
          provider_has_key: error.response.data.detail?.provider_has_key || false,
          ai_provider_ready: error.response.data.detail?.ai_provider_ready || false,
        });
        return error.response.data.detail;
      }
      throw error;
    } finally {
      setValidating(false);
    }
  };

  // Save settings
  const saveSettings = async () => {
    if (!settings) return;

    try {
      setSaving(true);
      setError(null);
      setSuccessMessage(null);

      // Build payload without masked api_keys unless user provided new values
      const payload: any = {
        enable_ai: settings.enable_ai,
        ai_provider: settings.ai_provider,
        model: settings.model,
        rate_limit_per_minute: settings.rate_limit_per_minute,
        rate_limit_window_seconds: settings.rate_limit_window_seconds,
        monthly_cost_cap_usd: settings.monthly_cost_cap_usd,
        hint_budget_per_session: settings.hint_budget_per_session,
        review_budget_per_session: settings.review_budget_per_session,
        elaborate_budget_per_session: settings.elaborate_budget_per_session,
        cognitive_profile: settings.cognitive_profile,
      };
      const keysToSend: { [key: string]: string | null } = {};
      Object.entries(apiKeyInputs || {}).forEach(([prov, val]) => {
        // Send only keys the user typed (non-empty). To clear a key, we could support null explicitly later.
        if (typeof val === 'string' && val.length > 0) {
          keysToSend[prov] = val;
        }
      });
      if (Object.keys(keysToSend).length > 0) {
        payload.api_keys = keysToSend;
      }

      // First validate
      const validation = await validateSettings(payload);
      if (!validation.valid) {
        setError('Please fix the validation errors before saving');
        return;
      }

  // Save if valid
  await settingsAPI.updateSettings(payload);
      setSuccessMessage('Settings saved successfully!');
      
      // Reload to get updated effective settings
      await loadSettings();

    } catch (error: any) {
      console.error('Error saving settings:', error);
      setError(error.response?.data?.detail || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  // Handle provider change
  const handleProviderChange = async (provider: string) => {
    if (!settings) return;

    const newSettings = { ...settings, ai_provider: provider };
    
    // Reset model when provider changes
    const allProviderModels = models?.models?.[provider] ?? [];
    const filtered = onlyFreeModels
      ? allProviderModels.filter((m) => isFreeModel(m, provider))
      : allProviderModels;
    newSettings.model = filtered.length > 0 ? filtered[0] : '';

    setSettings(newSettings);

    // Validate the new provider selection and live-update models/effective
    await validateSettings({ ai_provider: provider, model: newSettings.model });
  };

  // Handle model change
  const handleModelChange = async (model: string) => {
    if (!settings) return;

    const newSettings = { ...settings, model };
    setSettings(newSettings);

    // Validate the new model selection and live-update effective model
    await validateSettings({ ai_provider: settings.ai_provider, model });
  };

  // Handle API key change
  const handleApiKeyChange = (provider: string, value: string) => {
    if (!settings) return;
    setApiKeyInputs((prev) => ({
      ...prev,
      [provider]: value,
    }));
  };

  // Helper: determine if a model is free (heuristics; primarily for OpenRouter)
  const isFreeModel = (modelId: string, provider?: string) => {
    const prov = provider || settings?.ai_provider || '';
    if (prov === 'openrouter') {
      return modelId.includes(':free');
    }
    return false;
  };

  // Get provider readiness status
  const getProviderStatus = () => {
    if (!effective) return { icon: <Warning />, color: 'warning', text: 'Unknown' };
    
    if (effective.ai_provider_ready) {
      return { icon: <Check />, color: 'success', text: 'Ready' };
    }
    
    if (effective.provider_requires_key && !effective.provider_has_key) {
      return { icon: <Key />, color: 'error', text: 'API Key Required' };
    }
    
    return { icon: <ErrorIcon />, color: 'error', text: 'Not Ready' };
  };

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!settings) {
    return (
      <Alert severity="error">
        Failed to load settings. Please try refreshing the page.
      </Alert>
    );
  }

  const providerStatus = getProviderStatus();

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          ⚙️ Settings
        </Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadSettings}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={saveSettings}
            disabled={saving || validating}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </Box>
      </Box>

      {/* Status Messages */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {successMessage && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      )}

      {/* Validation Results */}
      {validationResult && !validationResult.valid && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Validation Issues:</Typography>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {validationResult.errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* AI Provider Configuration */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                AI Provider Configuration
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.enable_ai}
                        onChange={(e) => setSettings({ ...settings, enable_ai: e.target.checked })}
                      />
                    }
                    label="Enable AI Features"
                  />
                </Grid>

                {settings.enable_ai && (
                  <>
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth>
                        <InputLabel>AI Provider</InputLabel>
                        <Select
                          value={settings.ai_provider}
                          onChange={(e) => handleProviderChange(e.target.value)}
                          disabled={validating}
                        >
                          {providers?.allowed.map((provider) => (
                            <MenuItem key={provider} value={provider}>
                              {provider}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                      {providers?.notes[settings.ai_provider] && (
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                          {providers.notes[settings.ai_provider]}
                        </Typography>
                      )}
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth>
                        <InputLabel>Model</InputLabel>
                        <Select
                          value={settings.model}
                          onChange={(e) => handleModelChange(e.target.value)}
                          disabled={validating || !models?.models[settings.ai_provider]?.length}
                        >
                          {(onlyFreeModels
                            ? (models?.models[settings.ai_provider] || []).filter((m) => isFreeModel(m, settings.ai_provider))
                            : (models?.models[settings.ai_provider] || [])
                           ).map((model) => (
                            <MenuItem key={model} value={model}>
                              {model}
                            </MenuItem>
                          )) || []}
                        </Select>
                      </FormControl>
                      {/* Toggle: Only Free Models (shown for OpenRouter) */}
                      {settings.ai_provider === 'openrouter' && (
                        <FormControlLabel
                          control={
                            <Switch
                              checked={onlyFreeModels}
                              onChange={(e) => {
                                setOnlyFreeModels(e.target.checked);
                                // If current model is not free when toggled on, switch to first free model
                                const provider = settings.ai_provider;
                                const allModels = models?.models?.[provider] || [];
                                const filtered = e.target.checked
                                  ? allModels.filter((m) => isFreeModel(m, provider))
                                  : allModels;
                                if (filtered.length > 0 && !filtered.includes(settings.model)) {
                                  handleModelChange(filtered[0]);
                                }
                              }}
                            />
                          }
                          label="Only show free models"
                          sx={{ mt: 1 }}
                        />
                      )}
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        Effective Model: {effective?.effective_model || 'None'}
                      </Typography>
                    </Grid>

                    {/* API Keys Section */}
                    {settings.ai_provider !== 'none' && settings.ai_provider !== 'local' && (
                      <Grid item xs={12}>
                        <Accordion>
                          <AccordionSummary expandIcon={<ExpandMore />}>
                            <Typography variant="subtitle1">
                              API Keys
                            </Typography>
                            <Chip
                              icon={providerStatus.icon}
                              label={providerStatus.text}
                              color={providerStatus.color as any}
                              size="small"
                              sx={{ ml: 2 }}
                            />
                          </AccordionSummary>
                          <AccordionDetails>
                            <Grid container spacing={2}>
                              {providers?.allowed.filter(p => p !== 'none' && p !== 'local').map((provider) => (
                                <Grid item xs={12} key={provider}>
                                  <TextField
                                    fullWidth
                                    label={`${provider} API Key`}
                                    type="password"
                                    value={apiKeyInputs?.[provider] ?? ''}
                                    onChange={(e) => handleApiKeyChange(provider, e.target.value)}
                                    placeholder="Enter API key"
                                    InputProps={{
                                      endAdornment: effective?.api_keys_present[provider] ? (
                                        <Tooltip title="API Key Present">
                                          <Check color="success" />
                                        </Tooltip>
                                      ) : (
                                        <Tooltip title="No API Key">
                                          <Key color="disabled" />
                                        </Tooltip>
                                      ),
                                    }}
                                    helperText={
                                      effective?.api_keys_present[provider]
                                        ? 'API key is configured'
                                        : 'Enter your API key or set via environment variable'
                                    }
                                  />
                                </Grid>
                              ))}
                            </Grid>
                          </AccordionDetails>
                        </Accordion>
                      </Grid>
                    )}
                  </>
                )}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Current Status */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Status
              </Typography>
              
              <Box display="flex" flexDirection="column" gap={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">AI Enabled:</Typography>
                  <Chip
                    label={settings.enable_ai ? 'Yes' : 'No'}
                    color={settings.enable_ai ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
                
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">Provider:</Typography>
                  <Chip label={settings.ai_provider} size="small" />
                </Box>
                
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">Model:</Typography>
                  <Chip label={effective?.effective_model || 'None'} size="small" />
                </Box>
                
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">Provider Status:</Typography>
                  <Chip
                    icon={providerStatus.icon}
                    label={providerStatus.text}
                    color={providerStatus.color as any}
                    size="small"
                  />
                </Box>

                {validating && (
                  <Box display="flex" justifyContent="center" mt={2}>
                    <CircularProgress size={20} />
                    <Typography variant="caption" sx={{ ml: 1 }}>
                      Validating...
                    </Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Rate Limiting Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Rate Limiting & Budget
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Rate Limit (per minute)"
                    type="number"
                    value={settings.rate_limit_per_minute}
                    onChange={(e) => setSettings({ ...settings, rate_limit_per_minute: parseInt(e.target.value) || 0 })}
                    inputProps={{ min: 1, max: 120 }}
                    helperText="Max API calls per minute"
                  />
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Rate Window (seconds)"
                    type="number"
                    value={settings.rate_limit_window_seconds}
                    onChange={(e) => setSettings({ ...settings, rate_limit_window_seconds: parseInt(e.target.value) || 0 })}
                    inputProps={{ min: 10, max: 3600 }}
                    helperText="Time window for rate limiting"
                  />
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Monthly Budget (USD)"
                    type="number"
                    value={settings.monthly_cost_cap_usd}
                    onChange={(e) => setSettings({ ...settings, monthly_cost_cap_usd: parseFloat(e.target.value) || 0 })}
                    inputProps={{ min: 0, max: 1000, step: 0.01 }}
                    helperText="Monthly spending limit"
                  />
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Hints per Session"
                    type="number"
                    value={settings.hint_budget_per_session}
                    onChange={(e) => setSettings({ ...settings, hint_budget_per_session: parseInt(e.target.value) || 0 })}
                    inputProps={{ min: 0, max: 100 }}
                    helperText="Max hints per session"
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Reviews per Session"
                    type="number"
                    value={settings.review_budget_per_session}
                    onChange={(e) => setSettings({ ...settings, review_budget_per_session: parseInt(e.target.value) || 0 })}
                    inputProps={{ min: 0, max: 100 }}
                    helperText="Max reviews per session"
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Elaborations per Session"
                    type="number"
                    value={settings.elaborate_budget_per_session}
                    onChange={(e) => setSettings({ ...settings, elaborate_budget_per_session: parseInt(e.target.value) || 0 })}
                    inputProps={{ min: 0, max: 100 }}
                    helperText="Max elaborations per session"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Cognitive Profile */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="h6">Cognitive Profile Settings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Working Memory (1-10)"
                    type="number"
                    value={settings.cognitive_profile?.working_memory_capacity || 5}
                    onChange={(e) => setSettings({
                      ...settings,
                      cognitive_profile: {
                        ...settings.cognitive_profile,
                        working_memory_capacity: parseInt(e.target.value) || 5,
                      },
                    })}
                    inputProps={{ min: 1, max: 10 }}
                  />
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Learning Style</InputLabel>
                    <Select
                      value={settings.cognitive_profile?.learning_style_preference || 'balanced'}
                      onChange={(e) => setSettings({
                        ...settings,
                        cognitive_profile: {
                          ...settings.cognitive_profile,
                          learning_style_preference: e.target.value,
                        },
                      })}
                    >
                      <MenuItem value="visual">Visual</MenuItem>
                      <MenuItem value="verbal">Verbal</MenuItem>
                      <MenuItem value="balanced">Balanced</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Visual vs Verbal (0-1)"
                    type="number"
                    value={settings.cognitive_profile?.visual_vs_verbal || 0.5}
                    onChange={(e) => setSettings({
                      ...settings,
                      cognitive_profile: {
                        ...settings.cognitive_profile,
                        visual_vs_verbal: parseFloat(e.target.value) || 0.5,
                      },
                    })}
                    inputProps={{ min: 0, max: 1, step: 0.1 }}
                  />
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Processing Speed</InputLabel>
                    <Select
                      value={settings.cognitive_profile?.processing_speed || 'average'}
                      onChange={(e) => setSettings({
                        ...settings,
                        cognitive_profile: {
                          ...settings.cognitive_profile,
                          processing_speed: e.target.value,
                        },
                      })}
                    >
                      <MenuItem value="slow">Slow</MenuItem>
                      <MenuItem value="average">Average</MenuItem>
                      <MenuItem value="fast">Fast</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Settings;
