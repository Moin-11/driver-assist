import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertCircle, Eye, Navigation, History, LogOut } from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();

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
      title: 'Road Signal Monitoring',
      description: 'Real-time detection and alerts for traffic signals',
      icon: Eye,
      color: 'bg-yellow-500',
      path: '/road-signal-monitoring',
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

        <div className="mt-8 text-center">
          <p className="text-gray-500 text-sm">
            All modules are ready for live monitoring
          </p>
        </div>
      </div>
    </div>
  );
};

export default Home;
