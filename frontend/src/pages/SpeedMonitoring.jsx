import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFeedback } from '@/context/FeedbackContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Eye, ArrowLeft, Save } from 'lucide-react';
import { format } from 'date-fns';

const SpeedMonitoring = () => {
  const navigate = useNavigate();
  const { addFeedback, isConnected, connectionError, feedbackHistory } = useFeedback();
  const moduleName = 'Speed Monitoring';

  // Get events from feedback history (filtered to this module)
  const events = feedbackHistory.filter(event => event.module === moduleName).slice(0, 10);

  // Extract current speed from most recent GPS event
  const [currentSpeed, setCurrentSpeed] = useState(0);
  const [gpsStatus, setGpsStatus] = useState('Waiting for GPS...');

  useEffect(() => {
    const latestSpeedEvent = feedbackHistory.find(event =>
      event.module === moduleName && event.type === 'speed_update'
    );

    if (latestSpeedEvent) {
      setCurrentSpeed(latestSpeedEvent.speed_mph || 0);
      setGpsStatus(latestSpeedEvent.gps_fix ? 'GPS Fix Acquired' : 'No GPS Fix');
    }
  }, [feedbackHistory]);

  const getSpeedColor = (speed) => {
    if (speed > 70) return 'text-red-600';
    if (speed > 50) return 'text-yellow-600';
    return 'text-green-600';
  };

  const handleSaveFeedback = () => {
    events.forEach((event) => {
      addFeedback(event);
    });
    alert('All speed events saved to feedback history!');
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
                GPS Speed Monitoring
              </h1>
              <p className="text-sm text-gray-600">Real-time GPS speed tracking</p>
              <p className="text-xs text-gray-500 mt-1">Note: Traffic sign detection coming soon (requires YOLO integration)</p>
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
              <div className={`text-4xl font-bold ${getSpeedColor(currentSpeed)}`}>
                {Math.round(currentSpeed)} mph
              </div>
              <div className="text-sm text-gray-600 mt-1">{gpsStatus}</div>
            </CardContent>
          </Card>

          <Card className="bg-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Connection Status</CardTitle>
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
              <CardTitle className="text-sm font-medium text-gray-600">Speed Updates</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">{events.length}</div>
              <div className="text-xs text-gray-500 mt-1">Recent updates received</div>
            </CardContent>
          </Card>
        </div>

        <Card className="bg-white">
          <CardHeader>
            <CardTitle className="text-base">Live Feed - GPS Speed Updates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {events.length === 0 ? (
                <div className="text-center py-8 text-gray-500 text-sm">
                  {isConnected
                    ? 'Waiting for GPS speed updates...'
                    : 'Waiting for connection to backend server...'}
                </div>
              ) : (
                events.map((event) => {
                  return (
                    <div
                      key={event.id}
                      className="p-4 rounded-lg border-l-4 bg-blue-50 border-blue-500 text-blue-900"
                    >
                      <div className="flex justify-between items-start mb-1">
                        <div className="flex items-center gap-2">
                          <Eye className="w-4 h-4" />
                          <span className="font-bold text-sm">
                            {event.type === 'speed_update' ? 'Speed Update' : 'GPS Status'}
                          </span>
                        </div>
                        <span className="text-xs">
                          {event.timestamp ? format(new Date(event.timestamp), 'HH:mm:ss') : ''}
                        </span>
                      </div>
                      <p className="text-sm mb-2">{event.message}</p>
                      <div className="flex gap-4 text-xs text-gray-600">
                        {event.speed_mph !== undefined && (
                          <>
                            <span>Speed: {Math.round(event.speed_mph)} mph</span>
                            <span>Speed: {Math.round(event.speed_kph)} km/h</span>
                          </>
                        )}
                        <span>GPS: {event.gps_fix ? '✓ Fix' : '✗ No Fix'}</span>
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

export default SpeedMonitoring;
