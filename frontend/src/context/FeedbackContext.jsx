import React, { createContext, useContext, useState, useEffect } from 'react';

const FeedbackContext = createContext();

export const useFeedback = () => {
  const context = useContext(FeedbackContext);
  if (!context) {
    throw new Error('useFeedback must be used within a FeedbackProvider');
  }
  return context;
};

export const FeedbackProvider = ({ children }) => {
  const [feedbackHistory, setFeedbackHistory] = useState(() => {
    // Load from localStorage on initial render
    const saved = localStorage.getItem('driverAssistFeedback');
    if (saved) {
      const events = JSON.parse(saved);
      // Deduplicate events by id and timestamp to remove old duplicates
      const uniqueEvents = events.reduce((acc, event) => {
        const key = `${event.id}-${event.timestamp}`;
        if (!acc.seen.has(key)) {
          acc.seen.add(key);
          acc.events.push(event);
        }
        return acc;
      }, { seen: new Set(), events: [] }).events;
      return uniqueEvents;
    }
    // Start with empty array - no dummy data
    return [];
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

        // Normalize the event data - use module name as eventType for better display
        const normalizedData = {
          ...data,
          // Use module name as the display title, fallback to eventType or type
          eventType: data.eventType || data.module || data.type || 'Event',
        };

        // Add to feedback history with timestamp if not present
        const newFeedback = {
          id: normalizedData.id || Date.now(),
          timestamp: normalizedData.timestamp || new Date().toISOString(),
          ...normalizedData,
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
