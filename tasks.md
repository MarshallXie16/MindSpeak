# MindSpeak - Tasks & Roadmap

**Last Updated:** 2025-11-16
**Sprint:** Environment Setup & MVP Completion
**Target MVP Date:** Week of Nov 23, 2025

---

## Current Sprint: Environment Setup & Testing

### ✅ Completed
- [x] Project architecture review
- [x] Code audit (backend & frontend)
- [x] Documentation structure created (CLAUDE.md, memory.md, tasks.md)

### 🚧 In Progress
- [ ] Environment setup (backend + frontend)
- [ ] Database initialization
- [ ] Dependency installation
- [ ] API key configuration

### 📋 Backlog (This Sprint)
- [ ] End-to-end testing (full user flow)
- [ ] Fix any discovered bugs
- [ ] Complete any incomplete features
- [ ] Create comprehensive README.md

---

## Phase 1: Environment Setup & Validation (TODAY)

### Task 1.1: Backend Environment Setup
**Priority:** CRITICAL
**Status:** NOT STARTED

**Steps:**
1. Create `.env` file in backend/ with required variables
2. Install Python dependencies (`pip install -r requirements.txt`)
3. Initialize database (`flask db upgrade`)
4. Create uploads directory
5. Verify configuration loads correctly

**Acceptance Criteria:**
- [ ] `.env` file exists with all required keys
- [ ] All dependencies installed without errors
- [ ] Database created successfully (mindspeak.db)
- [ ] Uploads directory exists
- [ ] Backend starts without errors: `python app.py`

**Dependencies:** None
**Estimated Time:** 30 minutes

---

### Task 1.2: Frontend Environment Setup
**Priority:** CRITICAL
**Status:** NOT STARTED

**Steps:**
1. Install Node dependencies (`npm install`)
2. Create `.env` file in frontend/ if needed
3. Verify build works
4. Test dev server starts

**Acceptance Criteria:**
- [ ] All npm dependencies installed
- [ ] No version conflicts
- [ ] Frontend starts without errors: `npm start`
- [ ] Can access http://localhost:3000

**Dependencies:** None
**Estimated Time:** 15 minutes

---

### Task 1.3: API Integration Testing
**Priority:** HIGH
**Status:** NOT STARTED

**Steps:**
1. Start backend server (port 5000)
2. Start frontend server (port 3000)
3. Test registration flow
4. Test login flow
5. Test dashboard load
6. Test audio upload (create mock API keys if needed)

**Acceptance Criteria:**
- [ ] Can register new user from frontend
- [ ] Can login with credentials
- [ ] Dashboard loads with stats
- [ ] No CORS errors
- [ ] JWT token flows correctly

**Dependencies:** Task 1.1, Task 1.2
**Estimated Time:** 30 minutes

---

## Phase 2: Feature Completion & Bug Fixes (NOV 17-18)

### Task 2.1: Audio Recording Flow
**Priority:** HIGH
**Status:** TO VALIDATE

**What to Test:**
- [ ] Record button on Dashboard works
- [ ] AudioVisualizer shows during recording
- [ ] Can stop recording and upload
- [ ] Audio file is saved to backend
- [ ] Entry created with pending status
- [ ] Redirects to processing page

**Known Issues:**
- None identified yet

**If Bugs Found:**
1. Document the bug in detail
2. Fix immediately
3. Test again
4. Update this task

**Dependencies:** Task 1.3
**Estimated Time:** 1-2 hours (if bugs found)

---

### Task 2.2: AI Processing Pipeline
**Priority:** CRITICAL
**Status:** TO VALIDATE

**What to Test:**
- [ ] Process button triggers AI pipeline
- [ ] Whisper API transcribes audio correctly
- [ ] Claude API formats content
- [ ] Mood score is reasonable (1-10)
- [ ] Emotions array populated
- [ ] Insights generated
- [ ] Entry status updates to 'completed'
- [ ] Can view completed entry

**Known Issues:**
- Requires valid OPENAI_API_KEY and ANTHROPIC_API_KEY
- Synchronous processing may timeout on large files

**Improvements Needed:**
- [ ] Add timeout handling (current: 2 minute max)
- [ ] Better error messages if API keys invalid
- [ ] Progress indicator on frontend during processing

**Dependencies:** Task 2.1
**Estimated Time:** 2-3 hours (testing + fixes)

---

### Task 2.3: Entry Management (CRUD)
**Priority:** MEDIUM
**Status:** TO VALIDATE

**What to Test:**
- [ ] EntriesList page loads all entries
- [ ] Pagination works (if > 20 entries)
- [ ] Can click entry to view details
- [ ] Can edit entry content
- [ ] Changes save successfully
- [ ] Can delete entry (soft delete)
- [ ] Deleted entries appear in trash
- [ ] Can view trash
- [ ] Can hard delete from trash

**Known Issues:**
- None identified yet

**Dependencies:** Task 2.2
**Estimated Time:** 1-2 hours

---

### Task 2.4: User Profile & Preferences
**Priority:** MEDIUM
**Status:** TO VALIDATE

**What to Test:**
- [ ] Profile page loads user info
- [ ] Can update display name
- [ ] Can update timezone
- [ ] Can add goals
- [ ] Can remove goals
- [ ] Can set custom AI instructions
- [ ] Preferences save correctly
- [ ] Theme setting works (if implemented)
- [ ] Reminder settings work (if implemented)

**Known Issues:**
- None identified yet

**Dependencies:** Task 1.3
**Estimated Time:** 1-2 hours

---

### Task 2.5: Streak Tracking
**Priority:** LOW
**Status:** TO VALIDATE

**What to Test:**
- [ ] Dashboard shows current streak
- [ ] Creating entry increments streak (consecutive days)
- [ ] Missing a day breaks streak
- [ ] Longest streak tracked correctly
- [ ] Can fix streaks with `/fix-streaks` endpoint

**Known Issues:**
- Streak logic uses entry.created_at, not entry.entry_date (might want to change)

**Dependencies:** Task 2.2
**Estimated Time:** 30 minutes

---

### Task 2.6: Usage Limits (Free Tier)
**Priority:** MEDIUM
**Status:** TO VALIDATE

**What to Test:**
- [ ] Free users limited to 5 entries/month
- [ ] Upload blocked after 5 entries
- [ ] Error message clear
- [ ] Dashboard shows remaining entries
- [ ] Premium users bypass limit

**Known Issues:**
- No upgrade flow implemented yet (future feature)

**Dependencies:** Task 2.1
**Estimated Time:** 30 minutes

---

## Phase 3: Polish & Documentation (NOV 19-20)

### Task 3.1: Error Handling Audit
**Priority:** HIGH
**Status:** NOT STARTED

**Review Points:**
- [ ] All API endpoints have try/catch
- [ ] User-friendly error messages
- [ ] Frontend shows errors to user
- [ ] Network errors handled gracefully
- [ ] Invalid inputs rejected with clear messages

**Improvements:**
- [ ] Standardize error response format
- [ ] Add error logging
- [ ] Toast notifications for errors
- [ ] Retry logic for network failures

**Dependencies:** All Phase 2 tasks
**Estimated Time:** 2-3 hours

---

### Task 3.2: Create Comprehensive README
**Priority:** HIGH
**Status:** NOT STARTED

**Sections to Include:**
- [ ] Project description
- [ ] Features list
- [ ] Tech stack
- [ ] Prerequisites (Node, Python, API keys)
- [ ] Installation instructions (backend + frontend)
- [ ] Environment variables documentation
- [ ] Usage guide (how to use the app)
- [ ] API endpoints documentation
- [ ] Troubleshooting section
- [ ] Contributing guidelines (future)
- [ ] License

**Dependencies:** All Phase 2 tasks
**Estimated Time:** 1-2 hours

---

### Task 3.3: Code Cleanup
**Priority:** MEDIUM
**Status:** NOT STARTED

**Checklist:**
- [ ] Remove console.log statements
- [ ] Remove commented-out code
- [ ] Remove TODO comments or convert to tasks
- [ ] Ensure consistent formatting
- [ ] Add missing docstrings
- [ ] Check for unused imports
- [ ] Verify all files have appropriate headers

**Dependencies:** None
**Estimated Time:** 1-2 hours

---

### Task 3.4: Testing Coverage
**Priority:** LOW (MVP), HIGH (Production)
**Status:** NOT STARTED

**Backend Tests to Write:**
- [ ] Auth: registration, login, JWT validation
- [ ] Entries: CRUD operations
- [ ] AI service: mock API responses
- [ ] Usage limits
- [ ] Streak calculation

**Frontend Tests to Write:**
- [ ] Component tests (Button, Modal, etc.)
- [ ] Auth flow integration test
- [ ] Dashboard rendering
- [ ] Entry creation flow

**Dependencies:** All features complete
**Estimated Time:** 8-10 hours (not critical for MVP)

---

## Phase 4: Optional MVP Enhancements (NOV 21-22)

### Task 4.1: Text-Based Journaling
**Priority:** LOW
**Status:** NOT STARTED

**Description:**
Allow users to create journal entries by typing instead of recording audio. Skip Whisper, go straight to Claude processing.

**Implementation:**
- [ ] Add "Write" button to Dashboard
- [ ] Create TextEntryModal component
- [ ] Add POST `/entries/text` endpoint
- [ ] Process text with Claude (skip Whisper)
- [ ] Test full flow

**Estimated Time:** 2-3 hours

---

### Task 4.2: Mood Chart Visualization
**Priority:** LOW
**Status:** NOT STARTED

**Description:**
Show mood trends over time on Dashboard with a simple line chart.

**Implementation:**
- [ ] Install chart library (recharts or chart.js)
- [ ] Add GET `/entries/mood-history` endpoint
- [ ] Create MoodChart component
- [ ] Display on Dashboard
- [ ] Test with sample data

**Estimated Time:** 3-4 hours

---

### Task 4.3: Search & Filtering
**Priority:** LOW
**Status:** NOT STARTED

**Description:**
Allow users to search entries by title/content and filter by date range or mood.

**Implementation:**
- [ ] Add search input to EntriesList
- [ ] Add date range picker
- [ ] Add mood filter dropdown
- [ ] Update GET `/entries` to accept filters
- [ ] Implement backend filtering logic
- [ ] Test various filter combinations

**Estimated Time:** 3-4 hours

---

### Task 4.4: Email Verification
**Priority:** LOW
**Status:** NOT STARTED

**Description:**
Verify user email addresses before allowing full access.

**Implementation:**
- [ ] Set up email service (SendGrid or AWS SES)
- [ ] Add verification email template
- [ ] Create verification endpoint
- [ ] Block features for unverified users
- [ ] Add resend verification link
- [ ] Test email delivery

**Estimated Time:** 4-5 hours

---

## Technical Debt

### High Priority
- [ ] **Move AI processing to background queue (Celery/Redis)** - Currently synchronous with hacky event loop
- [ ] **Add rate limiting** - Prevent API abuse
- [ ] **Implement JWT refresh tokens** - Better security
- [ ] **Add database indexes** - Improve query performance
- [ ] **Implement proper logging** - Use Python logging module consistently

### Medium Priority
- [ ] **Add API documentation (Swagger)** - Auto-generated docs
- [ ] **Standardize error codes** - Consistent error handling
- [ ] **Add input validation layer** - More comprehensive validation
- [ ] **Optimize database queries** - Use select_related/joinedload
- [ ] **Add caching layer (Redis)** - Cache user sessions, stats

### Low Priority
- [ ] **Add TypeScript strict mode fixes** - Currently some 'any' types
- [ ] **Improve mobile responsiveness** - Better mobile UX
- [ ] **Add loading skeletons** - Better perceived performance
- [ ] **Implement service workers** - Offline support
- [ ] **Add analytics tracking** - User behavior insights

---

## Bugs & Issues

### Known Bugs
*None reported yet - will populate after testing*

---

### Recently Fixed Bugs
*Will populate as bugs are fixed*

---

## Feature Requests

### User-Requested
*None yet - will track user feedback*

---

### Internal Ideas
- Export entries as PDF
- Share entries publicly with unique link
- Voice playback of entries
- Multi-language support
- Guided journaling prompts
- Integration with calendar apps
- Therapist collaboration features

---

## Dependencies & Blockers

### Current Blockers
*None*

### Upcoming Blockers
- **API keys required** - Need valid OpenAI and Anthropic API keys for testing
- **Email service** - Need SendGrid/SES for email verification (optional feature)
- **Production hosting** - Need deployment plan (Heroku, AWS, Railway, etc.)

---

## Success Metrics

### MVP Launch Criteria
- [ ] User can register and login
- [ ] User can record audio journal entry
- [ ] AI processes entry successfully
- [ ] User can view all entries
- [ ] User can edit and delete entries
- [ ] Dashboard shows accurate stats
- [ ] No critical bugs
- [ ] README complete

### Post-MVP Goals
- 10 beta testers using the app
- 50+ journal entries processed
- < 10 second average processing time
- Zero data loss incidents
- Positive user feedback

---

## Notes & Reminders

- **Keep it simple** - MVP doesn't need to be perfect
- **User feedback is king** - Get real users testing ASAP
- **Document as you go** - Update memory.md with new learnings
- **Test frequently** - Don't wait until the end
- **Security first** - Never commit API keys or secrets

---

**This file should be updated daily during active development.**
