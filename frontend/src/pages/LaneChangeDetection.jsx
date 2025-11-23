import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFeedback } from '@/context/FeedbackContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Navigation, ArrowLeft, Save, ArrowRight, MoveLeft } from 'lucide-react';
import { format } from 'date-fns';

const LaneChangeDetection = () => {
  const navigate = useNavigate();
  const { addFeedback, isConnected, connectionError, feedbackHistory } = useFeedback();
  const moduleName = 'Lane Change Detection';

  // Get events from feedback history (filtered to this module)
  const events = feedbackHistory.filter(event => event.module === moduleName).slice(0, 10);

  const [currentLane, setCurrentLane] = useState('Center');

  const lanes = ['Left', 'Center', 'Right'];

  // Update current lane based on latest event
  useEffect(() => {
    if (events.length > 0 && events[0].toLane) {
      setCurrentLane(events[0].toLane);
    }
  }, [events]);

  const getEventColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'bg-red-100 border-red-500 text-red-900';
      case 'medium':
        return 'bg-yellow-100 border-yellow-500 text-yellow-900';
      default:
        return 'bg-green-100 border-green-500 text-green-900';
    }
  };

  const handleSaveFeedback = () => {
    events.forEach((event) => {
      addFeedback({
        module: 'Lane Change Detection',
        eventType: `${event.fromLane} to ${event.toLane}`,
        message: event.message,
        signalUsed: event.signalUsed,
        safetyScore: event.safetyScore,
        severity: event.severity,
      });
    });
    alert('All lane change events saved to feedback history!');
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
                Lane Change Detection
              </h1>
              <p className="text-sm text-gray-600">Track and analyze lane change behavior</p>
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

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
          <Card className="bg-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Current Lane</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">{currentLane}</div>
            </CardContent>
          </Card>

          <Card className="bg-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Connection</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-400'}`}></div>
                <span className="text-lg font-semibold">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              {connectionError && (
                <p className="text-xs text-red-600 mt-1">{connectionError}</p>
              )}
            </CardContent>
          </Card>

          <Card className="bg-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total Changes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">{events.length}</div>
            </CardContent>
          </Card>

          <Card className="bg-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Avg Safety</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {events.length > 0
                  ? Math.round(events.reduce((sum, e) => sum + e.safetyScore, 0) / events.length)
                  : '--'}
                {events.length > 0 && '%'}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="bg-white">
          <CardHeader>
            <CardTitle className="text-base">Live Feed - Lane Changes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {events.length === 0 ? (
                <div className="text-center py-8 text-gray-500 text-sm">
                  {isConnected
                    ? 'Monitoring for lane changes... No changes detected yet.'
                    : 'Waiting for connection to backend server...'}
                </div>
              ) : (
                events.map((event) => (
                  <div
                    key={event.id}
                    className={`p-4 rounded-lg border-l-4 ${getEventColor(event.severity)}`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <div className="flex items-center gap-2">
                        {event.toLane === 'Right' ? (
                          <ArrowRight className="w-4 h-4" />
                        ) : (
                          <MoveLeft className="w-4 h-4" />
                        )}
                        <span className="font-bold text-sm">
                          {event.fromLane} → {event.toLane}
                        </span>
                      </div>
                      <span className="text-xs">
                        {event.timestamp ? format(new Date(event.timestamp), 'HH:mm:ss') : ''}
                      </span>
                    </div>
                    <p className="text-sm mb-2">{event.message}</p>
                    <div className="flex gap-4 text-xs text-gray-600">
                      <span>Signal: {event.signalUsed ? '✓ Yes' : '✗ No'}</span>
                      {event.safetyScore !== undefined && <span>Safety Score: {event.safetyScore}%</span>}
                      <span className="uppercase">Severity: {event.severity}</span>
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

export default LaneChangeDetection;
