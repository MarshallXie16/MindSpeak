# MindSpeak - Project Memory

**Last Updated:** 2025-11-16
**Project Status:** MVP Development - Backend & Frontend ~80% complete
**Current Focus:** Environment setup, testing, and completing remaining MVP features

---

## Project Overview

MindSpeak is a voice-based AI journaling application that transforms spoken thoughts into structured journal entries with AI-powered insights. Users speak naturally, and the app transcribes, formats, analyzes mood, detects emotions, and provides personalized insights.

### Core Value Proposition
- **Voice-first journaling** → Natural, frictionless way to journal
- **AI enhancement** → Transforms rambling speech into coherent entries
- **Mental health insights** → Mood tracking, emotion analysis, personalized feedback
- **Privacy-focused** → Personal journal with optional therapist sharing

---

## Technical Architecture

### Tech Stack

**Backend (Python/Flask):**
- Flask 3.x with application factory pattern
- SQLAlchemy ORM with Flask-SQLAlchemy extension
- Flask-JWT-Extended for authentication (JWT tokens)
- Flask-CORS for cross-origin requests
- Flask-Migrate (Alembic) for database migrations
- OpenAI Whisper API for speech-to-text
- Anthropic Claude 3.5 Sonnet for journal processing
- SQLite (development) / PostgreSQL (production-ready)

**Frontend (React/TypeScript):**
- React 19 with TypeScript (strict mode)
- React Router v7 for client-side routing
- Axios for HTTP requests with interceptors
- TailwindCSS for styling
- Lucide React for icons
- Web Audio API for recording
- class-variance-authority for component variants

### Architecture Patterns

**Backend:**
- **Application Factory Pattern** (`app/__init__.py`) - Allows multiple app instances for testing
- **Blueprint Pattern** - Modular routes (auth, entries, user)
- **Service Layer Pattern** - AI services abstracted into dedicated classes
- **Facade Pattern** - JournalAIService orchestrates complex AI pipeline
- **Singleton Pattern** - Global AI service instance (`get_ai_service()`)

**Frontend:**
- **Context API** - AuthContext for global authentication state
- **Custom Hooks** - Reusable logic extraction
- **Protected Routes** - HOC pattern for authentication guards
- **Component Library** - Reusable UI components with variants

---

## Database Schema

### Users Table
```sql
- id (PK)
- email (unique, not null)
- username (unique, nullable)
- password_hash (bcrypt)
- created_at, updated_at, last_login_at
- subscription_tier (free, premium, pro)
- subscription_expires_at
- is_active, is_verified
- verification_token, verification_sent_at
- Profile: first_name, last_name, display_name, avatar_url, bio, timezone, locale
- Privacy: is_public, share_token (for therapist)
- Security: two_factor_enabled, two_factor_secret, failed_login_attempts, locked_until
- Notifications: email_notifications, push_notifications
- beta_features flag
```

### Journal_Entries Table
```sql
- id (PK)
- user_id (FK → users.id)
- title
- raw_transcript (from Whisper)
- formatted_content (from Claude)
- mood_score (1-10 integer)
- emotions (JSON array: [{name, confidence}])
- insights (JSON array of strings)
- audio_filename
- processing_status (pending, processing, completed, error)
- created_at, updated_at, entry_date
- is_deleted (soft delete), deleted_at
```

### User_Preferences Table
```sql
- user_id (PK, FK → users.id)
- custom_ai_instructions (text)
- goals (JSON: [{id, text, created_at}])
- reminder_enabled, reminder_time, reminder_days (JSON)
- theme (light, dark, auto)
- current_streak, longest_streak, last_entry_date
```

### Usage_Tracking Table
```sql
- id (PK)
- user_id (FK → users.id)
- entry_count (monthly count)
- month_year (YYYY-MM)
- last_entry_at
- Unique constraint: (user_id, month_year)
```

---

## API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - Create new user + default preferences
- `POST /login` - Authenticate user, return JWT
- `GET /me` - Get current user info (requires JWT)
- `POST /logout` - Logout (placeholder for JWT blacklist)

### Journal Entries (`/api/entries`)
- `POST /upload-audio` - Upload audio file, create pending entry, check tier limits
- `POST /:id/process` - Trigger AI processing (Whisper + Claude)
- `GET /` - Get paginated entries list (query: page, limit)
- `GET /:id` - Get single entry with full content
- `PUT /:id` - Update entry fields
- `DELETE /:id` - Soft delete entry
- `GET /stats` - Dashboard statistics (total, streak, month, mood avg)
- `GET /trash` - Get soft-deleted entries
- `DELETE /hard-delete-all` - Permanently delete soft-deleted entries
- `POST /fix-streaks` - Recalculate streaks (utility endpoint)

### User Management (`/api/user`)
- `GET /profile` - Get user profile
- `PUT /profile` - Update profile (display_name, timezone, locale)
- `GET /preferences` - Get user preferences
- `PUT /preferences` - Update preferences (AI instructions, reminders, theme)
- `POST /preferences/goals` - Add new goal
- `DELETE /preferences/goals/:id` - Remove goal

---

## AI Processing Pipeline

The AI pipeline is orchestrated by `JournalAIService` and runs asynchronously with progress updates:

### Processing Flow
```
1. Audio Upload → Save to disk, create JournalEntry (status=pending)
2. Frontend calls /process → Backend starts async processing
3. Progress Updates:
   - transcribing (10-25%) → Whisper API
   - restructuring (25-50%) → Claude API (content formatting)
   - analyzing (50-75%) → Claude (mood, emotions, insights)
   - complete (100%) → Update entry in database
```

### Whisper Transcription
- **Service:** `WhisperTranscriber` (backend/app/services/whisper_transcriber.py)
- **Model:** whisper-1
- **File limit:** 25MB
- **Supported formats:** flac, m4a, mp3, mp4, mpeg, mpga, oga, ogg, wav, webm
- **Output:** TranscriptionResult with text, confidence, language, duration
- **Error handling:** File not found, file too large, no speech detected, invalid format

### Claude Processing
- **Service:** `ClaudeProcessor` (backend/app/services/claude_processor.py)
- **Model:** claude-3-5-sonnet-20241022
- **Max tokens:** 4000
- **Input:** Raw transcript + user context (custom instructions, goals)
- **Prompt engineering:** Preserves user voice, organizes thoughts, maintains authenticity
- **Output:** JournalAnalysis with title, formatted_content, mood_score, emotions[], insights[]
- **Robust parsing:** Multiple fallback strategies for JSON parsing (handles Chinese, control chars, newlines)

### User Context Integration
The AI processing uses user preferences to personalize responses:
- **custom_ai_instructions** - User's writing style preferences
- **goals** - Personal goals to reference in insights

---

## Key Business Logic

### Subscription Tiers & Limits
```python
FREE:
- 5 entries per month
- Basic features

PREMIUM/PRO:
- Unlimited entries
- Future: Advanced analytics, export, therapist sharing
```

Limits enforced in `UsageTracking.can_create_entry()` before audio upload.

### Streak Tracking
- Tracks consecutive daily journaling
- **current_streak** - Increments if entry on consecutive day
- **longest_streak** - All-time best streak
- **last_entry_date** - YYYY-MM-DD format for easy comparison
- Logic in `UserPreferences.update_streak()`

### Soft Delete Pattern
- Journal entries use `is_deleted` flag instead of hard delete
- User can restore from trash
- `/hard-delete-all` permanently removes soft-deleted entries + audio files

---

## Frontend Architecture

### Routing Structure
```
/ → Redirect to /dashboard
/login → Public
/register → Public
/dashboard → Protected (shows stats, recent entries, record button)
/record → Protected (audio recording interface)
/entries → Protected (paginated list of all entries)
/entries/:id/edit → Protected (edit entry content)
/entries/:id/process → Protected (AI processing status page)
/profile → Protected (user profile + preferences)
```

### Authentication Flow
1. User logs in → JWT token stored in `localStorage.auth_token`
2. `AuthContext` provides `user` object and `login/logout` functions
3. `api.ts` interceptor adds `Authorization: Bearer {token}` to all requests
4. 401 response → Clear token, redirect to /login
5. `ProtectedRoute` component checks auth before rendering

### State Management
- **Global:** AuthContext for user/token
- **Local:** useState/useEffect for component state
- **API calls:** Direct axios calls in components (no Redux, keeping it simple)

---

## File Structure Reference

### Backend Critical Files
```
backend/
├── app.py                      # Entry point, creates app
├── config/config.py            # Environment-based config
├── app/__init__.py             # Application factory
├── app/models/
│   ├── user.py                 # User model + db instance
│   ├── entry.py                # JournalEntry model
│   ├── user_preferences.py     # UserPreferences model
│   └── usage_tracking.py       # UsageTracking model
├── app/routes/
│   ├── auth.py                 # Auth endpoints
│   ├── entries.py              # Entry CRUD + AI processing
│   └── user.py                 # Profile + preferences
├── app/services/
│   ├── base.py                 # Abstract base classes
│   ├── whisper_transcriber.py  # OpenAI Whisper integration
│   ├── claude_processor.py     # Anthropic Claude integration
│   └── journal_ai_service.py   # Orchestration service
└── migrations/                 # Alembic migrations
```

### Frontend Critical Files
```
frontend/
├── src/
│   ├── App.tsx                 # Router + Routes
│   ├── index.tsx               # React entry point
│   ├── contexts/
│   │   └── AuthContext.tsx     # Auth state management
│   ├── services/
│   │   └── api.ts              # Axios client + API functions
│   ├── utils/
│   │   └── audioRecorder.ts    # Web Audio recording
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx       # Main landing page
│   │   ├── Recording.tsx       # Audio recording UI
│   │   ├── ProcessingEntry.tsx # AI processing status
│   │   ├── EntryEditor.tsx     # Edit journal entries
│   │   ├── EntriesList.tsx     # Browse all entries
│   │   └── Profile.tsx         # User settings
│   └── components/
│       ├── Layout.tsx          # App shell with navigation
│       ├── ProtectedRoute.tsx  # Auth guard
│       ├── EntryCard.tsx       # Entry display component
│       ├── NewEntryModal.tsx   # Entry creation modal
│       ├── AudioVisualizer.tsx # Recording visualization
│       └── ui/                 # Reusable UI components
```

---

## Environment Variables

### Backend (.env)
```bash
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///mindspeak.db  # or postgres://...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=10485760  # 10MB
JWT_ACCESS_TOKEN_EXPIRES=86400  # 24 hours
```

### Frontend (.env)
```bash
REACT_APP_API_URL=http://localhost:5000/api
```

---

## Development Workflow

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
python app.py  # Runs on localhost:5000
```

### Frontend Setup
```bash
cd frontend
npm install
npm start  # Runs on localhost:3000
```

### Testing Backend Locally
```bash
# Test registration
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Test login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Test protected endpoint
curl http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Known Patterns & Conventions

### Python Code Style
- Snake_case for functions, variables
- PascalCase for classes
- Docstrings for all public methods
- Type hints where beneficial
- Line length: ~120 characters

### TypeScript Code Style
- camelCase for functions, variables
- PascalCase for components, interfaces, types
- Explicit return types for functions
- Interface over type for object shapes
- Functional components with hooks

### API Response Format
```typescript
// Success
{
  "user": {...},
  "token": "...",
  // or
  "message": "Success",
  "data": {...}
}

// Error
{
  "error": "Human-readable error message"
}
```

---

## Critical Dependencies

### Backend
- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM integration
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - CORS handling
- **Flask-Migrate** - Database migrations
- **bcrypt** - Password hashing
- **openai** - Whisper API client
- **anthropic** - Claude API client
- **marshmallow** - Request validation

### Frontend
- **react** - UI library
- **react-router-dom** - Routing
- **axios** - HTTP client
- **tailwindcss** - Styling
- **lucide-react** - Icons
- **class-variance-authority** - Component variants
- **tailwind-merge** - Tailwind class merging
- **clsx** - Conditional classes

---

## Security Considerations

### Implemented
✅ Password hashing with bcrypt
✅ JWT token authentication
✅ CORS configuration (localhost:3000 only)
✅ Input validation with marshmallow
✅ SQL injection protection (SQLAlchemy ORM)
✅ File upload validation (type, size)
✅ Soft delete for user data

### TODO
- Rate limiting (Flask-Limiter)
- HTTPS enforcement in production
- JWT refresh tokens
- JWT blacklist for logout
- Email verification
- 2FA implementation
- Content Security Policy headers
- Account lockout after failed logins (partially implemented)

---

## Performance Optimizations

### Current
- Database indexes on foreign keys
- Pagination for entry lists
- Async/await for AI processing
- JSON responses (no heavy templating)

### Future
- Redis caching for user sessions
- CDN for static assets
- Database connection pooling
- Background job queue (Celery) for AI processing
- Audio file compression before storage

---

## Testing Strategy

### Backend (TODO)
- pytest for unit tests
- pytest-flask for integration tests
- Test coverage target: 80%+
- Mock OpenAI and Anthropic API calls

### Frontend (TODO)
- Jest + React Testing Library
- Component tests for UI
- Integration tests for user flows
- E2E tests with Cypress/Playwright

---

## Common Issues & Solutions

### Issue: CORS errors in development
**Solution:** Backend CORS is configured for localhost:3000 and localhost:3001. Ensure frontend runs on these ports.

### Issue: JWT token expires
**Solution:** Token expires in 24 hours (configurable). Frontend auto-redirects to login on 401.

### Issue: Audio file upload fails
**Solution:** Check file size (max 10MB by default), format (webm, mp3, wav, etc.), and UPLOAD_FOLDER exists.

### Issue: AI processing fails
**Solution:** Check OPENAI_API_KEY and ANTHROPIC_API_KEY in .env. Review logs for specific API errors.

### Issue: Database migrations fail
**Solution:** Delete existing database (dev only) and run `flask db upgrade` again.

---

## Future Enhancements

### MVP+
- Text-based journaling (skip Whisper)
- Calendar view of entries
- Search and filtering
- Export entries (PDF, JSON)
- Mood charts over time
- Emotion trends visualization

### v2.0
- Therapist sharing with unique link
- Voice cloning for playback
- Multi-language support
- Mobile apps (React Native)
- Advanced analytics dashboard
- Goal tracking with progress
- Guided journaling prompts

### Business
- Stripe integration for subscriptions
- Admin dashboard
- Email verification system
- Password reset flow
- Referral system

---

## Lessons Learned

### What Works Well
- **Service layer abstraction** - Easy to swap AI providers
- **Soft delete** - Users appreciate trash/restore
- **Progress updates** - User sees AI processing in real-time
- **Robust JSON parsing** - Claude responses can be messy; multiple fallbacks help

### What to Improve
- **Async processing** - Should use Celery for production (not sync event loop hack)
- **Error handling** - More granular error codes for frontend
- **Validation** - More comprehensive input validation
- **Documentation** - API documentation (Swagger/OpenAPI)

---

## Quick Reference Commands

### Backend
```bash
# Create migration
flask db migrate -m "description"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade

# Run development server
python app.py

# Install dependencies
pip install -r requirements.txt
```

### Frontend
```bash
# Install dependencies
npm install

# Run dev server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Git
```bash
# Current branch
git status

# Create feature branch
git checkout -b feature/new-feature

# Commit changes
git add .
git commit -m "Description"

# Push changes
git push -u origin branch-name
```

---

**This document should be updated regularly as the project evolves.**
