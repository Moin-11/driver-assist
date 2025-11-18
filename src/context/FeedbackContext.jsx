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
  },
  {
    id: 1700000002,
    timestamp: new Date(Date.now() - 3600000 * 4).toISOString(), // 4 hours ago
    module: 'Road Signal Monitoring',
    eventType: 'Red Light',
    message: '🔴 Red light! Stop before intersection.',
    action: 'STOP',
    distance: 120,
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
  },
  {
    id: 1700000005,
    timestamp: new Date(Date.now() - 3600000 * 10).toISOString(), // 10 hours ago
    module: 'Road Signal Monitoring',
    eventType: 'Stop Sign',
    message: '🛑 Stop sign ahead! Come to complete stop.',
    action: 'STOP',
    distance: 85,
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
  },
  {
    id: 1700000008,
    timestamp: new Date(Date.now() - 3600000 * 16).toISOString(), // 16 hours ago
    module: 'Road Signal Monitoring',
    eventType: 'School Zone',
    message: '🏫 School zone ahead! Reduce speed to 25 mph.',
    action: 'CAUTION',
    distance: 200,
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
      'Road Signal Monitoring': [],
      'Lane Change Detection': [],
    };
  });

  // Save to localStorage whenever feedbackHistory changes
  useEffect(() => {
    localStorage.setItem('driverAssistFeedback', JSON.stringify(feedbackHistory));
  }, [feedbackHistory]);

  // Save to localStorage whenever moduleStates changes
  useEffect(() => {
    localStorage.setItem('driverAssistModuleStates', JSON.stringify(moduleStates));
  }, [moduleStates]);

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
  };

  return (
    <FeedbackContext.Provider value={value}>
      {children}
    </FeedbackContext.Provider>
  );
};
