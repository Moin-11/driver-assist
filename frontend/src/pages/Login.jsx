import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Car } from 'lucide-react';

const Login = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    // No auth logic needed - anything works
    onLogin();
    navigate('/home');
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-8">
      <div className="w-full max-w-xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            DriveAssist
          </h1>
          <p className="text-base text-gray-600">
            Your Intelligent Driving Companion
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8">
          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-gray-700 block">
                Email
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-12 text-base px-4"
                placeholder="driver@example.com"
                required
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-gray-700 block">
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-12 text-base px-4"
                placeholder="Enter your password"
                required
              />
            </div>

            <div className="space-y-3 pt-2">
              <Button
                type="submit"
                className="w-full h-12 text-base font-semibold"
              >
                Sign In
              </Button>

              <div className="grid grid-cols-2 gap-3">
                <Button
                  type="button"
                  variant="outline"
                  className="h-11 text-sm"
                  onClick={handleLogin}
                >
                  Face ID
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  className="h-11 text-sm"
                  onClick={handleLogin}
                >
                  Touch ID
                </Button>
              </div>
            </div>
          </form>
        </div>

        <p className="text-center text-gray-500 mt-6 text-sm">
          Designed for safe in-car authentication
        </p>
      </div>
    </div>
  );
};

export default Login;
