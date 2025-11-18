import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFeedback } from '@/context/FeedbackContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle, ArrowLeft, Save } from 'lucide-react';
import { format } from 'date-fns';

const BrakeChecking = () => {
  const navigate = useNavigate();
  const { addFeedback, getModuleEvents, updateModuleEvents } = useFeedback();
  const moduleName = 'Brake Checking';

  // Load events from context on mount
  const [events, setEvents] = useState(() => getModuleEvents(moduleName));
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [speed, setSpeed] = useState(45);

  // Update context whenever events change
  useEffect(() => {
    updateModuleEvents(moduleName, events);
  }, [events]);

  useEffect(() => {
    if (!isMonitoring) return;

    const interval = setInterval(() => {
      // Simulate speed changes
      const newSpeed = Math.max(0, Math.min(80, speed + (Math.random() * 10 - 5)));
      setSpeed(Math.round(newSpeed));

      // Randomly generate brake events (20% chance every 3 seconds)
      if (Math.random() > 0.8) {
        const brakeForce = Math.random();
        const eventType = brakeForce > 0.7 ? 'hard' : brakeForce > 0.4 ? 'moderate' : 'light';
        const newEvent = {
          id: Date.now(),
          time: new Date(),
          type: eventType,
          speed: Math.round(newSpeed),
          force: Math.round(brakeForce * 100),
          message: getBrakeMessage(eventType, newSpeed),
        };
        setEvents((prev) => [newEvent, ...prev].slice(0, 10));
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [isMonitoring, speed]);

  const getBrakeMessage = (type, currentSpeed) => {
    if (type === 'hard') {
      return `⚠️ HARD BRAKING DETECTED at ${currentSpeed} mph! Maintain safe following distance.`;
    } else if (type === 'moderate') {
      return `⚡ Moderate braking at ${currentSpeed} mph. Monitor traffic ahead.`;
    } else {
      return `✓ Gentle braking at ${currentSpeed} mph. Good control.`;
    }
  };

  const getEventColor = (type) => {
    switch (type) {
      case 'hard':
        return 'bg-red-100 border-red-500 text-red-900';
      case 'moderate':
        return 'bg-yellow-100 border-yellow-500 text-yellow-900';
      default:
        return 'bg-green-100 border-green-500 text-green-900';
    }
  };

  const handleSaveFeedback = () => {
    events.forEach((event) => {
      addFeedback({
        module: 'Brake Checking',
        eventType: event.type,
        message: event.message,
        speed: event.speed,
        force: event.force,
      });
    });
    alert('All brake events saved to feedback history!');
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
                Brake Checking Module
              </h1>
              <p className="text-sm text-gray-600">Real-time brake pattern monitoring</p>
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
          <Card className="bg-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Current Speed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">{speed} mph</div>
            </CardContent>
          </Card>

          <Card className="bg-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Monitoring Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${isMonitoring ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
                <span className="text-lg font-semibold">
                  {isMonitoring ? 'Active' : 'Paused'}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Events Detected</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">{events.length}</div>
            </CardContent>
          </Card>
        </div>

        <Card className="bg-white">
          <CardHeader>
            <CardTitle className="text-base">Live Feed - Brake Events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {events.length === 0 ? (
                <div className="text-center py-8 text-gray-500 text-sm">
                  Monitoring for brake events... No events detected yet.
                </div>
              ) : (
                events.map((event) => (
                  <div
                    key={event.id}
                    className={`p-4 rounded-lg border-l-4 ${getEventColor(event.type)}`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-bold text-sm uppercase">{event.type} BRAKE</span>
                      <span className="text-xs">{format(event.time, 'HH:mm:ss')}</span>
                    </div>
                    <p className="text-sm mb-2">{event.message}</p>
                    <div className="flex gap-4 text-xs text-gray-600">
                      <span>Force: {event.force}%</span>
                      <span>Speed: {event.speed} mph</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default BrakeChecking;
