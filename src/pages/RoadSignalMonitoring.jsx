import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFeedback } from '@/context/FeedbackContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Eye, ArrowLeft, Save, Octagon, Triangle, Circle } from 'lucide-react';
import { format } from 'date-fns';

const RoadSignalMonitoring = () => {
  const navigate = useNavigate();
  const { addFeedback, getModuleEvents, updateModuleEvents } = useFeedback();
  const moduleName = 'Road Signal Monitoring';

  // Load events from context on mount
  const [events, setEvents] = useState(() => getModuleEvents(moduleName));
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [currentSignal, setCurrentSignal] = useState(null);

  const signalTypes = [
    { type: 'Stop Sign', icon: Octagon, color: 'red', action: 'STOP', message: '🛑 Stop sign ahead! Come to complete stop.' },
    { type: 'Yield Sign', icon: Triangle, color: 'yellow', action: 'YIELD', message: '⚠️ Yield sign detected. Slow down and check traffic.' },
    { type: 'Green Light', icon: Circle, color: 'green', action: 'PROCEED', message: '✓ Green light. Proceed with caution.' },
    { type: 'Red Light', icon: Circle, color: 'red', action: 'STOP', message: '🔴 Red light! Stop before intersection.' },
    { type: 'Yellow Light', icon: Circle, color: 'yellow', action: 'CAUTION', message: '🟡 Yellow light. Prepare to stop if safe.' },
    { type: 'Speed Limit 45', icon: Octagon, color: 'white', action: 'LIMIT', message: '📊 Speed limit 45 mph. Adjust speed accordingly.' },
    { type: 'School Zone', icon: Triangle, color: 'yellow', action: 'CAUTION', message: '🏫 School zone ahead! Reduce speed to 25 mph.' },
  ];

  // Update context whenever events change
  useEffect(() => {
    updateModuleEvents(moduleName, events);
  }, [events]);

  useEffect(() => {
    if (!isMonitoring) return;

    const interval = setInterval(() => {
      // Randomly generate signal detection events (40% chance every 4 seconds)
      if (Math.random() > 0.6) {
        const signal = signalTypes[Math.floor(Math.random() * signalTypes.length)];
        const newEvent = {
          id: Date.now(),
          time: new Date(),
          ...signal,
          distance: Math.round(Math.random() * 200 + 50), // 50-250 meters
        };
        setCurrentSignal(signal);
        setEvents((prev) => [newEvent, ...prev].slice(0, 10));

        // Clear current signal after 5 seconds
        setTimeout(() => setCurrentSignal(null), 5000);
      }
    }, 4000);

    return () => clearInterval(interval);
  }, [isMonitoring]);

  const getEventColor = (color) => {
    switch (color) {
      case 'red':
        return 'bg-red-100 border-red-500 text-red-900';
      case 'yellow':
        return 'bg-yellow-100 border-yellow-500 text-yellow-900';
      case 'green':
        return 'bg-green-100 border-green-500 text-green-900';
      default:
        return 'bg-gray-100 border-gray-500 text-gray-900';
    }
  };

  const handleSaveFeedback = () => {
    events.forEach((event) => {
      addFeedback({
        module: 'Road Signal Monitoring',
        eventType: event.type,
        message: event.message,
        action: event.action,
        distance: event.distance,
      });
    });
    alert('All signal events saved to feedback history!');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              className="h-10"
              onClick={() => navigate('/home')}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Road Signal Monitoring
              </h1>
              <p className="text-sm text-gray-600">AI-powered traffic signal detection</p>
            </div>
          </div>
          <Button
            className="h-12 px-6 bg-green-600 hover:bg-green-700 text-white text-base font-semibold shadow-md"
            onClick={handleSaveFeedback}
            disabled={events.length === 0}
          >
            <Save className="mr-2 h-5 w-5" />
            Save All to History
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          <Card className="bg-white col-span-2">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Current Detection</CardTitle>
            </CardHeader>
            <CardContent>
              {currentSignal ? (
                <div className={`p-4 rounded-lg border-l-4 ${getEventColor(currentSignal.color)}`}>
                  <div className="flex items-center gap-3 mb-2">
                    {currentSignal.icon && <currentSignal.icon className="w-8 h-8" />}
                    <div>
                      <div className="text-xl font-bold">{currentSignal.type}</div>
                      <div className="text-sm mt-1">{currentSignal.action}</div>
                    </div>
                  </div>
                  <p className="text-sm mt-2">{currentSignal.message}</p>
                </div>
              ) : (
                <div className="text-center py-6 text-gray-500 text-sm">
                  Scanning for traffic signals...
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="bg-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Statistics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="text-xs text-gray-500">Monitoring Status</div>
                <div className="flex items-center gap-2 mt-1">
                  <div className={`w-3 h-3 rounded-full ${isMonitoring ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
                  <span className="text-lg font-semibold">
                    {isMonitoring ? 'Active' : 'Paused'}
                  </span>
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Signals Detected</div>
                <div className="text-3xl font-bold text-blue-600">{events.length}</div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="bg-white">
          <CardHeader>
            <CardTitle className="text-base">Live Feed - Detected Signals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {events.length === 0 ? (
                <div className="text-center py-8 text-gray-500 text-sm">
                  Monitoring for traffic signals... No signals detected yet.
                </div>
              ) : (
                events.map((event) => {
                  const Icon = event.icon;
                  return (
                    <div
                      key={event.id}
                      className={`p-4 rounded-lg border-l-4 ${getEventColor(event.color)}`}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <div className="flex items-center gap-2">
                          <Icon className="w-4 h-4" />
                          <span className="font-bold text-sm">{event.type}</span>
                        </div>
                        <span className="text-xs">{format(event.time, 'HH:mm:ss')}</span>
                      </div>
                      <p className="text-sm mb-2">{event.message}</p>
                      <div className="flex gap-4 text-xs text-gray-600">
                        <span>Action: {event.action}</span>
                        <span>Distance: {event.distance}m</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RoadSignalMonitoring;
