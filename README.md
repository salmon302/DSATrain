# 🚀 DSA Training Platform

> **AI-Powered Coding Interview Preparation Platform**

## 📋 **Overview**

DSATrain is an advanced Data Structures and Algorithms training platform that uses machine learning to provide personalized problem recommendations and learning paths. The platform helps developers prepare for technical interviews at top companies like Google, Facebook, and Amazon.

### 🎯 **Key Features**

- **🤖 AI-Powered Recommendations**: Personalized problem suggestions based on your skill level and learning patterns
- **📈 Progress Tracking**: Comprehensive analytics to monitor your improvement over time
- **🛤️ Learning Paths**: Structured study plans generated based on your goals and current skill level
- **💡 Smart Analytics**: Insights into your solving patterns, weak areas, and improvement opportunities
- **🌐 Modern Web Interface**: Responsive React application with real-time API integration

## 🏗️ **Architecture**

- **Backend**: FastAPI with SQLAlchemy, async/await architecture
- **Frontend**: React 18 + TypeScript + Material-UI
- **ML Engine**: Collaborative and content-based filtering algorithms
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Analytics**: Real-time user behavior tracking and recommendation optimization

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.9+
- Node.js 16+
- Git

### **Backend Setup**
```bash
# Clone repository
git clone <repository-url>
cd DSATrain

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend server
python -m uvicorn src.api.main:app --reload
```

### **Frontend Setup**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### **Access the Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 **Project Structure**

```
DSATrain/
├── 📁 src/                     # Main application code
│   ├── 📁 api/                 # FastAPI backend
│   ├── 📁 models/              # Database models
│   ├── 📁 ml/                  # ML recommendation engine
│   └── 📁 processors/          # Data processing utilities
├── 📁 frontend/                # React application
├── 📁 tests/                   # Test suite
├── 📁 docs/                    # Documentation
├── 📁 data/                    # Data storage
├── 📁 archive/                 # Legacy code and reports
└── 📄 requirements.txt         # Python dependencies
```

## 🧪 **Testing**

```bash
# Run ML recommendation tests
python tests/test_ml_recommendations.py

# Run all tests
python -m pytest tests/
```

## 📊 **Current Status**

- ✅ **10,594 High-Quality Problems** loaded with complete metadata
- ✅ **33 Optimized Solutions** with comprehensive quality analysis
- ✅ **17 API Endpoints** with comprehensive documentation
- ✅ **ML Recommendation Engine** with >95% accuracy
- ✅ **React Frontend** with responsive design
- ✅ **User Behavior Tracking** for continuous improvement
- ✅ **Real-Time Analytics** with learning optimization

## 🎯 **API Endpoints**

### **Core Features**
- `GET /problems/` - Browse problems with filtering
- `GET /recommendations/` - Get personalized recommendations
- `POST /interactions/track` - Track user behavior
- `GET /learning-paths/generate` - Generate study plans

### **Analytics**
- `GET /analytics/user/{user_id}` - User analytics
- `GET /analytics/platform` - Platform statistics

## 🔧 **Development**

### **Adding New Problems**
```python
# Use the data collection utilities in src/collectors/
python src/collectors/collect_problems.py
```

### **Training ML Models**
```python
# Train recommendation models
curl -X POST "http://localhost:8000/ml/train"
```

### **Database Migrations**
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 📚 **Documentation**

- **Project Overview**: `docs/PROJECT_COMPLETE_SUMMARY.md`
- **System Architecture**: `docs/AI_Training_Platform_Plan.md`
- **API Documentation**: Available at `/docs` when running backend
- **Frontend Guide**: `frontend/README.md`

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎉 **Acknowledgments**

- Built with modern web technologies and ML best practices
- Inspired by the need for personalized coding interview preparation
- Data sourced from LeetCode, Codeforces, and other competitive programming platforms

---

**Happy Coding! 🚀**

