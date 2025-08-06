# DSA Training Platform Frontend

## Phase 4 Week 2 - React Frontend with ML Integration

This is the React frontend for the DSA Training Platform, featuring ML-powered recommendations and comprehensive user analytics.

## Features

### 🤖 ML-Powered Recommendations
- Personalized problem recommendations using collaborative filtering
- Content-based similarity matching
- User behavior tracking and learning pattern analysis
- Dynamic difficulty progression suggestions

### 📊 Interactive Dashboard
- Real-time platform statistics
- Personalized recommendation display
- Quick access to key features
- User progress tracking

### 🔍 Problem Browser
- Advanced filtering by difficulty, platform, and algorithm tags
- Full-text search functionality
- Quality score and Google interview relevance display
- Similar problem suggestions

### 🛤️ Learning Paths
- AI-generated personalized learning sequences
- Goal-based curriculum (Google interviews, competitive programming)
- Weekly milestone tracking
- Estimated completion times

### 📈 Analytics Dashboard
- User interaction analytics
- Learning pattern visualization
- Performance metrics and trends
- Recommendation effectiveness tracking

## Technology Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** for modern, responsive design
- **React Router** for navigation
- **Axios** for API communication
- **Recharts** for data visualization

## Setup Instructions

### Prerequisites
- Node.js 16+ and npm
- Backend API server running on http://localhost:8000

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open your browser to http://localhost:3000

### Environment Configuration

Create a `.env` file in the frontend directory:
```
REACT_APP_API_URL=http://localhost:8000
```

## API Integration

The frontend connects to the FastAPI backend through the `apiService` which provides:

- **Problem Management**: Browse, search, and filter problems
- **ML Recommendations**: Get personalized suggestions
- **User Tracking**: Record interactions for ML training
- **Analytics**: Access user behavior and platform trends
- **Learning Paths**: Generate and manage study plans

## Component Structure

```
src/
├── components/          # Reusable UI components
├── pages/              # Main page components
│   ├── Dashboard.tsx
│   ├── ProblemBrowser.tsx
│   ├── Recommendations.tsx
│   ├── LearningPaths.tsx
│   ├── Analytics.tsx
│   └── UserProfile.tsx
├── services/           # API service layer
│   └── api.ts
├── App.tsx            # Main application component
└── index.tsx          # Application entry point
```

## Key Features Implementation

### ML Recommendation Display
- Real-time personalized recommendations
- Explanation of recommendation reasoning
- Difficulty and quality score visualization
- Interactive recommendation actions

### User Behavior Tracking
- Automatic interaction logging
- Session-based analytics
- Learning pattern recognition
- Progress visualization

### Responsive Design
- Mobile-first approach
- Adaptive navigation
- Touch-friendly interfaces
- Cross-browser compatibility

## Development Status

### ✅ Completed
- Project structure and configuration
- API service layer with complete type definitions
- Main navigation and layout
- Dashboard with ML recommendation display
- Page components foundation
- Material-UI theme and styling

### 🚧 In Progress
- Complete implementation of all page components
- Data visualization charts
- Interactive problem browser with filters
- User authentication system

### 📋 Planned
- Advanced analytics charts
- Real-time recommendation updates
- Offline mode support
- PWA capabilities

## Building for Production

```bash
npm run build
```

The build artifacts will be stored in the `build/` directory, ready for deployment.

## Testing

```bash
npm test
```

## Contributing

1. Follow TypeScript best practices
2. Use Material-UI components consistently
3. Implement proper error handling
4. Add loading states for API calls
5. Ensure responsive design principles

## Integration with Backend

The frontend automatically adapts to backend availability:
- Shows connection status in the header
- Graceful degradation when API is offline
- Error messages with actionable guidance
- Automatic retry mechanisms

This frontend provides a modern, intuitive interface for the ML-powered DSA training platform, making advanced recommendation algorithms accessible through a user-friendly web interface.
