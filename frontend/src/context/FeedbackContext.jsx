import React, { createContext, useContext, useState, useEffect } from 'react';

const FeedbackContext = createContext();

export const useFeedback = () => {
  const context = useContext(FeedbackContext);
  if (!context) {
    throw new Error('useFeedback must be used within a FeedbackProvider');
  }
  return context;
};

// Dummy feedback data for initial demonstration
const dummyFeedback = [
  {
    id: 1700000001,
    timestamp: new Date(Date.now() - 3600000 * 2).toISOString(), // 2 hours ago
    module: 'Brake Checking',
    eventType: 'hard',
    message: '⚠️ HARD BRAKING DETECTED at 45 mph! Maintain safe following distance.',
    speed: 45,
    force: 85,
    severity: 'high',
  },
  {
    id: 1700000002,
    timestamp: new Date(Date.now() - 3600000 * 4).toISOString(), // 4 hours ago
    module: 'Speed Monitoring',
    eventType: 'Red Light',
    message: '🔴 Red light! Stop before intersection.',
    action: 'STOP',
    distance: 120,
    severity: 'moderate',
  },
  {
    id: 1700000003,
    timestamp: new Date(Date.now() - 3600000 * 6).toISOString(), // 6 hours ago
    module: 'Lane Change Detection',
    eventType: 'Center to Right',
    message: '⚠️ Lane change WITHOUT signal! Moved from Center to Right lane. Use turn signals!',
    signalUsed: false,
    safetyScore: 35,
    severity: 'high',
  },
  {
    id: 1700000004,
    timestamp: new Date(Date.now() - 3600000 * 8).toISOString(), // 8 hours ago
    module: 'Brake Checking',
    eventType: 'moderate',
    message: '⚡ Moderate braking at 55 mph. Monitor traffic ahead.',
    speed: 55,
    force: 60,
    severity: 'moderate',
  },
  {
    id: 1700000005,
    timestamp: new Date(Date.now() - 3600000 * 10).toISOString(), // 10 hours ago
    module: 'Speed Monitoring',
    eventType: 'Stop Sign',
    message: '🛑 Stop sign ahead! Come to complete stop.',
    action: 'STOP',
    distance: 85,
    severity: 'high',
  },
  {
    id: 1700000006,
    timestamp: new Date(Date.now() - 3600000 * 12).toISOString(), // 12 hours ago
    module: 'Lane Change Detection',
    eventType: 'Left to Center',
    message: '✓ Safe lane change from Left to Center lane with signal. Good job!',
    signalUsed: true,
    safetyScore: 92,
    severity: 'low',
  },
  {
    id: 1700000007,
    timestamp: new Date(Date.now() - 3600000 * 14).toISOString(), // 14 hours ago
    module: 'Brake Checking',
    eventType: 'light',
    message: '✓ Gentle braking at 30 mph. Good control.',
    speed: 30,
    force: 25,
    severity: 'low',
  },
  {
    id: 1700000008,
    timestamp: new Date(Date.now() - 3600000 * 16).toISOString(), // 16 hours ago
    module: 'Speed Monitoring',
    eventType: 'School Zone',
    message: '🏫 School zone ahead! Reduce speed to 25 mph.',
    action: 'CAUTION',
    distance: 200,
    severity: 'low',
  },
];

export const FeedbackProvider = ({ children }) => {
  const [feedbackHistory, setFeedbackHistory] = useState(() => {
    // Load from localStorage on initial render
    const saved = localStorage.getItem('driverAssistFeedback');
    if (saved) {
      return JSON.parse(saved);
    }
    // If no saved data, use dummy data
    return dummyFeedback;
  });

  // Module-specific event states (persists across navigation)
  const [moduleStates, setModuleStates] = useState(() => {
    const saved = localStorage.getItem('driverAssistModuleStates');
    if (saved) {
      return JSON.parse(saved);
    }
    return {
      'Brake Checking': [],
      'Speed Monitoring': [],
      'Lane Change Detection': [],
    };
  });

  // SSE connection state
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);

  // Save to localStorage whenever feedbackHistory changes
  useEffect(() => {
    localStorage.setItem('driverAssistFeedback', JSON.stringify(feedbackHistory));
  }, [feedbackHistory]);

  // Save to localStorage whenever moduleStates changes
  useEffect(() => {
    localStorage.setItem('driverAssistModuleStates', JSON.stringify(moduleStates));
  }, [moduleStates]);

  // Establish SSE connection to backend server
  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const eventSourceUrl = `${apiUrl}/events`;

    console.log('Connecting to SSE server:', eventSourceUrl);

    const eventSource = new EventSource(eventSourceUrl);

    eventSource.onopen = () => {
      console.log('SSE connection established');
      setIsConnected(true);
      setConnectionError(null);
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received event:', data);

        // Add to feedback history with timestamp if not present
        const newFeedback = {
          id: data.id || Date.now(),
          timestamp: data.timestamp || new Date().toISOString(),
          ...data,
        };
        setFeedbackHistory((prev) => [newFeedback, ...prev]);

        // Also update module-specific state if needed
        if (data.module) {
          setModuleStates((prev) => {
            const moduleName = data.module;
            const currentModuleEvents = prev[moduleName] || [];

            // Keep last 10 events for each module
            const updatedEvents = [newFeedback, ...currentModuleEvents].slice(0, 10);

            return {
              ...prev,
              [moduleName]: updatedEvents,
            };
          });
        }
      } catch (error) {
        console.error('Error parsing SSE event:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      setIsConnected(false);
      setConnectionError('Connection lost. Retrying...');
      // EventSource automatically attempts to reconnect
    };

    // Cleanup on unmount
    return () => {
      console.log('Closing SSE connection');
      eventSource.close();
      setIsConnected(false);
    };
  }, []); // Empty dependency array - connect once on mount

  const addFeedback = (feedback) => {
    const newFeedback = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      ...feedback,
    };
    setFeedbackHistory((prev) => [newFeedback, ...prev]);
  };

  const clearHistory = () => {
    setFeedbackHistory([]);
    localStorage.removeItem('driverAssistFeedback');
  };

  const deleteFeedback = (id) => {
    setFeedbackHistory((prev) => prev.filter((item) => item.id !== id));
  };

  // Get events for a specific module
  const getModuleEvents = (moduleName) => {
    return moduleStates[moduleName] || [];
  };

  // Update events for a specific module
  const updateModuleEvents = (moduleName, events) => {
    setModuleStates((prev) => ({
      ...prev,
      [moduleName]: events,
    }));
  };

  // Clear events for a specific module
  const clearModuleEvents = (moduleName) => {
    setModuleStates((prev) => ({
      ...prev,
      [moduleName]: [],
    }));
  };

  const value = {
    feedbackHistory,
    addFeedback,
    clearHistory,
    deleteFeedback,
    getModuleEvents,
    updateModuleEvents,
    clearModuleEvents,
    isConnected,
    connectionError,
  };

  return (
    <FeedbackContext.Provider value={value}>
      {children}
    </FeedbackContext.Provider>
  );
};
