# MindSpeak 🎙️🧠

**Voice-powered AI journaling for mental wellness**

MindSpeak transforms your spoken thoughts into structured journal entries with AI-powered insights. Simply speak naturally, and our advanced AI transcribes, organizes, analyzes your mood, and provides personalized reflections.

---

## ✨ Features

### Core Functionality
- 🎤 **Voice Recording** - Capture thoughts naturally through speech
- 🤖 **AI Transcription** - OpenAI Whisper converts speech to text with high accuracy
- ✍️ **Smart Formatting** - Claude AI restructures rambling thoughts into coherent entries
- 😊 **Mood Analysis** - Automatic mood scoring (1-10 scale)
- 💭 **Emotion Detection** - AI identifies emotions with confidence scores
- 💡 **Personalized Insights** - Actionable reflections based on your entries
- 📊 **Progress Tracking** - Streak counting, monthly stats, mood trends

### User Experience
- 🔐 **Secure Authentication** - JWT-based auth with bcrypt password hashing
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🗂️ **Entry Management** - Browse, edit, delete, restore from trash
- ⚙️ **Customizable AI** - Set custom instructions and personal goals
- 🎯 **Goal Tracking** - Define goals and see AI reference them in insights
- 🏆 **Journaling Streaks** - Gamified daily journaling motivation

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Flask 3.x (Python)
- **Database:** SQLAlchemy ORM with SQLite (dev) / PostgreSQL (production)
- **Authentication:** Flask-JWT-Extended (JWT tokens)
- **AI Services:**
  - OpenAI Whisper API (speech-to-text)
  - Anthropic Claude 3.5 Sonnet (content processing & insights)
- **Migrations:** Alembic via Flask-Migrate
- **Validation:** Marshmallow schemas

### Frontend
- **Framework:** React 19 with TypeScript
- **Routing:** React Router v7
- **HTTP Client:** Axios with interceptors
- **Styling:** TailwindCSS
- **Icons:** Lucide React
- **Audio:** Web Audio API

---

## 📋 Prerequisites

Before you begin, ensure you have:
- **Python 3.8+** installed
- **Node.js 16+** and npm installed
- **OpenAI API key** ([Get one here](https://platform.openai.com/api-keys))
- **Anthropic API key** ([Get one here](https://console.anthropic.com/))

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/MarshallXie16/MindSpeak.git
cd MindSpeak
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this
DATABASE_URL=sqlite:///mindspeak.db
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=10485760
JWT_ACCESS_TOKEN_EXPIRES=86400
EOF

# Initialize database
flask db upgrade

# Start backend server
python app.py
```

The backend will run on **http://localhost:5000**

### 3. Frontend Setup

```bash
# Open new terminal and navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file (optional - defaults to localhost:5000)
echo "REACT_APP_API_URL=http://localhost:5000/api" > .env

# Start frontend development server
npm start
```

The frontend will run on **http://localhost:3000**

---

## 🎯 Usage Guide

### Creating Your First Journal Entry

1. **Register** - Create an account at http://localhost:3000/register
2. **Login** - Sign in with your credentials
3. **Click "Record"** - Start recording your thoughts
4. **Speak naturally** - Don't worry about pauses or "um"s - AI cleans it up
5. **Stop recording** - Click stop when finished (max 2 minutes)
6. **Wait for processing** - AI transcribes and analyzes (10-30 seconds)
7. **View your entry** - See formatted content, mood, emotions, and insights!

### Managing Entries
- **Browse All Entries** - Click "Entries" in navigation
- **Edit Entry** - Click on any entry to edit content
- **Delete Entry** - Entries go to trash (soft delete)
- **View Trash** - Restore or permanently delete

### Personalizing AI
- Go to **Profile → Preferences**
- Set **Custom AI Instructions** (e.g., "Write in a poetic style")
- Add **Personal Goals** (e.g., "I want to be more grateful")
- AI will reference these in future entries!

---

## 🗂️ Project Structure

```
MindSpeak/
├── backend/                 # Flask backend
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   └── services/        # AI services
│   ├── migrations/          # Database migrations
│   ├── config/              # Configuration
│   └── app.py               # Entry point
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── contexts/        # React contexts
│   │   ├── services/        # API client
│   │   └── utils/           # Utilities
│   └── public/              # Static assets
├── CLAUDE.md                # AI agent instructions
├── memory.md                # Project knowledge base
├── tasks.md                 # Development roadmap
└── README.md                # This file
```

---

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Login and get JWT
- `GET /api/auth/me` - Get current user info

### Journal Entries
- `POST /api/entries/upload-audio` - Upload audio file
- `POST /api/entries/:id/process` - Process entry with AI
- `GET /api/entries` - Get all entries (paginated)
- `GET /api/entries/:id` - Get single entry
- `PUT /api/entries/:id` - Update entry
- `DELETE /api/entries/:id` - Soft delete entry
- `GET /api/entries/stats` - Dashboard statistics
- `GET /api/entries/trash` - Get deleted entries

### User Settings
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update profile
- `GET /api/user/preferences` - Get preferences
- `PUT /api/user/preferences` - Update preferences
- `POST /api/user/preferences/goals` - Add goal
- `DELETE /api/user/preferences/goals/:id` - Remove goal

Full API documentation: See `memory.md` for detailed schemas.

---

## 🔐 Environment Variables

### Backend (.env)
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FLASK_ENV` | Environment (development/production) | No | development |
| `SECRET_KEY` | Flask secret key | Yes | - |
| `JWT_SECRET_KEY` | JWT signing key | Yes | - |
| `DATABASE_URL` | Database connection string | No | sqlite:///mindspeak.db |
| `OPENAI_API_KEY` | OpenAI API key for Whisper | Yes | - |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | Yes | - |
| `UPLOAD_FOLDER` | Audio file upload directory | No | uploads |
| `MAX_CONTENT_LENGTH` | Max upload size in bytes | No | 10485760 (10MB) |
| `JWT_ACCESS_TOKEN_EXPIRES` | Token expiration in seconds | No | 86400 (24hrs) |

### Frontend (.env)
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `REACT_APP_API_URL` | Backend API base URL | No | http://localhost:5000/api |

---

## 🧪 Testing

### Backend Tests (TODO)
```bash
cd backend
pytest
```

### Frontend Tests (TODO)
```bash
cd frontend
npm test
```

---

## 📦 Deployment

### Backend (Example: Railway/Heroku)
1. Set environment variables in hosting dashboard
2. Change `DATABASE_URL` to PostgreSQL connection string
3. Run `flask db upgrade` on first deploy
4. Ensure `gunicorn` is used in production (included in requirements.txt)

### Frontend (Example: Vercel/Netlify)
1. Build command: `npm run build`
2. Publish directory: `build`
3. Set `REACT_APP_API_URL` to your backend URL

---

## 🐛 Troubleshooting

### Backend won't start
- **Check Python version:** `python --version` (must be 3.8+)
- **Check virtual environment:** Ensure `venv` is activated
- **Check dependencies:** Run `pip install -r requirements.txt` again
- **Check database:** Delete `mindspeak.db` and run `flask db upgrade`

### Frontend won't start
- **Check Node version:** `node --version` (must be 16+)
- **Clear cache:** Delete `node_modules` and run `npm install` again
- **Check port:** Ensure port 3000 is not already in use

### CORS errors
- Ensure backend is running on `localhost:5000`
- Ensure frontend is running on `localhost:3000` or `localhost:3001`
- Backend CORS is configured for these origins only

### AI processing fails
- **Check API keys:** Ensure `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` are valid
- **Check audio file:** Must be < 10MB and supported format (webm, mp3, wav, m4a, ogg)
- **Check logs:** Backend logs will show detailed error messages

### Audio recording doesn't work
- **Check browser permissions:** Grant microphone access when prompted
- **Check HTTPS:** Some browsers require HTTPS for microphone (works on localhost)
- **Check browser:** Use Chrome, Firefox, Safari (not IE)

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `npm test` and `pytest`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Coding Standards
- **Backend:** Follow PEP 8, add docstrings, type hints
- **Frontend:** Use TypeScript, functional components, meaningful names
- **Commits:** Descriptive commit messages

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI Whisper** - Industry-leading speech recognition
- **Anthropic Claude** - Advanced language model for insights
- **Flask** - Lightweight Python web framework
- **React** - UI library
- **TailwindCSS** - Utility-first CSS framework

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/MarshallXie16/MindSpeak/issues)
- **Email:** support@mindspeak.example.com (placeholder)

---

## 🗺️ Roadmap

### Completed ✅
- Voice recording and upload
- AI transcription (Whisper)
- AI processing (Claude)
- User authentication
- Entry management
- Mood tracking
- Streak counting
- Usage limits (free tier)

### In Progress 🚧
- Testing & bug fixes
- Documentation completion
- Environment setup automation

### Planned 📋
- Text-based journaling
- Mood charts & analytics
- Search & filtering
- Email verification
- Export to PDF
- Therapist sharing
- Mobile app

---

**Made with ❤️ for better mental health**

