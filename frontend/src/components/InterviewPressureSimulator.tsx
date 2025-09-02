import React, { useMemo, useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Paper,
  LinearProgress,
} from '@mui/material';
import {
  Warning,
  Psychology,
  Timer,
  Notifications,
  VolumeUp,
} from '@mui/icons-material';

interface InterviewPressureSimulatorProps {
  pressureLevel: number;
  timeElapsed: number;
  isActive: boolean;
  onPressureChange: (level: number) => void;
}

interface PressureEvent {
  type: 'warning' | 'info' | 'interruption';
  message: string;
  timestamp: number;
}

const InterviewPressureSimulator: React.FC<InterviewPressureSimulatorProps> = ({
  pressureLevel,
  timeElapsed,
  isActive,
  onPressureChange,
}) => {
  const [events, setEvents] = useState<PressureEvent[]>([]);
  const [showInterruption, setShowInterruption] = useState(false);
  const [currentInterruption, setCurrentInterruption] = useState<string>('');
  const [lastEventTime, setLastEventTime] = useState(0);

  // Pressure level configurations
  const pressureConfigs = useMemo(() => ({
    1: {
      name: 'Relaxed',
      color: 'success',
      eventFrequency: 0, // No events
      description: 'Comfortable practice environment'
    },
    2: {
      name: 'Standard',
      color: 'info',
      eventFrequency: 300, // Every 5 minutes
      description: 'Normal interview conditions'
    },
    3: {
      name: 'Focused',
      color: 'warning',
      eventFrequency: 180, // Every 3 minutes
      description: 'Attentive interviewer with questions'
    },
    4: {
      name: 'Intense',
      color: 'error',
      eventFrequency: 120, // Every 2 minutes
      description: 'Challenging interviewer with frequent interruptions'
    },
    5: {
      name: 'Extreme',
      color: 'error',
      eventFrequency: 60, // Every minute
      description: 'High-stress scenario with constant pressure'
    }
  }), []);

  // Possible interview interruptions and questions
  const interviewInterruptions = useMemo(() => [
    "Can you explain your approach before writing more code?",
    "What's the time complexity of your current solution?",
    "Have you considered any edge cases?",
    "Can you walk me through this part of your code?",
    "Is there a more efficient way to solve this?",
    "How would this solution scale with larger inputs?",
    "What if the input was sorted? Would that change your approach?",
    "Can you test your solution with a simple example?",
    "Are you handling the empty input case?",
    "What's the space complexity here?",
    "Can you optimize this further?",
    "Let's discuss an alternative approach.",
    "How confident are you in this solution?",
    "What other data structures could you use here?",
    "Can you trace through your algorithm step by step?"
  ], []);

  const timeWarnings = useMemo(() => [
    "You have 30 minutes remaining.",
    "Halfway through the interview time.",
    "15 minutes left - consider wrapping up soon.",
    "5 minutes remaining - final optimizations?",
    "Time's almost up - can you summarize your solution?"
  ], []);

  // Generate pressure events based on level and time
  useEffect(() => {
    if (!isActive || pressureLevel === 1) return;

    const config = pressureConfigs[pressureLevel as keyof typeof pressureConfigs];
    const shouldTriggerEvent = timeElapsed > lastEventTime + config.eventFrequency;

    if (shouldTriggerEvent) {
      setLastEventTime(timeElapsed);
      
      // Random event type based on pressure level
      const eventTypes: ('warning' | 'info' | 'interruption')[] = ['info'];
      
      if (pressureLevel >= 3) {
        eventTypes.push('interruption');
      }
      
      if (pressureLevel >= 4) {
        eventTypes.push('warning', 'interruption');
      }

      const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
      
      if (eventType === 'interruption') {
        const interruption = interviewInterruptions[
          Math.floor(Math.random() * interviewInterruptions.length)
        ];
        setCurrentInterruption(interruption);
        setShowInterruption(true);
        
        setEvents(prev => [...prev, {
          type: 'interruption',
          message: `Interviewer: "${interruption}"`,
          timestamp: timeElapsed
        }]);
      } else if (eventType === 'warning') {
        const warning = timeWarnings[Math.min(Math.floor(timeElapsed / 540), timeWarnings.length - 1)];
        setEvents(prev => [...prev, {
          type: 'warning',
          message: warning,
          timestamp: timeElapsed
        }]);
      } else {
        const infoMessages = [
          "Interviewer is taking notes",
          "Interviewer seems engaged",
          "Good progress so far",
          "Keep explaining your thought process"
        ];
        const info = infoMessages[Math.floor(Math.random() * infoMessages.length)];
        setEvents(prev => [...prev, {
          type: 'info',
          message: info,
          timestamp: timeElapsed
        }]);
      }
    }
  }, [timeElapsed, isActive, pressureLevel, lastEventTime, pressureConfigs, interviewInterruptions, timeWarnings]);

  const handleInterruptionResponse = () => {
    setShowInterruption(false);
    setEvents(prev => [...prev, {
      type: 'info',
      message: "You acknowledged the interviewer's question",
      timestamp: timeElapsed
    }]);
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const currentConfig = pressureConfigs[pressureLevel as keyof typeof pressureConfigs];

  return (
    <Box>
      {/* Pressure Level Controls */}
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <Psychology sx={{ mr: 1, verticalAlign: 'middle' }} />
            Interview Pressure Simulation
          </Typography>
          
          <Box display="flex" gap={1} mb={2} flexWrap="wrap">
            {Object.entries(pressureConfigs).map(([level, config]) => (
              <Chip
                key={level}
                label={`${level}: ${config.name}`}
                color={pressureLevel === parseInt(level) ? config.color as any : 'default'}
                onClick={() => onPressureChange(parseInt(level))}
                clickable
                variant={pressureLevel === parseInt(level) ? 'filled' : 'outlined'}
              />
            ))}
          </Box>
          
          <Typography variant="body2" color="text.secondary">
            <strong>Current:</strong> {currentConfig.name} - {currentConfig.description}
          </Typography>
          
          {pressureLevel > 1 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Next Event In: {Math.max(0, currentConfig.eventFrequency - (timeElapsed - lastEventTime))}s
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={Math.min(100, ((timeElapsed - lastEventTime) / currentConfig.eventFrequency) * 100)}
                sx={{ height: 6, borderRadius: 3 }}
              />
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Event Timeline */}
      {events.length > 0 && (
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Interview Timeline
            </Typography>
            
            <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
              {events.slice(-10).map((event, index) => (
                <Alert 
                  key={index} 
                  severity={event.type === 'warning' ? 'warning' : event.type === 'interruption' ? 'error' : 'info'}
                  sx={{ mb: 1 }}
                  icon={event.type === 'interruption' ? <VolumeUp /> : event.type === 'warning' ? <Timer /> : <Notifications />}
                >
                  <Typography variant="body2">
                    <strong>[{formatTime(event.timestamp)}]</strong> {event.message}
                  </Typography>
                </Alert>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Interviewer Interruption Dialog */}
      <Dialog 
        open={showInterruption} 
        onClose={handleInterruptionResponse}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ backgroundColor: 'warning.light' }}>
          <Warning sx={{ mr: 1, verticalAlign: 'middle' }} />
          Interviewer Interruption
        </DialogTitle>
        <DialogContent>
          <Box sx={{ py: 2 }}>
            <Typography variant="h6" gutterBottom>
              "Excuse me..."
            </Typography>
            <Paper sx={{ p: 2, backgroundColor: 'grey.100' }}>
              <Typography variant="body1" sx={{ fontStyle: 'italic' }}>
                "{currentInterruption}"
              </Typography>
            </Paper>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              This is a typical interviewer interruption. Take a moment to address their question, then continue coding.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleInterruptionResponse} variant="contained" color="primary">
            Acknowledge & Continue
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InterviewPressureSimulator;
