import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { FeedbackProvider } from './context/FeedbackContext';
import { useState } from 'react';
import Login from './pages/Login';
import Home from './pages/Home';
import BrakeChecking from './pages/BrakeChecking';
import RoadSignalMonitoring from './pages/RoadSignalMonitoring';
import LaneChangeDetection from './pages/LaneChangeDetection';
import FeedbackHistory from './pages/FeedbackHistory';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <FeedbackProvider>
      <Router>
        <Routes>
          <Route
            path="/login"
            element={
              isAuthenticated ?
                <Navigate to="/home" /> :
                <Login onLogin={() => setIsAuthenticated(true)} />
            }
          />
          <Route
            path="/home"
            element={
              isAuthenticated ?
                <Home /> :
                <Navigate to="/login" />
            }
          />
          <Route
            path="/brake-checking"
            element={
              isAuthenticated ?
                <BrakeChecking /> :
                <Navigate to="/login" />
            }
          />
          <Route
            path="/road-signal-monitoring"
            element={
              isAuthenticated ?
                <RoadSignalMonitoring /> :
                <Navigate to="/login" />
            }
          />
          <Route
            path="/lane-change-detection"
            element={
              isAuthenticated ?
                <LaneChangeDetection /> :
                <Navigate to="/login" />
            }
          />
          <Route
            path="/feedback-history"
            element={
              isAuthenticated ?
                <FeedbackHistory /> :
                <Navigate to="/login" />
            }
          />
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    </FeedbackProvider>
  );
}

export default App;
