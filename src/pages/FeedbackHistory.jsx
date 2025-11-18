import { useNavigate } from 'react-router-dom';
import { useFeedback } from '@/context/FeedbackContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { History, ArrowLeft, Trash2, AlertCircle, Eye, Navigation } from 'lucide-react';
import { format } from 'date-fns';

const FeedbackHistory = () => {
  const navigate = useNavigate();
  const { feedbackHistory, clearHistory, deleteFeedback } = useFeedback();

  const getModuleIcon = (module) => {
    switch (module) {
      case 'Brake Checking':
        return <AlertCircle className="w-6 h-6 text-red-500" />;
      case 'Road Signal Monitoring':
        return <Eye className="w-6 h-6 text-yellow-600" />;
      case 'Lane Change Detection':
        return <Navigation className="w-6 h-6 text-green-600" />;
      default:
        return <History className="w-6 h-6 text-blue-500" />;
    }
  };

  const getModuleColor = (module) => {
    switch (module) {
      case 'Brake Checking':
        return 'bg-red-100 border-red-500 text-red-900';
      case 'Road Signal Monitoring':
        return 'bg-yellow-100 border-yellow-500 text-yellow-900';
      case 'Lane Change Detection':
        return 'bg-green-100 border-green-500 text-green-900';
      default:
        return 'bg-blue-100 border-blue-500 text-blue-900';
    }
  };

  const handleClearAll = () => {
    if (window.confirm('Are you sure you want to clear all feedback history? This cannot be undone.')) {
      clearHistory();
    }
  };

  const handleDelete = (id) => {
    if (window.confirm('Delete this feedback entry?')) {
      deleteFeedback(id);
    }
  };

  const groupedByModule = feedbackHistory.reduce((acc, item) => {
    if (!acc[item.module]) {
      acc[item.module] = [];
    }
    acc[item.module].push(item);
    return acc;
  }, {});

  const stats = {
    total: feedbackHistory.length,
    braking: feedbackHistory.filter(f => f.module === 'Brake Checking').length,
    signals: feedbackHistory.filter(f => f.module === 'Road Signal Monitoring').length,
    lanes: feedbackHistory.filter(f => f.module === 'Lane Change Detection').length,
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
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
                Feedback History
              </h1>
              <p className="text-sm text-gray-600">Review all driving events and warnings</p>
            </div>
          </div>
          {feedbackHistory.length > 0 && (
            <Button
              variant="destructive"
              className="h-10 px-4"
              onClick={handleClearAll}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Clear All
            </Button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="bg-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total Events</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
            </CardContent>
          </Card>

          <Card className="bg-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Brake Events</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">{stats.braking}</div>
            </CardContent>
          </Card>

          <Card className="bg-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Signal Events</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-600">{stats.signals}</div>
            </CardContent>
          </Card>

          <Card className="bg-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Lane Changes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">{stats.lanes}</div>
            </CardContent>
          </Card>
        </div>

        {feedbackHistory.length === 0 ? (
          <Card className="bg-white">
            <CardContent className="py-24">
              <div className="text-center">
                <History className="w-24 h-24 text-gray-300 mx-auto mb-6" />
                <h2 className="text-3xl font-bold text-gray-900 mb-4">No Feedback History Yet</h2>
                <p className="text-xl text-gray-600 mb-8">
                  Start monitoring with the modules to generate feedback events
                </p>
                <Button
                  size="lg"
                  className="h-14 px-8 text-lg"
                  onClick={() => navigate('/home')}
                >
                  Go to Modules
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {Object.entries(groupedByModule).map(([module, items]) => (
              <Card key={module} className="bg-white">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-3">
                    {getModuleIcon(module)}
                    {module} ({items.length} events)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {items.map((item) => (
                      <div
                        key={item.id}
                        className={`p-5 rounded-lg border-l-4 ${getModuleColor(module)} flex justify-between items-start`}
                      >
                        <div className="flex-1">
                          <div className="flex justify-between items-start mb-2">
                            <span className="font-bold text-lg">{item.eventType}</span>
                            <span className="text-sm">
                              {format(new Date(item.timestamp), 'MMM dd, yyyy HH:mm:ss')}
                            </span>
                          </div>
                          <p className="text-base mb-2">{item.message}</p>
                          <div className="flex gap-4 text-sm flex-wrap">
                            {item.speed && <span>Speed: {item.speed} mph</span>}
                            {item.force && <span>Force: {item.force}%</span>}
                            {item.action && <span>Action: {item.action}</span>}
                            {item.distance && <span>Distance: {item.distance}m</span>}
                            {item.signalUsed !== undefined && (
                              <span>Signal: {item.signalUsed ? '✓ Yes' : '✗ No'}</span>
                            )}
                            {item.safetyScore && <span>Safety: {item.safetyScore}%</span>}
                            {item.severity && (
                              <span className="uppercase">Severity: {item.severity}</span>
                            )}
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="ml-4"
                          onClick={() => handleDelete(item.id)}
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default FeedbackHistory;
