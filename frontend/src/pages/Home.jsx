import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFeedback } from '@/context/FeedbackContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertCircle, Eye, Navigation, History, LogOut } from 'lucide-react';
import { format } from 'date-fns';

const Home = () => {
  const navigate = useNavigate();
  const { feedbackHistory } = useFeedback();
  const [, setRefresh] = useState(0);

  // Auto-refresh every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setRefresh(prev => prev + 1);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const modules = [
    {
      id: 1,
      title: 'Brake Checking',
      description: 'Monitor braking patterns and detect hard braking events',
      icon: AlertCircle,
      color: 'bg-red-500',
      path: '/brake-checking',
    },
    {
      id: 2,
      title: 'Speed Monitoring',
      description: 'Real-time speed monitoring and traffic signal alerts',
      icon: Eye,
      color: 'bg-yellow-500',
      path: '/speed-monitoring',
    },
    {
      id: 3,
      title: 'Lane Change Detection',
      description: 'Track lane changes and detect unsafe maneuvers',
      icon: Navigation,
      color: 'bg-green-500',
      path: '/lane-change-detection',
    },
  ];

  const getModuleIcon = (module) => {
    switch (module) {
      case 'Brake Checking':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'Speed Monitoring':
        return <Eye className="w-4 h-4 text-yellow-600" />;
      case 'Lane Change Detection':
        return <Navigation className="w-4 h-4 text-green-600" />;
      default:
        return <History className="w-4 h-4 text-blue-500" />;
    }
  };

  const getSeverityBadge = (severity) => {
    if (!severity) return null;
    const colors = {
      high: 'bg-red-100 text-red-800 border-red-300',
      moderate: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      low: 'bg-green-100 text-green-800 border-green-300',
    };
    return (
      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${colors[severity]}`}>
        {severity.toUpperCase()}
      </span>
    );
  };

  const getModuleColor = (module) => {
    switch (module) {
      case 'Brake Checking':
        return 'bg-red-50 border-l-red-500';
      case 'Speed Monitoring':
        return 'bg-yellow-50 border-l-yellow-500';
      case 'Lane Change Detection':
        return 'bg-green-50 border-l-green-500';
      default:
        return 'bg-blue-50 border-l-blue-500';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-1">DriveAssist</h1>
            <p className="text-sm text-gray-600">Select a module to begin monitoring</p>
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              className="h-10 px-4"
              onClick={() => navigate('/feedback-history')}
            >
              Feedback History
            </Button>
            <Button
              variant="outline"
              className="h-10 px-4"
              onClick={() => navigate('/login')}
            >
              Logout
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {modules.map((module) => (
            <Card
              key={module.id}
              className="cursor-pointer hover:shadow-lg transition-all duration-200 border hover:border-gray-400"
              onClick={() => navigate(module.path)}
            >
              <CardHeader className="pb-3">
                <CardTitle className="text-lg mb-1">{module.title}</CardTitle>
                <CardDescription className="text-sm">
                  {module.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button size="sm" className="w-full">
                  Open Module
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card className="mt-8 bg-white">
          <CardHeader>
            <CardTitle className="text-xl flex items-center gap-2">
              <History className="w-5 h-5" />
              Live Feedback
            </CardTitle>
            <CardDescription>Real-time warnings and events (auto-refreshing)</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-96 overflow-y-auto space-y-2">
              {feedbackHistory.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <History className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-sm">No feedback events yet. Start monitoring with the modules above.</p>
                </div>
              ) : (
                feedbackHistory.map((event) => (
                  <div
                    key={event.id}
                    className={`p-3 rounded-lg border-l-4 ${getModuleColor(event.module)}`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <div className="flex items-center gap-2">
                        {getModuleIcon(event.module)}
                        <span className="font-semibold text-sm">{event.module}</span>
                        {getSeverityBadge(event.severity)}
                      </div>
                      <span className="text-xs text-gray-500">
                        {format(new Date(event.timestamp), 'MMM dd, HH:mm:ss')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mt-1">{event.message}</p>
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

export default Home;
