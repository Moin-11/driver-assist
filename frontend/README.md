# DriveAssist - Intelligent Driving Assistance for Novice Drivers

An intelligent and adaptive driving assistance system designed specifically for novice drivers. This React application features real-time monitoring modules with in-car UX optimizations.

## Features

### 1. Login Page
- Large, touch-friendly inputs optimized for in-car use
- Email and password authentication (no backend validation - any credentials work)
- Biometric auth buttons (Face ID, Touch ID) for quick access
- Clean, professional design with DriveAssist branding

### 2. Home Page
- Three main monitoring module cards:
  - **Brake Checking** - Monitor braking patterns and detect hard braking events
  - **Road Signal Monitoring** - Real-time detection and alerts for traffic signals
  - **Lane Change Detection** - Track lane changes and detect unsafe maneuvers
- Quick access to Feedback History
- Logout functionality

### 3. Module Pages (Live Feed Simulations)

#### Brake Checking Module
- Real-time speed monitoring
- Simulated brake event detection (light, moderate, hard)
- Live feed of braking events with timestamps
- Safety warnings and recommendations
- Save events to feedback history

#### Road Signal Monitoring Module
- AI-powered traffic signal detection simulation
- Detects: Stop signs, Yield signs, Traffic lights, Speed limits, School zones
- Current detection display with visual feedback
- Distance measurements and recommended actions
- Event logging with timestamps

#### Lane Change Detection Module
- Live lane visualization (Left, Center, Right)
- Turn signal usage tracking
- Safety score calculation
- Real-time warnings for unsafe maneuvers
- Severity classification (low, medium, high)

### 4. Feedback History Page
- Comprehensive view of all driving events
- Grouped by module for easy navigation
- Statistics dashboard (total events, by module)
- Individual event deletion
- Clear all history option
- Detailed event information with timestamps

## Technology Stack

- **React** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **shadcn/ui** - Component library
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **date-fns** - Date formatting

## State Management

- **React Context API** - Global feedback state management
- **localStorage** - Persistent storage for feedback history

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

## Project Structure

```
src/
├── components/
│   └── ui/           # shadcn/ui components (Button, Card, Input)
├── context/
│   └── FeedbackContext.jsx  # Global state management
├── lib/
│   └── utils.js      # Utility functions
├── pages/
│   ├── Login.jsx
│   ├── Home.jsx
│   ├── BrakeChecking.jsx
│   ├── RoadSignalMonitoring.jsx
│   ├── LaneChangeDetection.jsx
│   └── FeedbackHistory.jsx
├── App.jsx           # Main app with routing
└── main.jsx          # Entry point
```

## In-Car UX Optimizations

- Large, touch-friendly buttons and inputs (minimum height: 56px)
- High contrast colors for visibility
- Clear, readable fonts (minimum 16px)
- Simple navigation patterns
- Minimal distractions while monitoring
- Quick access to critical features

## Future Enhancements

- Backend integration for user authentication
- Real camera feed integration
- Machine learning model integration for actual detection
- Voice command support
- Emergency contact management
- Driver performance analytics
- Export feedback reports

## License

MIT
